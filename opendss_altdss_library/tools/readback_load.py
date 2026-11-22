#!/usr/bin/env python3
"""Print pinned Load constructor readbacks and focused behavior probes."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from math import hypot, sqrt

from altdss import altdss, enums
from dss import DSSException
from numpy.testing import assert_allclose

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/loads/load_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/load/zipv_snapshot.dss"
POWER_FIELDS = ("kW", "kvar", "PF", "kVA")
ENUM_TYPES = {"Model": enums.LoadModel, "Status": enums.LoadStatus, "Conn": enums.Connection}


def circuit():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.load_probe BasekV=12.47 Bus1=source")
    return ctx


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label, *, rtol=1e-9):
    assert_allclose(actual, expected, rtol=rtol, atol=1e-12, err_msg=label)


def nominal(load):
    return {field: getattr(load, field) for field in POWER_FIELDS}


def check_nominal(load, expected):
    actual = nominal(load)
    near(list(actual.values()), expected, f"{load.Name}, fields {POWER_FIELDS}")
    return actual


def reactive(kw, pf):
    return kw * sqrt(1 / pf**2 - 1)


def read_defaults():
    ctx = circuit()
    load = ctx.Load.new("readback_default", begin_edit=False)
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))[0]["properties"]
    results = {}
    for row in rows:
        key, keyword = row["name"], row.get("altdss_keyword", "Name")
        if keyword == "Like":
            results[key] = {"status": "action", "note": "Creation keyword and action method with no getter."}
            continue
        raw = getattr(load, keyword)
        value = raw.tolist() if hasattr(raw, "tolist") else getattr(raw, "Name", raw)
        entry = {"status": "read back"}
        if keyword in ENUM_TYPES:
            equal(type(raw), ENUM_TYPES[keyword], keyword + " enum type")
        if isinstance(raw, IntEnum):
            entry.update(enum_type=type(raw).__name__, enum_member=raw.name)
            value = int(raw)
        if "reference_class" in row:
            entry["object_repr"] = repr(raw)
        entry["value"] = value
        if row["default_value"] is not None:
            equal(value, row["default_value"], f"Load.{keyword} default")
        results[key] = entry

    equal(load.Name, "readback_default", "Identifier")
    equal(load.Bus1, "readback_default_1", "Generated bus")
    equal(load.BaseFreq, 60, "Circuit fundamental")
    equal((load.NumTerminals(), load.NumConductors()), (1, 4), "Default topology")
    near(load.ZIPV, [0] * 7, "Initial ZIPV storage")
    equal(repr(load.Spectrum), "<Spectrum.defaultload>", "Spectrum default object")
    for field in ("Daily", "Yearly", "Duty", "Growth", "CVRCurve"):
        equal(getattr(load, field), None, f"{field} initially unset")
    check_nominal(load, [10, reactive(10, 0.88), 0.88, 10 / 0.88])
    return results


def check_families():
    ctx = circuit()
    energy_kw = 30000 / (30 * 24) * 4
    specifications = (
        ("kw_pf", {"kW": 100, "PF": 0.95}, [100, reactive(100, 0.95), 0.95, 100 / 0.95]),
        ("kw_kvar", {"kW": 100, "kvar": 30}, [100, 30, 100 / hypot(100, 30), hypot(100, 30)]),
        ("kva_pf", {"kVA": 200, "PF": 0.9}, [180, reactive(180, 0.9), 0.9, 200]),
        ("connected_kva", {"PF": 0.9, "XfkVA": 100, "AllocationFactor": 0.5}, [45, reactive(45, 0.9), 0.9, 0]),
        ("billed_energy", {"kWh": 30000, "kWhDays": 30, "CFactor": 4, "PF": 0.9},
         [energy_kw, reactive(energy_kw, 0.9), 0.9, 0]),
    )
    results = {}
    for label, props, expected in specifications:
        by_python = ctx.Load.new(label + "_py", **props)
        dss_name = label + "_dss"
        command = " ".join(f"{key}={value}" for key, value in props.items())
        ctx.Commands(f"New Load.{dss_name} {command}")
        results[label] = {
            "input_order": list(props),
            "inputs": props,
            "python": check_nominal(by_python, expected),
            "dss_text": check_nominal(ctx.Load[dss_name], expected),
        }
    return results


def check_family_switch():
    ctx = circuit()
    result = {}
    kw, kvar = 50, 20
    kva = hypot(kw, kvar)
    pf = kw / kva
    for path in ("attribute", "edit", "dss_text"):
        load = ctx.Load.new(path, kW=kw, PF=0.9)
        initial = check_nominal(load, [kw, reactive(kw, 0.9), 0.9, kw / 0.9])
        steps = {}
        for keyword, value, expected in (
            ("kvar", kvar, [kw, kvar, pf, kva]),
            ("PF", 0.8, [kw, kvar, pf, kva]),
            ("kVA", 100, [100 * pf, reactive(100 * pf, pf), pf, 100]),
        ):
            if path == "attribute":
                setattr(load, keyword, value)
            elif path == "edit":
                load.edit(**{keyword: value})
            else:
                ctx.Commands(f"Edit Load.{path} {keyword}={value}")
            steps[keyword] = check_nominal(load, expected)
        result[path] = {"initial": initial, "after_each_write": steps}

    load = ctx.Load.new("last_family", kW=kw, kvar=kvar)
    load.edit(kWh=30000, kWhDays=30, CFactor=4, PF=0.9)
    energy_kw = 30000 / (30 * 24) * 4
    result["energy_after_kw_kvar"] = check_nominal(load, [energy_kw, reactive(energy_kw, 0.9), 0.9, kva])
    load.edit(kVA=200, PF=0.9)
    result["kva_after_energy"] = check_nominal(load, [180, reactive(180, 0.9), 0.9, 200])
    load.edit(kW=100, PF=0.95)
    result["kw_after_kva"] = check_nominal(load, [100, reactive(100, 0.95), 0.95, 100 / 0.95])
    return result


def check_allocation_order():
    ctx = circuit()
    results = {}
    for label, props, expected_kw in (
        ("pf_last", {"XfkVA": 100, "AllocationFactor": 0.5, "PF": 0.9}, 44),
        ("pf_first", {"PF": 0.9, "XfkVA": 100, "AllocationFactor": 0.5}, 45),
    ):
        expected = [expected_kw, reactive(expected_kw, 0.9), 0.9, 0]
        load = ctx.Load.new(label, **props)
        fields = " ".join(f"{key}={value}" for key, value in props.items())
        ctx.Commands(f"New Load.{label}_text {fields}")
        results[label] = {"keyword_order": list(props), "python": check_nominal(load, expected),
                          "dss_text": check_nominal(ctx.Load[label + "_text"], expected)}
    load = ctx.Load["pf_last"]
    load.edit(AllocationFactor=0.5)
    results["repeat_allocation_at_new_pf"] = check_nominal(load, [45, reactive(45, 0.9), 0.9, 0])
    return results


def check_edit_finalization():
    ctx = circuit()
    expected = [50, reactive(50, 0.9), 0.9, 50 / 0.9]
    stale = [50, reactive(10, 0.88), 0.9, 10 / 0.88]
    results = {}
    for label, order in (("kw_first", ("kW", "PF")), ("pf_first", ("PF", "kW"))):
        values = {"kW": 50, "PF": 0.9}
        load = ctx.Load.new(label)
        for field in order:
            setattr(load, field, values[field])
        before = check_nominal(load, stale)
        load.end_edit()
        results[label] = {"open_edit": before, "after_end_edit": check_nominal(load, expected)}
    by_kwargs = ctx.Load.new("kwargs", kW=50, PF=0.9)
    ctx.Commands("New Load.text kW=50 PF=0.9")
    results["kwargs"] = check_nominal(by_kwargs, expected)
    results["text"] = check_nominal(ctx.Load["text"], expected)
    by_closed_edit = ctx.Load.new("closed_edit", begin_edit=False)
    by_closed_edit.kW = 50
    by_closed_edit.PF = 0.9
    results["bare_begin_edit_false"] = check_nominal(by_closed_edit, stale)
    by_closed_edit.edit(kW=50, PF=0.9)
    results["completed_edit"] = check_nominal(by_closed_edit, expected)
    with_completed_kwargs = ctx.Load.new("closed_kwargs", kW=10, PF=0.88)
    with_completed_kwargs.kW = 50
    with_completed_kwargs.PF = 0.9
    results["attributes_after_completed_kwargs"] = check_nominal(with_completed_kwargs, expected)
    return results


def check_connections():
    ctx = circuit()
    load = ctx.Load.new("connections", Bus1="source.1.2.3.0", kV=12.47, kW=60, kvar=15)
    cases = [(3, "wye", 4), (3, "delta", 3), (2, "wye", 3), (2, "delta", 3),
             (1, "wye", 2), (1, "delta", 2)]
    results = []
    for phases, conn, conductors in cases:
        load.edit(Phases=phases, Conn=conn)
        equal((load.NumConductors(), load.NumTerminals()), (conductors, 1), "Load topology")
        equal(load.Conn, getattr(enums.Connection, conn), "Connection enum readback")
        results.append({"phases": phases, "connection": load.Conn.name,
                        "conductors": load.NumConductors(), "terminals": load.NumTerminals()})
    before = nominal(load)
    load.edit(kV=4.16)
    equal(load.kV, 4.16, "Rated voltage write")
    equal(nominal(load), before, "Rated voltage edit retains nominal power")
    return {"topology": results, "rated_kv_after_edit": load.kV, "power_after_kv_edit": nominal(load)}


def check_shapes():
    ctx = circuit()
    ctx.Commands(
        "New LoadShape.profile npts=2 interval=1 mult=[0.9 1]\n"
        "New LoadShape.actual npts=2 interval=1 UseActual=yes mult=[1 1.5]\n"
        "New LoadShape.actual_pq npts=2 interval=1 UseActual=yes mult=[1 1.5] Qmult=[0.4 0.6]\n"
        "New GrowthShape.grow npts=1 year=[2026] mult=[1.02]"
    )
    daily = ctx.Load.new("daily_only", Daily="profile")
    yearly = ctx.Load.new("yearly_only", Yearly="profile")
    equal((repr(daily.Daily), repr(daily.Yearly)), ("<LoadShape.profile>",) * 2, "Daily fills unset Yearly")
    equal(yearly.Daily, None, "Yearly leaves Daily unset")
    equal(repr(yearly.Yearly), "<LoadShape.profile>", "Yearly object")
    actual = ctx.Load.new("actual_pf", kW=10, PF=0.9, Daily="actual")
    actual_pf = check_nominal(actual, [1.5, reactive(1.5, 0.9), 0.9, 1.5 / 0.9])
    actual_pq = {}
    for keyword in ("Daily", "Yearly", "Duty"):
        load = ctx.Load.new(keyword, kW=10, kvar=2, **{keyword: ctx.LoadShape["actual_pq"]})
        equal(repr(getattr(load, keyword)), "<LoadShape.actual_pq>", f"{keyword} actual object")
        actual_pq[keyword] = check_nominal(load, [1.5, 0.6, 1.5 / hypot(1.5, 0.6), hypot(1.5, 0.6)])
    refs = ctx.Load.new("refs", Yearly="profile", Daily="actual", Duty="profile",
                        Growth=ctx.GrowthShape["grow"], CVRCurve="profile")
    references = {field: repr(getattr(refs, field)) for field in ("Daily", "Yearly", "Duty", "Growth", "CVRCurve")}
    equal(references, {
        "Daily": "<LoadShape.actual>", "Yearly": "<LoadShape.profile>", "Duty": "<LoadShape.profile>",
        "Growth": "<GrowthShape.grow>", "CVRCurve": "<LoadShape.profile>",
    }, "Shape references and preservation of explicit Yearly")
    return {"daily_only": {"Daily": repr(daily.Daily), "Yearly": repr(daily.Yearly)},
            "yearly_only": {"Daily": None, "Yearly": repr(yearly.Yearly)},
            "use_actual_with_pf": actual_pf, "use_actual_with_kvar": actual_pq, "references": references}


def check_scaled_fields():
    ctx = circuit()
    ctx.Commands("New Load.percent %Mean=75 %StdDev=12 %SeriesRL=30")
    load = ctx.Load["percent"]
    values = {field: getattr(load, field) for field in ("pctMean", "pctStdDev", "pctSeriesRL")}
    near(list(values.values()), [75, 12, 30], "Percent text writes and Python readbacks")
    return values


def check_zipv_solve():
    ctx = altdss.NewContext()
    ctx.Commands(DSS_EXAMPLE.read_text(encoding="utf-8"))
    load = ctx.Load["zip_snapshot"]
    equal(ctx.Solution.Converged, True, "DSS ZIPV solve")
    equal((type(load.Model), load.Model), (enums.LoadModel, enums.LoadModel.ZIPV), "ZIPV model")
    coefficients = load.ZIPV.tolist()
    equal(coefficients, [0, 0, 1, 0, 0, 1, 0.8], "ZIPV coefficients")
    total = load.TotalPowers()
    near(total, [60 + 15j], "Served ZIPV power", rtol=1e-6)
    currents = load.Currents()
    equal(len(currents), 4, "ZIPV terminal current count")
    if not all(2 < abs(current) < 4 for current in currents[:3]):
        raise ValueError(f"Unexpected phase currents: {currents}")
    bad = ctx.Load.new("bad_zip_length", kW=1, PF=1)
    try:
        bad.edit(ZIPV=[0, 0, 1, 0, 0, 1])
    except DSSException as exc:
        length_error = str(exc)
        if "(#20200423)" not in length_error or "Expected 7 elements, got 6" not in length_error:
            raise
    else:
        raise ValueError("The engine accepted a six-value ZIPV array")
    return {"converged": True, "model": load.Model.name, "coefficients": coefficients,
            "total_power_kw_kvar": [float(total[0].real), float(total[0].imag)],
            "currents_a": [[float(i.real), float(i.imag)] for i in currents],
            "wrong_length_error": length_error}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": read_defaults(),
        "specification_families": check_families(),
        "family_switch": check_family_switch(),
        "allocation_order": check_allocation_order(),
        "edit_finalization": check_edit_finalization(),
        "connections": check_connections(),
        "shape_assignment": check_shapes(),
        "scaled_percent_fields": check_scaled_fields(),
        "zipv_solve": check_zipv_solve(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
