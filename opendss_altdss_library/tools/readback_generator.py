#!/usr/bin/env python3
"""Print pinned Generator constructor readbacks and focused solve probes."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from math import hypot, sqrt
from pathlib import Path

from altdss import altdss, enums
from dss import DSSException
from numpy.testing import assert_allclose

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/generators/generator_properties.json"
PV_EXAMPLE = LIBRARY_ROOT / "examples/generator/pv_voltage_target.dss"
KV = 12.47
SOURCE_BUS = "source.1.2.3.0"
ENUMS = {
    "Model": enums.GeneratorModel, "DispMode": enums.GeneratorDispatchMode,
    "Status": enums.GeneratorStatus, "Conn": enums.Connection,
}


def circuit():
    ctx = altdss.NewContext()
    ctx.Commands(f"New Circuit.generator_probe BasekV={KV} Bus1=source")
    return ctx


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label, *, rtol=1e-9, atol=1e-10):
    assert_allclose(actual, expected, rtol=rtol, atol=atol, err_msg=label)


def reactive(kw, pf):
    return kw * sqrt(1 / pf**2 - 1)


def setpoints(gen):
    return {key: getattr(gen, key) for key in ("kW", "kvar", "PF", "kVA")}


def check_setpoints(gen, expected):
    values = setpoints(gen)
    near(list(values.values()), expected, gen.Name + " kW, kvar, PF, kVA")
    return values


def power_pair(power):
    return [float(power.real), float(power.imag)]


def solved_power(ctx, gen):
    equal(ctx.Solution.Converged, True, gen.Name + " convergence")
    values = gen.TotalPowers()
    equal((len(values), gen.NumTerminals()), (1, 1), gen.Name + " one terminal result")
    return values[0]


def dss_error(action, code, fragment):
    try:
        action()
    except DSSException as exc:
        message = str(exc)
        if f"(#{code})" not in message or fragment not in message:
            raise
        return message
    raise ValueError(f"Expected DSS error #{code}: {fragment}")


def attribute_error(action, keyword, fragment):
    try:
        action()
    except AttributeError as exc:
        message = str(exc)
        if keyword not in message or fragment not in message:
            raise
        return message
    raise ValueError(f"Expected Python AttributeError for {keyword}")


def read_defaults():
    ctx = circuit()
    gen = ctx.Generator.new("readback_default", begin_edit=False)
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))[0]["properties"]
    results = {}
    for row in rows:
        key = row["name"]
        if key == "mva":
            ctx.Commands("? Generator.readback_default.MVA")
            value = float(ctx.TextResult)
            near(value, 1.2, "Initial MVA rating")
            results[key] = {"status": "DSS text readback", "value": value}
            continue
        keyword = row.get("altdss_keyword", "Name")
        raw = getattr(gen, keyword)
        if keyword in ("Like", "Refuel"):
            equal(callable(raw), True, keyword + " action method")
            results[key] = {"status": "action", "note": "Method without a property getter."}
            continue
        entry = {"status": "read back", "value": getattr(raw, "Name", raw)}
        if keyword in ENUMS:
            equal(type(raw), ENUMS[keyword], keyword + " enum type")
        if isinstance(raw, IntEnum):
            entry.update(enum_type=type(raw).__name__, enum_member=raw.name, value=int(raw))
        if "reference_class" in row:
            entry["object_repr"] = repr(raw)
        if keyword == "DynOut":
            equal(type(raw), list, "DynOut list")
        if row["default_value"] is not None:
            equal(entry["value"], row["default_value"], keyword + " default")
        results[key] = entry

    equal((gen.Name, gen.Bus1, gen.NumTerminals(), gen.NumConductors()),
          ("readback_default", "readback_default_1", 1, 4), "Default topology")
    equal((gen.BaseFreq, gen.Minkvar, gen.Maxkvar), (60, -120, 120), "Default frequency and limits")
    for field in ("Yearly", "Daily", "Duty", "DynamicEq"):
        equal(getattr(gen, field), None, field + " initially unset")
    equal(repr(gen.Spectrum), "<Spectrum.defaultgen>", "Default spectrum object")
    initial = check_setpoints(gen, [1000, 60, 0.88, 1200])
    return {"properties": results, "topology": topology(gen), "initial_schedule": initial,
            "pf_implied_by_kw_and_kvar": gen.kW / hypot(gen.kW, gen.kvar)}


def check_power_specifications():
    ctx = circuit()
    by_pf = ctx.Generator.new("by_pf", kW=2000, PF=0.9)
    by_kvar = ctx.Generator.new("by_kvar", kW=2000, kvar=400)
    ctx.Commands("New Generator.text_pf kW=2000 PF=0.9\nNew Generator.text_kvar kW=2000 kvar=400")
    pf_values = [2000, reactive(2000, 0.9), 0.9, 2400]
    kvar_values = [2000, 400, 2000 / hypot(2000, 400), 2400]
    result = {
        "kw_pf": {"python": check_setpoints(by_pf, pf_values), "text": check_setpoints(ctx.Generator["text_pf"], pf_values)},
        "kw_kvar": {"python": check_setpoints(by_kvar, kvar_values),
                    "text": check_setpoints(ctx.Generator["text_kvar"], kvar_values)},
    }
    by_kvar.edit(PF=0.9)
    result["pf_after_kw_kvar"] = check_setpoints(by_kvar, pf_values)
    by_kvar.edit(Maxkvar=3000, Minkvar=-3000)
    by_kvar.edit(kvar=200)
    equal((by_kvar.Minkvar, by_kvar.Maxkvar), (-400, 400), "kvar write resets explicit PV limits")
    result["limits_after_kvar_edit"] = [by_kvar.Minkvar, by_kvar.Maxkvar]

    rating = ctx.Generator.new("rating_only", kVA=3000)
    result["rating_only"] = check_setpoints(rating, [1000, 60, 0.88, 3000])
    auto = ctx.Generator.new("dynamic_rating", begin_edit=False)
    auto.edit(kW=2000)
    result["auto_rating_after_kw_edit"] = check_setpoints(auto, [2000, reactive(2000, 0.88), 0.88, 2400])
    auto.edit(kVA=5000)
    auto.edit(kW=1000)
    result["explicit_rating_after_kw_edit"] = check_setpoints(auto, [1000, reactive(1000, 0.88), 0.88, 5000])
    return result


def check_mva():
    ctx = circuit()
    ctx.Commands("New Generator.rating Bus1=source.1.2.3.0 kV=12.47 MVA=3")
    gen = ctx.Generator["rating"]
    initial = check_setpoints(gen, [1000, 60, 0.88, 3000])
    ctx.Commands("? Generator.rating.MVA")
    text_value = float(ctx.TextResult)
    equal(text_value, 3, "DSS MVA query")
    gen.edit(kW=700)
    after = check_setpoints(gen, [700, reactive(700, 0.88), 0.88, 3000])
    equal(hasattr(gen, "MVA"), False, "MVA absent from Python object")
    setter_error = attribute_error(lambda: setattr(gen, "MVA", 3), "MVA", "no attribute")
    keyword_error = attribute_error(lambda: ctx.Generator.new("python_mva", MVA=3), "MVA", "no attribute")
    return {"dss_mva": text_value, "setpoints": initial, "after_kw_edit": after,
            "python_attribute_error": setter_error, "python_keyword_error": keyword_error}


def topology(gen):
    return {"phases": gen.Phases, "connection": gen.Conn.name, "bus": gen.Bus1,
            "terminals": gen.NumTerminals(), "conductors": gen.NumConductors()}


def check_topology():
    ctx = circuit()
    results = []
    for phases, conn, conductors in ((3, "wye", 4), (3, "delta", 3), (2, "wye", 3),
                                     (2, "delta", 3), (1, "wye", 2), (1, "delta", 2)):
        gen = ctx.Generator.new(f"g{phases}_{conn}", Phases=phases, Conn=conn)
        equal((gen.NumTerminals(), gen.NumConductors(), gen.Conn), (1, conductors, getattr(enums.Connection, conn)),
              gen.Name + " topology")
        results.append(topology(gen))
    gen = ctx.Generator.new("zero_kv", kW=100)
    gen.edit(kV=0)
    equal(gen.kV, 0, "Zero kV setter accepted")
    bad_kv = ctx.Generator.new("negative_kv", kW=100)
    bad_phases = ctx.Generator.new("zero_phases", kW=100)
    return {"cases": results, "zero_kv_readback": gen.kV,
            "negative_kv_error": dss_error(lambda: bad_kv.edit(kV=-12.47), 2020032, "cannot be negative"),
            "zero_phases_error": dss_error(lambda: bad_phases.edit(Phases=0), 2020031, "cannot be zero")}


def check_snapshot_models():
    results = {}
    for model in (1, 2, 4, 5, 7):
        ctx = circuit()
        ctx.Commands(f"New Load.fixture Bus1={SOURCE_BUS} Phases=3 kV={KV} kW=1500 kvar=500")
        gen = ctx.Generator.new("snapshot", Bus1=SOURCE_BUS, kV=KV, kW=1000, PF=0.95, Model=model)
        ctx.Solution.Solve()
        power = solved_power(ctx, gen)
        near(power, -1000 - reactive(1000, 0.95) * 1j, f"Model {model} in-range terminal power", rtol=0.01)
        results[str(model)] = {"model": gen.Model.name, "scheduled": setpoints(gen),
                               "terminal_power_kw_kvar": power_pair(power), "converged": True}
    ctx = circuit()
    gen = ctx.Generator.new("consuming", Bus1=SOURCE_BUS, kV=KV, kW=-500, PF=0.9)
    ctx.Solution.Solve()
    power = solved_power(ctx, gen)
    near(power, 500 + reactive(500, 0.9) * 1j, "Negative kW draws power", rtol=1e-5)
    equal(gen.kVA, -600, "Automatic rating keeps the sign")
    return {"model_cases": results, "negative_kw": {"scheduled": setpoints(gen),
            "terminal_power_kw_kvar": power_pair(power), "converged": True}}


def check_pv():
    script = PV_EXAMPLE.read_text(encoding="utf-8")
    setup, _, final_command = script.rstrip().rpartition("\n")
    equal(final_command, "Solve", "PV example final command")
    results = {}
    for target, limit in ((1.0, 120), (1.03, 120), (1.0, 3000), (1.03, 3000)):
        ctx = altdss.NewContext()
        if (target, limit) == (1.03, 3000):
            ctx.Commands(script)
            gen = ctx.Generator["pv"]
        else:
            ctx.Commands(setup)
            gen = ctx.Generator["pv"]
            gen.edit(Vpu=target, Maxkvar=limit, Minkvar=-limit)
            ctx.Solution.Solve()
        power = solved_power(ctx, gen)
        v = gen.Voltages()
        voltage_pu = float(sum(abs(phase - v[3]) for phase in v[:3]) / 3 * sqrt(3) / (gen.kV * 1000))
        equal((gen.Model, gen.Vpu, gen.Minkvar, gen.Maxkvar),
              (enums.GeneratorModel.ConstantPV, target, -limit, limit), "PV inputs")
        scheduled = check_setpoints(gen, [800, reactive(800, 0.88), 0.88, 960])
        near(power.real, -800, "PV real power", rtol=1e-5)
        at_limit = (target, limit) != (1.0, 3000)
        if at_limit:
            near(-power.imag, limit, "PV positive injection at Maxkvar", rtol=1e-6)
            if voltage_pu >= target:
                raise ValueError(f"Expected the reactive-limited voltage to stay below its target: {voltage_pu}")
        else:
            near(voltage_pu, target, "Within-range PV target", rtol=1e-6)
            if not 0 < -power.imag < limit:
                raise ValueError(f"Unexpected within-range reactive output: {power}")
        results[f"target_{target}_limit_{limit}"] = {
            "requested_vpu": target, "achieved_vpu": voltage_pu, "min_kvar": gen.Minkvar, "max_kvar": gen.Maxkvar,
            "terminal_power_kw_kvar": power_pair(power), "limiting_property": "Maxkvar" if at_limit else None,
            "scheduled": scheduled, "converged": True,
        }
    near(results["target_1.0_limit_120"]["achieved_vpu"], results["target_1.03_limit_120"]["achieved_vpu"],
         "Both targets saturate at the same narrow limit")
    if results["target_1.03_limit_3000"]["achieved_vpu"] <= results["target_1.03_limit_120"]["achieved_vpu"]:
        raise ValueError("Widening reactive limits did not increase the achieved voltage")
    return results


def check_user_model_guards():
    ctx = circuit()
    missing_path = (Path.cwd() / "missing_phase3b_generator_models" / "model.dll").resolve()
    equal(missing_path.exists(), False, "Missing DLL guard fixture")
    missing = dss_error(lambda: ctx.Generator.new("missing", Model=6, UserModel=str(missing_path)),
                        570, "Not Loaded")
    missing = missing.split(". DSS Directory", maxsplit=1)[0].replace(str(missing_path), "model.dll")
    ctx = circuit()
    gen = ctx.Generator.new("no_user_model", Bus1=SOURCE_BUS, kV=KV, Model=6)
    equal(gen.Model, enums.GeneratorModel.Usermodel, "Model 6 without library constructs")
    undefined = dss_error(ctx.Solution.Solve, 567, "user-written model is not defined")
    ctx = circuit()
    gen = ctx.Generator.new("missing_dynamic", kW=100)
    missing_dynamic = dss_error(lambda: gen.edit(DynamicEq="nonexistent"), 401,
                                'DynamicExp object "nonexistent" not found')
    return {"missing_library_at_construction": missing, "undefined_user_model_at_solve": undefined,
            "missing_dynamic_reference": missing_dynamic, "compiled_model_execution": "not-run",
            "dynamics_and_shaft_execution": "not-run"}


def check_shapes():
    ctx = circuit()
    ctx.Commands(
        "New LoadShape.profile Npts=2 Interval=1 Mult=[0.8 1]\n"
        "New LoadShape.actual Npts=2 Interval=1 UseActual=yes Mult=[100 150] QMult=[15 30]"
    )
    gen = ctx.Generator.new("shaped", Daily="profile")
    equal((gen.Yearly, repr(gen.Daily), gen.Duty), (None, "<LoadShape.profile>", None), "Daily leaves other refs unset")
    refs = {"Yearly": None, "Daily": repr(gen.Daily), "Duty": None}
    actual_refs = {}
    for field in ("Daily", "Yearly", "Duty"):
        shaped = ctx.Generator.new(field, kW=1000, PF=0.9, **{field: ctx.LoadShape["actual"]})
        equal(repr(getattr(shaped, field)), "<LoadShape.actual>", field + " object")
        actual_refs[field] = check_setpoints(shaped, [150, 30, 150 / hypot(150, 30), 1200])
    return {"daily_only": refs, "after_use_actual_assignment": actual_refs, "time_shape_dispatch": "not-run"}


def check_actions_and_fuel():
    ctx = circuit()
    base = ctx.Generator.new("base", Bus1="original.1.2.3", Phases=3, Conn="delta", kV=4.16, kW=200, PF=0.95)
    broken_like = attribute_error(lambda: ctx.Generator.new("kwarg_copy", Like="base"), "Like", "read-only")
    ctx.Commands("New Generator.text_copy Like=base")
    method = ctx.Generator.new("method_copy", Bus1="own_bus")
    method.Like("base")
    copies = {}
    for target, bus in ((ctx.Generator["text_copy"], "text_copy_1"), (method, "own_bus")):
        equal((target.Bus1, target.kW, target.kV, target.Conn, target.NumConductors()),
              (bus, 200, 4.16, enums.Connection.delta, 4), "Like preserves existing wiring and conductors")
        copies[target.Name] = {"topology": topology(target), "scheduled": setpoints(target), "kV": target.kV}
    equal(base.NumConductors(), 3, "Delta source conductor count")

    gen = ctx.Generator.new("fuel", UseFuel=True, FuelkWh=100, DutyStart=1.5)
    ctx.Commands("Edit Generator.fuel %Fuel=50 %Reserve=25")
    state = {field: getattr(gen, field) for field in ("UseFuel", "FuelkWh", "pctFuel", "pctReserve", "DutyStart")}
    equal(list(state.values()), [True, 100, 50, 25, 1.5], "Fuel percent and hour readback")
    gen.Refuel()
    equal((gen.FuelkWh, gen.pctFuel, gen.pctReserve), (100, 100, 25), "Python refuel")
    after_method = {"FuelkWh": gen.FuelkWh, "pctFuel": gen.pctFuel, "pctReserve": gen.pctReserve}
    ctx.Commands("Edit Generator.fuel %Fuel=50 Refuel=yes")
    equal(gen.pctFuel, 100, "DSS refuel")
    broken_refuel = attribute_error(lambda: ctx.Generator.new("kwarg_refuel", Refuel=True), "Refuel", "read-only")
    return {"like": {"source": topology(base), "copies": copies, "python_keyword_error": broken_like},
            "fuel": {"before_refuel": state, "after_python_refuel": after_method, "pct_fuel_after_text_refuel": gen.pctFuel,
                     "python_keyword_error": broken_refuel, "consumption_study": "not-run"}}


def check_dispatch_metadata():
    ctx = circuit()
    gen = ctx.Generator.new("dispatch", kW=100)
    gen.edit(DispMode=3)
    try:
        _ = gen.DispMode
    except ValueError as exc:
        error = str(exc)
        if "not a valid GeneratorDispatchMode" not in error:
            raise
    else:
        raise ValueError("Reading invalid DispMode should raise ValueError")
    return {"invalid_python_enum_readback": error,
            "behavior": {field: "not-run" for field in ("DispMode", "DispValue", "Status", "ForceOn", "PVFactor", "GenDispatcher")}}


def check_registers():
    ctx = circuit()
    gen = ctx.Generator.new("registers", Bus1=SOURCE_BUS, kV=KV, kW=1000, PF=0.95)
    names = ["kWh", "kvarh", "Max kW", "Max kVA", "Hours", "$"]
    equal(gen.RegisterNames(), names, "Register names")
    before = gen.RegisterValues().tolist()
    equal(before, [0] * 6, "Initial register values")
    ctx.Commands("Set Mode=Daily Number=1 StepSize=1h PriceSignal=30\nSolve")
    equal(ctx.Solution.Converged, True, "One-hour register sample")
    after = {name: float(value) for name, value in gen.RegistersDict().items()}
    equal(list(after), names, "Register dictionary names")
    near(list(after.values()), [1000, reactive(1000, 0.95), 1000, 1000 / 0.95, 1, 30],
         "One-hour generator registers")
    return {"names": names, "initial_values": before, "after_one_hour": after, "price_signal": 30}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": read_defaults(),
        "power_specifications": check_power_specifications(),
        "mva_alias": check_mva(),
        "topology": check_topology(),
        "snapshot_power": check_snapshot_models(),
        "pv_voltage_target": check_pv(),
        "user_model_guards": check_user_model_guards(),
        "shapes": check_shapes(),
        "actions_and_fuel": check_actions_and_fuel(),
        "dispatch_review": check_dispatch_metadata(),
        "registers": check_registers(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
