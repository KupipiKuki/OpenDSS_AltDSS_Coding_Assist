#!/usr/bin/env python3
"""Print pinned Capacitor constructor readbacks and focused behavior probes."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from math import pi, sqrt

import numpy as np
from altdss import altdss, enums
from dss import DSSException
from numpy.testing import assert_allclose

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/capacitors/capacitor_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/capacitor/stepped_shunt.dss"
BASE_KV = 12.47
BASE_HZ = 60
SOURCE_BUS = "source.1.2.3"
STEP_FIELDS = ("kvar", "Cuf", "R", "XL", "Harm", "States")
LEGACY_NAMES = ("Model", "Vmin", "Vmax", "StepSize", "Vharmonics", "PctLead", "PctLag", "PtPhase", "Userated", "Spectrum")


def circuit():
    ctx = altdss.NewContext()
    ctx.Commands(f"New Circuit.capacitor_probe BasekV={BASE_KV} Bus1=source")
    return ctx


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label, *, rtol=1e-9, atol=1e-10):
    assert_allclose(actual, expected, rtol=rtol, atol=atol, err_msg=label)


def omega(bank):
    return 2 * pi * bank.BaseFreq


def kvar_to_uf(kvar, bank):
    return 1000 * kvar / (omega(bank) * bank.kV**2)


def ratings(bank):
    return [bank.NormAmps, bank.EmergAmps]


def kvar_ratings(kvar, kv=BASE_KV):
    rated_current = kvar / (sqrt(3) * kv)
    return [1.35 * rated_current, 1.8 * rated_current]


def normalized_power(powers):
    return [[float(value.real), float(value.imag)] for value in powers]


def solve(ctx, bank):
    ctx.Solution.Solve()
    equal(ctx.Solution.Converged, True, bank.Name + " solved")
    result = bank.TotalPowers()
    equal(len(result), bank.NumTerminals(), bank.Name + " result lengths")
    return result


def step_readbacks(bank):
    return {key: getattr(bank, key).tolist() for key in STEP_FIELDS}


def dss_error(action, code, fragment):
    try:
        action()
    except DSSException as exc:
        message = str(exc)
        if f"(#{code})" not in message or fragment not in message:
            raise
        return message
    raise ValueError(f"Expected DSS error #{code}: {fragment}")


def read_defaults():
    ctx = circuit()
    bank = ctx.Capacitor.new("readback_default", begin_edit=False)
    results = {}
    records = json.loads(CATALOG.read_text(encoding="utf-8"))[0]["properties"]
    for row in records:
        key = row["name"]
        keyword = row.get("altdss_keyword", "Name")
        if keyword == "Like":
            equal(callable(bank.Like), True, "Like is an action method")
            results[key] = {"status": "action", "note": "Copy action. See the separate Like probe."}
            continue
        raw = getattr(bank, keyword)
        entry = {"status": "read back"}
        if isinstance(raw, np.ndarray):
            dtype = row["array_element_type"]
            equal(raw.dtype.name, dtype, keyword + " dtype")
            equal(tuple(raw.shape), (0 if keyword == "CMatrix" else bank.NumSteps,), keyword + " shape")
            entry.update(dtype=raw.dtype.name, shape=list(raw.shape), value=raw.tolist())
        elif isinstance(raw, IntEnum):
            equal(type(raw), enums.Connection, "Connection enum type")
            entry.update(enum_type=type(raw).__name__, enum_member=raw.name, value=int(raw))
        else:
            entry["value"] = raw
        if row["default_value"] is not None:
            equal(entry["value"], row["default_value"], f"{keyword} default")
        results[key] = entry
    equal((bank.Name, bank.Bus1, bank.Bus2), ("readback_default", "readback_default_1", "readback_default_1.0.0.0"),
          "Generated grounded bank buses")
    equal(bank.BaseFreq, BASE_HZ, "Circuit frequency")
    equal((bank.NumTerminals(), bank.NumConductors()), (2, 3), "Default topology")
    near(bank.Cuf, [kvar_to_uf(1200, bank)], "Default capacitance")
    near(ratings(bank), kvar_ratings(1200), "Default ratings")
    return {"properties": results, "topology": topology(bank)}


def family_readback(bank):
    return {"kV": bank.kV, "kvar": bank.kvar.tolist(), "Cuf": bank.Cuf.tolist(),
            "CMatrix": bank.CMatrix.tolist(), "ratings_a": ratings(bank)}


def check_families():
    ctx = circuit()
    bank = ctx.Capacitor.new("families", Bus1=SOURCE_BUS, kV=BASE_KV, kvar=[600])
    initial = family_readback(bank)
    near(bank.Cuf, [kvar_to_uf(600, bank)], "kvar-family capacitance")
    bank.edit(Cuf=[10])
    cuf_state = family_readback(bank)
    near(bank.kvar, [600], "Stale kvar after family switch")
    phase_kv = BASE_KV / sqrt(3)
    accumulated_kvar = omega(bank) * 10e-6 * phase_kv**2 / 1000
    near(ratings(bank), [factor * accumulated_kvar / bank.Phases / phase_kv for factor in (1.35, 1.8)],
         "Cuf-family ratings from the pinned accumulator")
    powers = solve(ctx, bank)
    voltages = bank.Voltages()
    measured_q = omega(bank) * 10e-6 * sum(abs(v)**2 for v in voltages[:3] - voltages[3:]) / 1000
    near(powers, [-1j * measured_q, 0j], "Cuf output from solved terminal voltage")
    cuf_state["terminal_powers_kw_kvar"] = normalized_power(powers)
    cuf_state["rating_kvar_accumulator_from_formula"] = accumulated_kvar

    bank.edit(kvar=[600])
    equal(family_readback(bank), initial, "Restore the kvar family")
    triangle = [20, -2, 19, -1, -3, 18]
    full = [20, -2, -1, -2, 19, -3, -1, -3, 18]
    bank.edit(CMatrix=triangle)
    from_triangle = family_readback(bank)
    near(bank.CMatrix, full, "Lower-triangle expansion")
    equal(ratings(bank), [0, 0], "Matrix leaves ratings unset unless specified")
    near(bank.kvar, initial["kvar"], "Matrix leaves kvar readback")
    near(bank.Cuf, initial["Cuf"], "Matrix leaves Cuf readback")
    bank.edit(CMatrix=full)
    equal(family_readback(bank), from_triangle, "Full matrix representation")
    ctx.Commands("Edit Capacitor.families CMatrix=[20 | -2 19 | -1 -3 18]")
    equal(family_readback(bank), from_triangle, "DSS triangle representation")
    matrix_powers = solve(ctx, bank)
    if matrix_powers[0].imag >= 0:
        raise ValueError(f"Expected the matrix bank to supply reactive power: {matrix_powers}")
    bank.edit(kvar=[600])
    restored = family_readback(bank)
    near(restored["CMatrix"], full, "Matrix retained as inactive storage")
    near(ratings(bank), initial["ratings_a"], "Restored kvar ratings")

    bad = ctx.Capacitor.new("bad_matrix", begin_edit=False)
    error = dss_error(lambda: bad.edit(CMatrix=[*triangle, 77, 88]), 2020036,
                      "Provide either the full matrix or the lower triangle")
    return {"kvar": initial, "cuf": cuf_state, "cmatrix": from_triangle, "matrix_input_lengths": [6, 9],
            "matrix_terminal_powers_kw_kvar": normalized_power(matrix_powers), "after_restore_kvar": restored,
            "wrong_matrix_length_error": error}


def check_resize():
    ctx = circuit()
    bank = ctx.Capacitor.new("resize", begin_edit=False)
    bank.edit(NumSteps=4)
    for field, expected in {"kvar": [300] * 4, "Cuf": [kvar_to_uf(300, bank)] * 4,
                            "R": [0] * 4, "XL": [0] * 4, "Harm": [0] * 4, "States": [1] * 4}.items():
        near(getattr(bank, field), expected, field + " after resize")
    equal(sum(bank.kvar), 1200, "Conserved kvar rating")
    ctx.Commands("New Capacitor.json_probe NumSteps=4 kvar=[300 300 300 300] States=[1 0 0 0]")
    exported = json.loads(ctx.Capacitor["json_probe"].to_json())
    equal(any(key.lower() == "numsteps" for key in exported), False, "NumSteps omitted from JSON")
    equal(exported["kvar"], [300] * 4, "JSON step array")
    bad = ctx.Capacitor.new("bad_kvar_length", NumSteps=4)
    length_error = dss_error(lambda: bad.edit(kvar=[100, 200]), 20200425, "Expected 4 elements, got 2")
    late_steps = ctx.Capacitor.new("cuf_then_steps", kV=BASE_KV, Cuf=[10], NumSteps=2)
    near(late_steps.Cuf, [10, 10], "Cuf replication on resize")
    equal(float(late_steps.kvar[0]), 1200, "Stale first kvar entry")
    late_array_error = dss_error(
        lambda: ctx.Capacitor.new("steps_then_short_cuf", kV=BASE_KV, NumSteps=2, Cuf=[10]),
        20200425, "Expected 2 elements, got 1",
    )
    proper = ctx.Capacitor.new("steps_first", kV=BASE_KV, NumSteps=2, Cuf=[10, 20])
    near(proper.Cuf, [10, 20], "Ordered full-length Cuf")
    return {"four_step_bank": step_readbacks(bank), "json_property_keys": list(exported),
            "wrong_kvar_length_error": length_error, "cuf_before_resize": step_readbacks(late_steps),
            "short_cuf_after_resize_error": late_array_error, "full_cuf_after_resize": step_readbacks(proper)}


def check_filter_edits():
    ctx = circuit()
    bank = ctx.Capacitor.new("filter", R=[0.02], XL=[0.4])
    bank.edit(NumSteps=4)
    near(bank.R, [0.08] * 4, "kvar-family R scaling")
    near(bank.XL, [1.6] * 4, "kvar-family XL scaling")
    scaled = step_readbacks(bank)
    bank.edit(Harm=[5] * 4)
    expected_xl = 1 / (omega(bank) * bank.Cuf[0] * 1e-6) / 5**2
    near(bank.XL, [expected_xl] * 4, "Harm-derived XL")
    tuned = step_readbacks(bank)
    cuf = ctx.Capacitor.new("filter_cuf", Cuf=[10], R=[0.02], Harm=[5])
    before = step_readbacks(cuf)
    cuf.edit(NumSteps=2)
    for key in ("Cuf", "R", "XL", "Harm"):
        near(getattr(cuf, key), before[key] * 2, "Cuf-family resize " + key)
    return {"kvar_family_resized": scaled, "after_harm_edit": tuned, "cuf_family_resized": step_readbacks(cuf)}


def topology(bank):
    return {"phases": bank.Phases, "connection": bank.Conn.name, "bus1": bank.Bus1, "bus2": bank.Bus2,
            "terminals": bank.NumTerminals(), "conductors": bank.NumConductors(), "shunt": bank.IsShunt()}


def check_topology():
    ctx = circuit()
    result = {}
    for phases, conn, terminals, conductors in (
        (3, "wye", 2, 3), (3, "delta", 1, 3), (2, "wye", 2, 2), (2, "delta", 1, 3),
        (1, "wye", 2, 1), (1, "delta", 1, 2),
    ):
        name = f"ph{phases}_{conn}"
        bank = ctx.Capacitor.new(name, Phases=phases, Conn=conn, Bus1="primary.1")
        equal((bank.NumTerminals(), bank.NumConductors()), (terminals, conductors), name + " topology")
        equal(bank.Bus2, "primary" + ".0" * phases if conn == "wye" else "", name + " Bus2")
        result[name] = topology(bank)
    bad = ctx.Capacitor.new("zero_phase", begin_edit=False)
    result["zero_phases_error"] = dss_error(lambda: bad.edit(Phases=0), 2020031, "cannot be zero")
    bank = ctx.Capacitor.new("wiring", Bus1="a.1.2.3", Bus2="b.1.2.3")
    equal(bank.IsShunt(), False, "Different-bus series connection")
    before = topology(bank)
    bank.edit(Conn="delta")
    equal(bank.Bus2, "", "Delta removes second terminal")
    delta = topology(bank)
    bank.edit(Conn="wye")
    equal(bank.Bus2, "wiring_2", "Restored wye generates a bus")
    result["topology_transition"] = {"initial": before, "delta": delta, "return_to_wye": topology(bank)}
    return result


def check_series_and_delta_power():
    ctx = circuit()
    ctx.Commands(
        "New Capacitor.series Bus1=source.1.2.3 Bus2=loadbus.1.2.3 Phases=3 Conn=wye kV=12.47 kvar=30000\n"
        "New Load.fixture Bus1=loadbus.1.2.3.0 Phases=3 Conn=wye kV=12.47 kW=1000 kvar=200"
    )
    bank = ctx.Capacitor["series"]
    equal(bank.IsShunt(), False, "Series connection")
    powers = solve(ctx, bank)
    near(powers.real, [1000, -1000], "Series terminal active powers", rtol=1e-5)
    near(powers[1].imag, -200, "Series receiving-end reactive power", rtol=1e-5)
    if not (powers[0].imag > 0 and powers.imag.sum() < 0):
        raise ValueError(f"Unexpected series capacitor power: {powers}")
    result = {"series": {"topology": topology(bank), "terminal_powers_kw_kvar": normalized_power(powers)}}

    ctx = circuit()
    bank = ctx.Capacitor.new("delta", Bus1=SOURCE_BUS, Conn="delta", kV=BASE_KV, kvar=[600])
    powers = solve(ctx, bank)
    near(powers, [-600j], "Delta shunt power", rtol=0.01)
    result["delta"] = {"topology": topology(bank), "terminal_powers_kw_kvar": normalized_power(powers)}
    return result


def check_states():
    ctx = altdss.NewContext()
    ctx.Commands(DSS_EXAMPLE.read_text(encoding="utf-8"))
    bank = ctx.Capacitor["steps"]
    equal(ctx.Solution.Converged, True, "DSS example final solve")
    equal(bank.States.tolist(), [1, 0, 0, 0], "DSS example final States")
    one = bank.TotalPowers()
    bank.States = np.asarray([0, 1, 1, 0], dtype=np.int32)
    after_attr = bank.States.tolist()
    equal(after_attr, [1, 0, 0, 0], "Object setter no-op")
    near(solve(ctx, bank), one, "Same solved power after no-op")
    bank.edit(States=[0, 1, 1, 0])
    after_edit = bank.States.tolist()
    equal(after_edit, [1, 0, 0, 0], "Python edit no-op")
    ctx.Commands("Edit Capacitor.steps States=[1 1 1 1]")
    all_on = solve(ctx, bank)
    equal(bank.States.tolist(), [1] * 4, "DSS all on")
    near(all_on, [-1200j, 0j], "Shunt output with four energized steps", rtol=0.01)
    near(one[0].imag / all_on[0].imag, 0.25, "One-step fraction at solved voltage", rtol=0.002)
    ctx.Commands("Edit Capacitor.steps State=[0 0 1 1]")
    abbreviated = bank.States.tolist()
    equal(abbreviated, [0, 0, 1, 1], "State is a DSS abbreviation for States")

    kwargs = ctx.Capacitor.new("kwargs", NumSteps=4, kvar=[300] * 4, States=[0, 1, 1, 0])
    equal(kwargs.States.tolist(), [1] * 4, "Python creation keyword no-op")
    return {"text_single_step": normalized_power(one), "states_after_python_attribute": after_attr,
            "states_after_python_edit": after_edit, "states_from_python_kwargs": kwargs.States.tolist(),
            "text_all_steps": normalized_power(all_on), "one_to_all_kvar_ratio": float(one[0].imag / all_on[0].imag),
            "states_after_text_abbreviation": abbreviated}


def check_unequal_steps():
    results = {}
    for field, values in (("kvar", [100, 200]), ("Cuf", [7, 14])):
        ctx = circuit()
        bank = ctx.Capacitor.new("unequal", Bus1=SOURCE_BUS, kV=BASE_KV, NumSteps=2, **{field: values})
        outputs = []
        for state in ("[1 0]", "[0 1]"):
            ctx.Commands(f"Edit Capacitor.unequal States={state}")
            outputs.append(float(-solve(ctx, bank)[0].imag))
        if field == "kvar":
            near(bank.Cuf, [kvar_to_uf(100, bank)] * 2, "Equal capacitance from first kvar entry")
            near(outputs, [100, 100], "Equal output for unequal kvar array", rtol=0.002)
        else:
            near(outputs[1] / outputs[0], 2, "Different output for unequal Cuf array", rtol=0.002)
        results[field] = {"step_arrays": step_readbacks(bank), "single_step_output_kvar": outputs}
    return results


def check_ratings():
    ctx = circuit()
    result = {}
    for name, overrides in (("automatic", {}), ("explicit_normal", {"NormAmps": 50}),
                            ("both_explicit", {"NormAmps": 50, "EmergAmps": 90})):
        bank = ctx.Capacitor.new(name, kvar=[1200], **overrides)
        initial = ratings(bank)
        bank.edit(kvar=[2400])
        expected = [overrides.get(field, default) for field, default in
                    zip(("NormAmps", "EmergAmps"), kvar_ratings(2400), strict=True)]
        near(ratings(bank), expected, name + " edited ratings")
        result[name] = {"at_1200_kvar_a": initial, "at_2400_kvar_a": ratings(bank)}
    ctx.Commands("Edit Capacitor.both_explicit pctPerm=50 Repair=3")
    equal((bank.pctPerm, bank.Repair), (50, 3), "Percent and hour readback")
    result["pct_perm"] = bank.pctPerm
    result["repair_hours"] = bank.Repair
    return result


def check_like_and_legacy_names():
    ctx = circuit()
    source = ctx.Capacitor.new("origin", Bus1="origin_bus", Conn="delta", kV=4.16, kvar=[250])
    try:
        ctx.Capacitor.new("copy_kwargs", Like="origin")
    except AttributeError as exc:
        keyword_error = str(exc)
        if "Like" not in keyword_error or "read-only" not in keyword_error:
            raise
    else:
        raise ValueError("Like keyword unexpectedly succeeded")
    method = ctx.Capacitor.new("copy_method", Bus1="target_bus")
    method.Like("origin")
    ctx.Commands("New Capacitor.copy_text Like=origin")
    copies = {}
    for target, bus in ((method, "target_bus"), (ctx.Capacitor["copy_text"], "copy_text_1")):
        equal((target.Bus1, target.kV, target.kvar.tolist(), target.Conn, target.NumTerminals()),
              (bus, 4.16, [250], enums.Connection.delta, 2), "Like retains target buses and terminal count")
        copies[target.Name] = {"topology": topology(target), "kV": target.kV, "kvar": target.kvar.tolist()}
    equal(source.NumTerminals(), 1, "Source delta terminal count")
    errors = {}
    for field in (*LEGACY_NAMES, "State"):
        equal(hasattr(source, field), False, "Missing Python property " + field)
        if field != "State":
            errors[field] = dss_error(lambda: ctx.Commands(f"Edit Capacitor.origin {field}=1"), 110,
                                      f'Unknown parameter "{field}"')
    return {"kwargs_error": keyword_error, "source": topology(source), "copied": copies,
            "absent_python_properties": [*LEGACY_NAMES, "State"], "unknown_dss_parameters": errors}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": read_defaults(),
        "specification_families": check_families(),
        "resize": check_resize(),
        "filter_edits": check_filter_edits(),
        "topology": check_topology(),
        "series_and_delta_power": check_series_and_delta_power(),
        "step_switching": check_states(),
        "unequal_steps": check_unequal_steps(),
        "ratings": check_ratings(),
        "like_and_legacy_names": check_like_and_legacy_names(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
