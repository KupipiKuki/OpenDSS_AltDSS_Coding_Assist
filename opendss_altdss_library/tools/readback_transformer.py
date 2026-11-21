#!/usr/bin/env python3
"""Print the pinned Transformer and XfmrCode readbacks and focused probes."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from math import sqrt

from altdss import altdss, enums
from dss import DSSException
from numpy.testing import assert_allclose

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/transformers/transformer_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/transformer/three_winding_code.dss"


def new_circuit():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.transformer_probe BasekV=12.47 Bus1=source")
    return ctx


def normalize(value):
    if isinstance(value, IntEnum):
        return int(value)
    if isinstance(value, complex):
        return [value.real, value.imag]
    if hasattr(value, "tolist"):
        return normalize(value.tolist())
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    return getattr(value, "Name", value)


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label):
    assert_allclose(actual, expected, rtol=1e-9, atol=1e-12, err_msg=label)


def query(ctx, cls, obj, prop):
    ctx.Commands(f"? {cls}.{obj.Name}.{prop}")
    return ctx.TextResult


def read_defaults():
    ctx = new_circuit()
    results = {}
    for record in json.loads(CATALOG.read_text(encoding="utf-8")):
        cls = record["element_class"]
        obj = getattr(ctx, cls).new("readback_default", begin_edit=False)
        results[cls] = {}
        for row in record["properties"]:
            key, keyword = row["name"], row.get("altdss_keyword")
            if keyword == "Like":
                results[cls][key] = {"status": "action", "note": "Creation keyword and method with no getter."}
                continue
            entry = {"status": "read back"}
            if key == "name":
                raw = obj.Name
            elif keyword:
                raw = getattr(obj, keyword)
            else:
                text_keyword = row["dss_text_keyword"]
                text = query(ctx, cls, obj, text_keyword)
                convert = {"integer": int, "real": float, "string": str}[row["data_type"]]
                raw = convert(text)
                entry = {"status": "DSS text readback", "dss_text_keyword": text_keyword, "text": text}
            value = normalize(raw)
            expected = row["default_value"]
            if expected is not None:
                if isinstance(expected, (float, int, list)) and not isinstance(expected, bool):
                    near(value, expected, f"{cls}.{key}")
                else:
                    equal(value, expected, f"{cls}.{key}")
            entry["value"] = value
            if isinstance(raw, IntEnum):
                entry["enum_member"] = raw.name
            if keyword == "Conns":
                entry["enum_members"] = [member.name for member in raw]
            results[cls][key] = entry
    results["Transformer"]["buses"]["note"] = "Generated from the object name."
    equal(results["Transformer"]["buses"]["value"], ["readback_default_1", "readback_default_2"], "Initial buses")
    equal(results["Transformer"]["bus"]["value"], "readback_default_1", "Initial selected bus")
    equal(results["Transformer"]["xfmrcode"]["value"], None, "No initial code")
    near(results["Transformer"]["normamps"]["value"], 1100 / (sqrt(3) * 12.47), "Initial normal current")
    near(results["Transformer"]["emergamps"]["value"], 1500 / (sqrt(3) * 12.47), "Initial emergency current")
    equal(results["Transformer"]["basefreq"]["value"], 60.0, "Probe circuit base frequency")
    near(results["XfmrCode"]["rdcohms"]["value"], [0.85 * 0.002 * 12.47**2] * 2, "Code constructor DC ohms")
    return results


def check_winding_edit(cls):
    ctx = new_circuit()
    collection = getattr(ctx, cls)
    obj = collection.new(
        "resize", Windings=2, Conns=["delta", "wye"], kVs=[12.47, 4.16],
        kVAs=[900, 800], Taps=[1.05, 0.95], pctR=[0.3, 0.5],
    )
    fields = ("Conns", "kVs", "kVAs", "Taps", "pctR", "X13", "XSCArray")
    if cls == "Transformer":
        obj.Buses = ["PRIMARY.1", "SECONDARY.1"]
        fields += ("Buses",)

    before = {field: normalize(getattr(obj, field)) for field in fields}
    obj.edit(Windings=3)
    after = {field: normalize(getattr(obj, field)) for field in fields}
    for field, expected in (
        ("Conns", [0, 0, 0]), ("kVs", [12.47] * 3), ("kVAs", [1000] * 3),
        ("Taps", [1] * 3), ("pctR", [0.2] * 3), ("X13", 35),
        ("XSCArray", [7 if cls == "Transformer" else 0, 30, 30]),
    ):
        near(after[field], expected, f"{cls} resized {field}")
    result = {"before": before, "after": after}
    if cls == "Transformer":
        equal(before["Buses"], ["primary.1", "secondary.1"], "Lowercased bus names")
        equal(after["Buses"], ["primary.1", "secondary.1", "resize_3"], "Preserved buses")
        equal((obj.NumTerminals(), obj.NumConductors()), (3, 4), "Topology after resize")
        result["topology_3ph"] = {"terminals": obj.NumTerminals(), "conductors_per_terminal": obj.NumConductors()}
        obj.edit(Phases=1)
        equal((obj.NumTerminals(), obj.NumConductors()), (3, 2), "Topology after phase edit")
        result["topology_1ph"] = {"terminals": obj.NumTerminals(), "conductors_per_terminal": obj.NumConductors()}
    return result


def check_invalid_windings(cls):
    ctx = new_circuit()
    collection = getattr(ctx, cls)
    direct = collection.new("one_direct", begin_edit=False)
    direct.Windings = 1
    equal(direct.Windings, 2, f"{cls} direct Windings=1 readback")
    obj = collection.new("one_edit", begin_edit=False)
    try:
        obj.edit(Windings=1)
    except DSSException as exc:
        error = str(exc)
        if "(#2020031)" not in error or "must be greater than one" not in error:
            raise
    else:
        raise ValueError(f"{cls} edit(Windings=1) did not report error #2020031")
    equal(obj.Windings, 2, f"{cls} edit Windings=1 readback")
    return {"direct_setter_readback": direct.Windings, "edit_readback": obj.Windings, "edit_error": error}


def check_text_and_taps():
    ctx = new_circuit()
    wrong_length = ctx.Transformer.new("wrong_length", begin_edit=False)
    try:
        wrong_length.Buses = ["a", "b", "c", "d"]
    except DSSException as exc:
        length_error = str(exc)
        if "(#20200424)" not in length_error or "Expected 2 elements, got 4" not in length_error:
            raise
    else:
        raise ValueError("Transformer accepted four bus names for two windings")
    obj = ctx.Transformer.new("text", begin_edit=False)
    obj.edit(Taps=[1.5, 1])
    python_taps = normalize(obj.Taps)
    near(python_taps, [1.5, 1.0], "Direct array tap readback")
    obj.edit(Taps=[1, 1])
    ctx.Commands("Edit Transformer.text wdg=1 tap=1.5")
    text_taps = normalize(obj.Taps)
    near(text_taps, [1.5, 1.0], "Text scalar tap readback")
    near(obj.MaxTap, [1.1, 1.1], "MaxTap")
    near(obj.MinTap, [0.9, 0.9], "MinTap")

    ctx.Commands("New XfmrCode.text")
    code = ctx.XfmrCode["text"]
    text_results = {}
    for cls, element in (("Transformer", obj), ("XfmrCode", code)):
        prefix = f"Edit {cls}.text wdg=2"
        bus = " bus=SECONDARY.1.2.3.0" if cls == "Transformer" else ""
        ctx.Commands(prefix + bus + " conn=delta kV=4.16 kVA=700 tap=0.98 %R=0.45 RNeut=0.1 XNeut=0.2")
        expected = {"Wdg": "2", "Conn": "delta", "kV": "4.16", "kVA": "700", "Tap": "0.98",
                    "%R": "0.45", "RNeut": "0.1", "XNeut": "0.2"}
        if bus:
            expected["Bus"] = "secondary.1.2.3.0"
        result = {key: query(ctx, cls, element, key) for key in expected}
        equal(result, expected, f"{cls} selected winding text readbacks")
        absent = [key for key in expected if key not in ("RNeut", "XNeut")]
        equal([key for key in absent if hasattr(element, key)], [], f"{cls} scalar Python accessors")
        equal(element.Conns[1], enums.Connection.delta, f"{cls} connection enum")
        near([element.RNeut[1], element.XNeut[1]], [0.1, 0.2], f"{cls} neutral arrays")
        text_results[cls] = result
    return {
        "bus_length_error": length_error,
        "python_taps": python_taps, "dss_taps": text_taps,
        "max_taps": normalize(obj.MaxTap), "min_taps": normalize(obj.MinTap),
        "selected_winding_text": text_results,
    }


def check_losses_and_ratings(cls):
    ctx = new_circuit()
    obj = getattr(ctx, cls).new("ratings", begin_edit=False)
    obj.edit(pctLoadLoss=1)
    split = normalize(obj.pctR)
    near(split, [0.5, 0.5], f"{cls} loss split")
    obj.edit(pctR=[0.3, 0.6])
    derived = obj.pctLoadLoss
    near(derived, 0.9, f"{cls} loss from pctR")
    obj.edit(pctRs=[0.4, 0.8])
    near(obj.pctLoadLoss, 1.2, f"{cls} loss from pctRs")
    obj.edit(kVAs=[800, 500])
    from_array = [obj.NormHkVA, obj.EmergHkVA]
    near(from_array, [880, 1200], f"{cls} ratings from kVAs")
    ctx.Commands(f"Edit {cls}.ratings wdg=1 kVA=700")
    from_scalar = [obj.NormHkVA, obj.EmergHkVA]
    near(from_scalar, [770, 1050], f"{cls} ratings from winding-1 kVA")
    near(obj.kVAs, [700, 700], f"{cls} scalar kVA propagated")
    return {"pctR_after_loss_write": split, "pctLoadLoss_after_pctR": derived,
            "pctLoadLoss_after_pctRs": obj.pctLoadLoss, "ratings_from_kVAs": from_array,
            "ratings_from_winding_1": from_scalar, "kVAs_after_winding_1": normalize(obj.kVAs)}


def check_impedance(cls):
    ctx = new_circuit()
    obj = getattr(ctx, cls).new("impedance", Windings=3)
    obj.edit(X12=8, X13=31, X23=29)
    scalar_input = normalize(obj.XSCArray)
    near(scalar_input, [8, 31, 29], f"{cls} scalar reactance order")
    obj.edit(XSCArray=[11, 21, 31])
    array_input = normalize(obj.XSCArray)
    scalar_readbacks = [obj.XHL, obj.XHT, obj.XLT]
    near(array_input, [11, 21, 31], f"{cls} explicit array")
    near(scalar_readbacks, [8, 31, 29], f"{cls} retained scalar fields")
    obj.edit(X12=9)
    near(obj.XSCArray, [9, 31, 29], f"{cls} re-derived array")
    return {"from_scalars": scalar_input, "from_array": array_input,
            "scalars_after_array_write": scalar_readbacks, "after_scalar_edit": normalize(obj.XSCArray)}


def check_dc_resistance():
    ctx = new_circuit()
    obj = ctx.Transformer.new("dc", begin_edit=False)
    zbase = (12.47 / sqrt(3)) ** 2
    initial = normalize(obj.RDCOhms)
    near(initial, [0.85 * 0.002 * zbase] * 2, "Initial transformer ohms")
    obj.edit(pctR=[0.4, 0.8])
    derived = normalize(obj.RDCOhms)
    near(derived, [0.85 * 0.004 * zbase, 0.85 * 0.008 * zbase], "Recalculated transformer ohms")
    obj.edit(RDCOhms=[0.5, 0.6])
    obj.edit(pctR=[0.8, 1.2])
    from_array = normalize(obj.RDCOhms)
    near(from_array, [0.85 * 0.008 * zbase, 0.6], "Array write after recalculation")
    ctx.Commands("Edit Transformer.dc wdg=1 RDCOhms=0.5 wdg=2 RDCOhms=0.6")
    obj.edit(pctR=[0.9, 1.3])
    from_text = normalize(obj.RDCOhms)
    near(from_text, [0.5, 0.6], "Per-winding explicit ohms after recalculation")
    return {"voltage_va_base_ohms": zbase, "initial_ohms": initial, "derived_ohms": derived,
            "array_write_after_recalculation": from_array, "scalar_writes_after_recalculation": from_text}


def check_three_winding_code():
    ctx = altdss.NewContext()
    ctx.Commands(DSS_EXAMPLE.read_text(encoding="utf-8"))
    obj = ctx.Transformer["three_winding"]
    code = ctx.XfmrCode["three_phase"]
    equal(ctx.Solution.Converged, True, "DSS example converged")
    equal(obj.NumTerminals(), 3, "DSS example terminals")
    equal(obj.Buses, ["source.1.2.3.0", "secondary.1.2.3.0", "tertiary.1.2.3.0"], "DSS example buses")
    equal(obj.XfmrCode.Name, code.Name, "Code reference")
    fields = ("kVs", "kVAs", "pctR", "XHL", "XSCArray")
    before = {field: normalize(getattr(obj, field)) for field in fields}
    copied = {field: normalize(getattr(code, field)) for field in fields}
    equal(before, copied, "Copied code data")
    near(before["XSCArray"], [7, 35, 30], "DSS example reactances")
    code.edit(kVs=[13.2, 4.8, 2.4], kVAs=[1200, 1200, 1200], pctR=[0.3, 0.3, 0.3], XHL=8)
    edited = {field: normalize(getattr(code, field)) for field in fields}
    after = {field: normalize(getattr(obj, field)) for field in fields}
    equal(after, before, "Transformer retains copied values")
    obj.edit(XfmrCode=code)
    reassigned = {field: normalize(getattr(obj, field)) for field in fields}
    equal(reassigned, edited, "Reassigning copies new code values")
    return {"converged": True, "buses": obj.Buses, "terminals": obj.NumTerminals(), "code": code.Name,
            "initial": before, "edited_code": edited, "after_code_edit": after, "after_reassignment": reassigned}


def check_result_methods():
    ctx = new_circuit()
    obj = ctx.Transformer.new(
        "loaded", Phases=3, Windings=2, Buses=["source.1.2.3.0", "secondary.1.2.3.0"],
        Conns=["wye", "wye"], kVs=[12.47, 4.16], kVAs=[1000, 1000], pctR=[0.2, 0.2], XHL=7,
    )
    presolve = obj.WindingCurrents()
    near(presolve, [0j] * 12, "Unsolved winding currents")
    ctx.Commands("New Load.demo Bus1=secondary.1.2.3.0 Phases=3 Conn=wye kV=4.16 kW=100 PF=1")
    ctx.Solution.Solve()
    equal(ctx.Solution.Converged, True, "Loaded transformer converged")
    currents = obj.WindingCurrents()
    primary, secondary = obj.WindingVoltages(1), obj.WindingVoltages(2)
    losses = obj.LossesByType()
    equal((len(currents), len(primary), len(secondary), len(losses)), (12, 3, 3, 3), "Result lengths")
    assert_allclose(currents[::2], -currents[1::2], rtol=1e-5,
                    err_msg="Opposing winding currents with the default anti-float branch")
    if not (7100 < abs(primary[0]) < 7300 and 2300 < abs(secondary[0]) < 2500):
        raise ValueError("Unexpected winding voltage magnitudes")
    near(losses[0], losses[1] + losses[2], "Total loss")
    near(losses[2], 0j, "No-load loss with default core-loss inputs")
    if not (losses[1].real > 0 and losses[1].imag > 0):
        raise ValueError("Expected positive load losses")
    text = query(ctx, "Transformer", obj, "WdgCurrents")
    if not text:
        raise ValueError("DSS WdgCurrents result is empty")
    equal(hasattr(obj, "WdgCurrents"), False, "No Python WdgCurrents property")
    return {
        "load_kw": 100, "load_power_factor": 1, "converged": True,
        "presolve_winding_currents_a": normalize(presolve), "winding_currents_a": normalize(currents),
        "winding_1_voltages_v": normalize(primary), "winding_2_voltages_v": normalize(secondary),
        "loss_order": ["total", "load", "no_load"], "complex_losses_va": normalize(losses),
        "dss_wdgcurrents": text,
    }


def check_enums():
    expected = {
        enums.Connection: {"wye": 0, "delta": 1},
        enums.CoreType: {"shell": 0, "one_phase": 1, "three_leg": 3, "four_leg": 4, "five_leg": 5,
                         "core_1_phase": 9},
        enums.PhaseSequence: {"Lag": 0, "Lead": 1},
    }
    values = {}
    for enum, members in expected.items():
        values[enum.__name__] = {member.name: int(member) for member in enum}
        equal(values[enum.__name__], members, enum.__name__)
    return values


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    classes = ("Transformer", "XfmrCode")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": read_defaults(),
        "enums": check_enums(),
        "winding_resize": {cls: check_winding_edit(cls) for cls in classes},
        "windings_one": {cls: check_invalid_windings(cls) for cls in classes},
        "text_and_taps": check_text_and_taps(),
        "load_loss_and_ratings": {cls: check_losses_and_ratings(cls) for cls in classes},
        "impedance": {cls: check_impedance(cls) for cls in classes},
        "dc_resistance": check_dc_resistance(),
        "three_winding_code": check_three_winding_code(),
        "loaded_two_winding_results": check_result_methods(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
