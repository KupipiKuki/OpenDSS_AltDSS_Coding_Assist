#!/usr/bin/env python3
"""Print pinned RegControl constructor readbacks and focused control probes."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from math import isclose

from altdss import altdss, enums
from altdss.RegControl import RegControlProperties
from dss import DSSException
from dss.enums import ControlModes

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/regcontrols/regcontrol_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/regcontrol/fixed_tap_voltage.dss"
IEEE13 = LIBRARY_ROOT / "examples/fixtures/ieee13/IEEETestCases/13Bus/IEEE13Nodeckt.dss"


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label, *, tolerance=1e-9):
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def dss_error(action, code, detail):
    try:
        action()
    except DSSException as exc:
        message = str(exc)
        if f"(#{code})" not in message or detail not in message:
            raise
        return message
    raise ValueError(f"Expected DSS error #{code}: {detail}")


def attribute_error(action, field, detail):
    try:
        action()
    except AttributeError as exc:
        message = str(exc)
        if field not in message or detail not in message:
            raise
        return message
    raise ValueError(f"Expected AttributeError for {field}")


def local_circuit():
    ctx = altdss.NewContext()
    ctx.Commands(
        "New Circuit.regcontrol_probe BasekV=12.47 Bus1=source\n"
        "New Transformer.stepdown Phases=3 Windings=2 Buses=[source.1.2.3.0 secondary.1.2.3.0]\n"
        "~ Conns=[wye wye] kVs=[12.47 4.16] kVAs=[1000 1000] XHL=5\n"
        "New Load.fixture Bus1=secondary.1.2.3.0 Phases=3 Conn=wye kV=4.16 kW=100 kvar=20"
    )
    return ctx


def local_regulator(ctx, name="regulator"):
    return ctx.RegControl.new(name, Transformer=ctx.Transformer["stepdown"], Winding=2,
                              VReg=123, Band=2, PTRatio=20)


def ieee13_regulator():
    ctx = altdss.NewContext()
    ctx.Commands(f'Redirect "{IEEE13.as_posix()}"')
    reg = ctx.RegControl["reg1"]
    equal((ctx.Solution.Converged, reg.TapNum), (True, 9), "IEEE13 upstream initial controlled solve")
    return ctx, reg


def pt_voltage(reg):
    voltages = reg.Transformer.WindingVoltages(reg.Winding)
    return float(abs(voltages[0]) / reg.PTRatio)


def solve_result(ctx, reg):
    equal(ctx.Solution.Converged, True, reg.Name + " converged")
    return {"tap": reg.TapNum, "control_mode": ctx.Solution.ControlMode.name,
            "control_iterations": ctx.Solution.ControlIterations, "total_iterations": ctx.Solution.TotalIterations}


def check_defaults():
    ctx = local_circuit()
    reg = ctx.RegControl.new("readback_default", begin_edit=False)
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))[0]["properties"]
    equal(sorted(row["altdss_keyword"] for row in rows), sorted(RegControlProperties.__annotations__),
          "Catalog matches the wrapper keyword surface")
    result = {}
    for row in rows:
        key = row["altdss_keyword"]
        raw = getattr(reg, key)
        if key in ("Like", "Reset"):
            equal(callable(raw), True, key + " is a method")
            result[key] = {"status": "action", "note": "Callable method with no property getter."}
            continue
        expected = row["default_value"]
        if expected is not None:
            equal(raw, expected, key + " default")
        result[key] = {"status": "read back", "type": type(raw).__name__, "value": raw}
    equal(type(reg.PTPhase), int, "Default PTPhase returns ordinary int")
    equal((reg.Transformer, reg.TapNum, reg.BaseFreq), (None, 0, 60), "Unbound defaults")
    equal((reg.TapWinding, reg.RemotePTRatio), (reg.Winding, reg.PTRatio), "Dynamic defaults")
    return result


def check_tap_paths():
    result = {}
    for path in ("controlled_solve", "control_mode_off", "solve_no_control"):
        ctx, reg = ieee13_regulator()
        reg.TapNum = 5
        equal(reg.TapNum, 5, "Manual tap before " + path)
        if path == "control_mode_off":
            ctx.Commands("Set ControlMode=Off")
        if path == "solve_no_control":
            previous_control_iterations = ctx.Solution.ControlIterations
            ctx.Solution.SolveNoControl()
            equal(ctx.Solution.ControlMode, ControlModes.Static, "SolveNoControl leaves the selected mode")
        else:
            ctx.Solution.Solve()
        after = solve_result(ctx, reg)
        if path == "solve_no_control":
            retained = after.pop("control_iterations")
            equal(retained, previous_control_iterations, "SolveNoControl retains the previous control counter")
            after["retained_control_iterations"] = retained
        equal(after["tap"], 9 if path == "controlled_solve" else 5, path + " tap")
        if path == "controlled_solve":
            equal(after["total_iterations"], 12, "Controlled restoration iterations")
        result[path] = {"initial_tap": 9, "manual_tap": 5, **after}
    return result


def check_tap_range_and_winding():
    _, reg = ieee13_regulator()
    transformer = reg.Transformer
    index = reg.TapWinding - 1
    minimum = float(transformer.MinTap[index])
    maximum = float(transformer.MaxTap[index])
    steps = int(transformer.NumTaps[index])
    equal((minimum, maximum, steps), (0.9, 1.1, 32), "Tapped winding range")
    # Immediate readbacks: no control solve follows these manual writes.
    reg.TapNum = 99
    upper = {"request": 99, "tap": reg.TapNum, "present_tap": float(transformer.Taps[index])}
    reg.TapNum = -99
    lower = {"request": -99, "tap": reg.TapNum, "present_tap": float(transformer.Taps[index])}
    equal((upper["tap"], lower["tap"]), (16, -16), "Tap number clamps")
    near(upper["present_tap"], maximum, "Upper present tap")
    near(lower["present_tap"], minimum, "Lower present tap")

    _, reg = ieee13_regulator()
    reg.edit(Winding=2, TapWinding=1)
    equal((reg.Winding, reg.TapWinding), (2, 1), "Separate monitored and moved windings")
    initial = reg.Transformer.Taps.tolist()
    reg.TapNum = 4
    final = reg.Transformer.Taps.tolist()
    near(final[0], 1.025, "Moved winding 1")
    near(final[1], initial[1], "Winding 2 remains constant")
    equal(reg.TapNum, 4, "Tap readback from TapWinding")
    reg.edit(Winding=2)
    equal(reg.TapWinding, 2, "Winding reassign resets TapWinding")
    return {"clamping": {"min_tap": minimum, "max_tap": maximum, "num_taps": steps, "upper": upper, "lower": lower},
            "separate_windings": {"monitored_winding": 2, "tap_winding": 1, "tap_command": 4,
                                  "initial_winding_taps": initial, "after_command": final,
                                  "tap_winding_after_reassign": reg.TapWinding}}


def check_iteration_limit():
    ctx, reg = ieee13_regulator()
    reg.TapNum = 0
    reg.edit(MaxTapChange=1)
    error = dss_error(ctx.Solution.Solve, 485, "Warning Max Control Iterations Exceeded.")
    rejected = {"max_tap_change": reg.MaxTapChange, "max_control_iterations": ctx.Solution.MaxControlIterations,
                "error": error, "tap_at_error": reg.TapNum, "total_iterations": ctx.Solution.TotalIterations}
    ctx, reg = ieee13_regulator()
    reg.TapNum = 0
    equal(reg.MaxTapChange, 16, "Default MaxTapChange")
    ctx.Solution.Solve()
    successful = solve_result(ctx, reg)
    equal((successful["tap"], successful["total_iterations"]), (9, 12), "Default tap limit restores tap")
    return {"manual_start_tap": 0, "one_step": rejected, "default_limit": {"max_tap_change": 16, **successful}}


def check_sensing():
    ctx = local_circuit()
    reg = local_regulator(ctx)
    reg.edit(RemotePTRatio=10)
    first = [reg.PTRatio, reg.RemotePTRatio]
    equal(first, [20, 10], "Independent remote ratio")
    reg.edit(PTRatio=50)
    overwritten = [reg.PTRatio, reg.RemotePTRatio]
    equal(overwritten, [50, 50], "PTRatio resets remote ratio")
    reg.edit(PTRatio=55, RemotePTRatio=12)
    ordered = [reg.PTRatio, reg.RemotePTRatio]
    equal(ordered, [55, 12], "Set remote ratio after PTRatio")

    phases = {}
    for label, value, expected in (("positive_index", 2, 2), ("min", "min", enums.RegControlPhaseSelection.min),
                                   ("max", enums.RegControlPhaseSelection.max, enums.RegControlPhaseSelection.max)):
        reg.edit(PTPhase=value)
        raw = reg.PTPhase
        equal((type(raw), raw), (type(expected), expected), "PTPhase " + label)
        phases[label] = {"type": type(raw).__name__, "value": int(raw)}
        if isinstance(raw, IntEnum):
            phases[label]["member"] = raw.name
    reg.edit(PTPhase=4)
    equal(reg.PTPhase, 1, "Local phase index above winding phases resets")
    phases["out_of_range_positive"] = {"written": 4, "after_edit": reg.PTPhase}

    ctx = local_circuit()
    reg = local_regulator(ctx)
    local = (reg.Bus, reg.NumPhases(), reg.NumConductors())
    equal(local, ("", 3, 3), "Local sensing topology")
    reg.edit(Bus="secondary.1")
    remote = (reg.Bus, reg.NumPhases(), reg.NumConductors())
    equal(remote, ("secondary.1", 1, 2), "Remote sensing topology")
    ctx, reg = ieee13_regulator()
    reg.edit(Bus="634")
    ctx.Solution.Solve()
    remote_solve = solve_result(ctx, reg)
    equal(remote_solve["tap"], 16, "Remote IEEE13 voltage drives to upper tap limit")
    return {"ratio_columns": ["PTRatio", "RemotePTRatio"], "after_remote_only": first,
            "after_ptratio": overwritten, "after_ordered_edit": ordered, "pt_phase": phases,
            "topology_columns": ["Bus", "phases", "conductors"], "local_bus": local, "remote_bus": remote,
            "remote_ieee13": {"bus": reg.Bus, **remote_solve}}


def check_enabled_and_power():
    ctx, reg = ieee13_regulator()
    reg.edit(Enabled=False, VReg=100)
    ctx.Solution.Solve()
    disabled = solve_result(ctx, reg)
    equal(disabled["tap"], 9, "Disabled regulator does not move tap")
    equal(reg.Transformer.Enabled, True, "Transformer remains enabled")

    ctx, reg = ieee13_regulator()
    member = next(element for element in ctx.Element if element.FullName() == reg.FullName())
    powers = [[float(power.real), float(power.imag)] for power in member.TotalPowers()]
    equal(powers, [[0, 0]], "Controller contributes zero terminal power")
    transformer_powers = [[float(power.real), float(power.imag)] for power in reg.Transformer.TotalPowers()]
    if not any(abs(power[0]) > 0 for power in transformer_powers):
        raise ValueError("Expected electrical power on controlled transformer")
    return {"disabled": {"initial_tap": 9, "new_vreg": 100, "enabled": False, **disabled},
            "element": member.FullName(), "control_terminal_power_kw_kvar": powers,
            "transformer_terminal_power_kw_kvar": transformer_powers}


def check_actions_and_keyword_case():
    ctx = local_circuit()
    source = local_regulator(ctx, "source")
    source.edit(VReg=122)
    reg = local_regulator(ctx, "target")
    reg.edit(VReg=110, Band=3)
    before_like = [reg.VReg, reg.Band]
    errors = {}
    for real, wrong in (("VReg", "Vreg"), ("RevVReg", "RevVreg")):
        equal(getattr(reg, real), 110 if real == "VReg" else 120, "Exact keyword " + real)
        errors[wrong] = {
            "attribute": attribute_error(lambda: getattr(reg, wrong), wrong, "no attribute"),
            "constructor": attribute_error(
                lambda: ctx.RegControl.new("wrong_" + wrong, Transformer="stepdown", **{wrong: 120}), wrong, "no attribute"
            ),
        }
    equal(reg.Like("source"), None, "Like returns None")
    after_like = [reg.VReg, reg.Band]
    equal(after_like, [122, 2], "Python Like copies settings")
    ctx.Commands("New RegControl.text_copy Like=source")
    copy = ctx.RegControl["text_copy"]
    equal((copy.VReg, copy.Band), (122, 2), "DSS Like copies settings")
    for name in ("Like", "Reset"):
        errors[name] = attribute_error(
            lambda: ctx.RegControl.new("action_" + name, Transformer="stepdown",
                                      **{name: "source" if name == "Like" else True}),
            name, "read-only",
        )
    # Use a non-neutral manual tap and run neither a power flow nor a control solve.
    source.TapNum = 4
    before_reset = source.TapNum
    equal(before_reset, 4, "Manual tap before reset actions")
    equal(source.Reset(), None, "Reset returns None")
    equal(source.TapNum, before_reset, "Python Reset keeps tap")
    ctx.Commands("Edit RegControl.source Reset=yes")
    equal(source.TapNum, before_reset, "DSS reset keeps tap")
    return {"voltage_fields": ["VReg", "Band"], "before_copy": before_like, "python_like": after_like,
            "dss_like": [copy.VReg, copy.Band], "tap_before_and_after_reset": [before_reset, source.TapNum],
            "errors": errors}


def check_guards():
    messages = {}
    for name, props in (("missing", {"VReg": 120}), ("unknown", {"Transformer": "nosucht"}),
                        ("wrong_class_name", {"Transformer": "probe_line"})):
        ctx = local_circuit()
        ctx.Commands("New Line.probe_line Bus1=secondary.1.2.3 Bus2=other.1.2.3")
        messages[name] = dss_error(lambda: ctx.RegControl.new(name, **props), 124, "Transformer Element is not set.")
    ctx = local_circuit()
    ctx.Commands("New Line.probe_line Bus1=secondary.1.2.3 Bus2=other.1.2.3")
    messages["wrong_class_text"] = dss_error(
        lambda: ctx.Commands("New RegControl.wrong_class_text Transformer=probe_line"), 124, "Transformer Element is not set."
    )
    ctx = local_circuit()
    bare = ctx.RegControl.new("bare")
    equal(bare.Transformer, None, "Bare construction succeeds")
    messages["bare_solve"] = dss_error(ctx.Solution.Solve, 482, "Error Encountered in Solve: Solution aborted.")
    ctx = local_circuit()
    messages["winding"] = dss_error(
        lambda: ctx.RegControl.new("winding", Transformer="stepdown", Winding=5),
        122, 'Winding no. "5" does not exist.',
    )
    return {"observed_errors": messages, "engine_123": "source-only for the supported reference paths"}


def check_examples():
    ctx = local_circuit()
    reg = local_regulator(ctx)
    ctx.Solution.ControlMode = ControlModes.Static
    ctx.Solution.Solve()
    controlled = solve_result(ctx, reg)
    volts = pt_voltage(reg)
    equal(controlled["tap"], 3, "Standalone controlled tap")
    near(volts, 122.16480326, "Standalone controlled PT volts", tolerance=1e-5)
    ctx = altdss.NewContext()
    ctx.Commands(DSS_EXAMPLE.read_text(encoding="utf-8"))
    reg = ctx.RegControl["regulator"]
    fixed = solve_result(ctx, reg)
    equal((fixed["tap"], ctx.TextResult.strip(), ctx.Solution.ControlMode), (4, "4", ControlModes.Off),
          "Standalone DSS manual tap, query and control mode")
    fixed_volts = pt_voltage(reg)
    near(fixed_volts, 122.91428576, "Standalone DSS manual PT volts", tolerance=1e-5)
    return {"python_model": {"solve_path": "static controlled solve", "pt_voltage_v": volts, **controlled},
            "dss_example": {"solve_path": "manual tap with ControlMode=Off", "pt_voltage_v": fixed_volts, **fixed}}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": check_defaults(),
        "tap_paths": check_tap_paths(),
        "tap_range_and_winding": check_tap_range_and_winding(),
        "max_tap_change": check_iteration_limit(),
        "sensing": check_sensing(),
        "enabled_and_power": check_enabled_and_power(),
        "actions_and_casing": check_actions_and_keyword_case(),
        "guards": check_guards(),
        "standalone_examples": check_examples(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
