#!/usr/bin/env python3
"""Check the pinned LoadShape surface and print a reproducible readback matrix."""
from __future__ import annotations

import json
from datetime import date
from math import isclose
from runpy import run_path

from altdss import altdss, enums
from altdss.LoadShape import LoadShapeProperties
from dss import DSSException
from dss.enums import SolveModes

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/loadshapes/loadshape_properties.json"
EXAMPLES = LIBRARY_ROOT / "examples/loadshape"


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def near(actual, expected, label):
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=0.001):
        raise ValueError(f"{label}: expected {expected}, observed {actual}")


def expected_error(action, error_type, text):
    try:
        action()
    except error_type as exc:
        if text not in str(exc):
            raise
        return str(exc)
    raise ValueError(f"Expected {error_type.__name__} with {text!r}")


def circuit():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.loadshape_probe BasekV=12.47 Bus1=source")
    return ctx


def add_load(ctx):
    ctx.Commands("New Load.demo Bus1=source.1.2.3.0 Phases=3 Conn=wye kV=12.47 kW=100 kvar=20")
    return ctx.Load["demo"]


def configure_daily(solution, number):
    solution.Mode = SolveModes.Daily
    solution.Number = number
    solution.StepSize = 3600
    solution.Hour = 0
    solution.Seconds = 0


def defaults_and_empty_statistics():
    ctx = circuit()
    shape = ctx.LoadShape.new("blank", begin_edit=False)
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))[0]["properties"]
    equal(sorted(row["altdss_keyword"] for row in rows), sorted(LoadShapeProperties.__annotations__),
          "Wrapper keyword surface")
    result = {}
    stats_errors = {}
    for row in rows:
        key = row["altdss_keyword"]
        if key in ("Mean", "StdDev"):
            # These getters can leave an engine error pending. Isolate each getter and consume its error.
            probe_ctx = circuit()
            probe = probe_ctx.LoadShape.new("empty_statistics", begin_edit=False)
            raw = getattr(probe, key)
            stats_errors[key] = expected_error(
                lambda: probe.CSVFile, DSSException, "(#61107) LoadShape has no data to be normalized."
            )
            equal(probe.CSVFile, "", "CSVFile after consuming the pending error")
        else:
            raw = getattr(shape, key)
        if key in ("Action", "Like"):
            equal(callable(raw), True, key + " is a method")
            result[key] = {"status": "action", "python_method": key}
        else:
            value = raw.tolist() if row["data_type"] == "array" else raw
            equal(value, row["default_value"], key + " default")
            result[key] = {"status": "read back", "type": type(raw).__name__, "value": value}
    equal(shape.Interpolation, enums.LoadShapeInterpolation.Avg, "Default interpolation mode")
    result["Interpolation"]["member"] = shape.Interpolation.name
    return result, {"fresh_csv_file": result["CSVFile"]["value"], "csv_read_after_statistics": stats_errors,
                    "csv_file_after_error_is_consumed": ""}


def check_lengths():
    ctx = circuit()
    empty = ctx.LoadShape.new("daily24", begin_edit=False)
    before = expected_error(lambda: empty.edit(PMult=[1.0] * 24), DSSException,
                            "(#20200425) LoadShape.daily24.PMult: Invalid number of elements. Expected 0 elements, got 24.")
    four = ctx.LoadShape.new("s1", NPts=4, PMult=[1, 2, 3, 4])
    errors = {
        "too_short": expected_error(lambda: four.edit(PMult=[1, 2]), DSSException,
                                    "(#20200425) LoadShape.s1.PMult: Invalid number of elements. Expected 4 elements, got 2."),
        "too_long": expected_error(lambda: four.edit(PMult=[1, 2, 3, 4, 5]), DSSException,
                                   "(#20200425) LoadShape.s1.PMult: Invalid number of elements. Expected 4 elements, got 5."),
    }
    equal(four.PMult.tolist(), [1, 2, 3, 4], "Rejected writes preserve the samples")
    # Grow by assigning a distinct shape so previously allocated buffers are never read or written at an invalid count.
    load = add_load(ctx)
    load.edit(Daily=four)
    replacement = ctx.LoadShape.new("s1_six_points", NPts=6, PMult=[1, 2, 3, 4, 5, 6])
    load.edit(Daily=replacement)
    equal(load.Daily, replacement, "Larger replacement bound to the load")
    equal((four.NPts, four.PMult.tolist()), (4, [1, 2, 3, 4]), "Original object preserved")
    equal((replacement.NPts, replacement.PMult.tolist()), (6, [1, 2, 3, 4, 5, 6]), "Sized replacement")
    return (
        {"before_npts": before, **errors, "exact_length": four.PMult.tolist()},
        {"unsafe_resize": "source-only: NPts changes the count without reallocating populated arrays",
         "original_npts": four.NPts, "replacement_npts": replacement.NPts,
         "replacement_pmult": load.Daily.PMult.tolist(), "daily_binding": load.Daily.FullName()},
    )


def interval_values(shape):
    return [shape.Interval, shape.SInterval, shape.MInterval]


def check_intervals():
    ctx = circuit()
    shape = ctx.LoadShape.new("intervals", begin_edit=False)
    initial = interval_values(shape)
    shape.edit(SInterval=1800)
    seconds = interval_values(shape)
    equal(seconds, [0.5, 1800, 30], "Write seconds")
    shape.edit(MInterval=15)
    minutes = interval_values(shape)
    equal(minutes, [0.25, 900, 15], "Write minutes")
    shape.edit(Interval=2)
    hours = interval_values(shape)
    equal(hours, [2.0, 7200, 120], "Write hours")
    variable = ctx.LoadShape.new("variable", NPts=3, Interval=0, Hour=[0.25, 1.0, 2.5],
                                 PMult=[0.5, 1.0, 1.5], QMult=[0.4, 0.9, 1.4])
    equal(interval_values(variable), [0, 0, 0], "Variable interval units")
    equal(variable.Hour.tolist(), [0.25, 1, 2.5], "Variable sample times")
    equal(variable.QMult.tolist(), [0.4, 0.9, 1.4], "Variable reactive samples")
    fixed = ctx.LoadShape.new("fixed", NPts=3, Interval=1, PMult=[0.5, 1.0, 1.5], Hour=[0.25, 1, 2.5])
    ctx.Commands("New LoadShape.text_hours npts=3 interval=1 mult=(0.5 1 1.5) hour=(0.25 1 2.5)")
    text = ctx.LoadShape["text_hours"]
    equal((fixed.Interval, text.Interval), (1, 0), "Python and DSS text Hour writes")
    return {"columns": ["Interval", "SInterval", "MInterval"], "initial": initial,
            "set_seconds": seconds, "set_minutes": minutes, "set_hours": hours,
            "variable": {"interval": variable.Interval, "hour": variable.Hour.tolist(),
                         "pmult": variable.PMult.tolist(), "qmult": variable.QMult.tolist()},
            "interval_after_hour_write": {"alt_dss_python": fixed.Interval, "dss_text": text.Interval}}


def check_actions_and_alias():
    ctx = circuit()
    shape = ctx.LoadShape.new("normalize", NPts=3, PMult=[1, 2, 4], QMult=[1, 2, 3])
    before = {"pmult": shape.PMult.tolist(), "pmax": shape.PMax, "pbase": shape.PBase}
    equal(before, {"pmult": [1, 2, 4], "pmax": 4, "pbase": 0}, "Data-derived PMax")
    equal(shape.Action(enums.LoadShapeAction.Normalize), None, "Normalize is a callable action")
    default_base = shape.PMult.tolist()
    equal(default_base, [0.25, 0.5, 1], "Peak-derived normalization divisor")
    shape = ctx.LoadShape.new("custom_base", NPts=3, PMult=[2, 4, 8], QMult=[1, 2, 4],
                              PBase=4, QBase=2, UseActual=True)
    shape.Action(enums.LoadShapeAction.Normalize)
    equal((shape.PMult.tolist(), shape.QMult.tolist(), shape.UseActual),
          ([0.5, 1, 2], [0.5, 1, 2], False), "Normalization uses explicit bases and clears UseActual")
    bases = {"pbase": shape.PBase, "qbase": shape.QBase, "pmult": shape.PMult.tolist(),
             "qmult": shape.QMult.tolist(), "use_actual": shape.UseActual}
    ctx.Commands("New LoadShape.s2 npts=3 mult=(0.1 0.2 0.3) qmult=(0.2 0.3 0.4)")
    source = ctx.LoadShape["s2"]
    equal(source.PMult.tolist(), [0.1, 0.2, 0.3], "DSS Mult alias")
    copy = ctx.LoadShape.new("s3", begin_edit=False)
    equal(copy.Like("s2"), None, "Like is callable")
    ctx.Commands("New LoadShape.text_copy Like=s2")
    for target in (copy, ctx.LoadShape["text_copy"]):
        equal((target.NPts, target.PMult.tolist(), target.QMult.tolist()),
              (3, [0.1, 0.2, 0.3], [0.2, 0.3, 0.4]), "Like copies both arrays")
    errors = {
        "Action": expected_error(lambda: ctx.LoadShape.new("bad_action", Action="normalize"), AttributeError, "read-only"),
        "Like": expected_error(lambda: ctx.LoadShape.new("bad_like", Like="s2"), AttributeError, "read-only"),
        "Npts": expected_error(lambda: source.Npts, AttributeError, "no attribute 'Npts'"),
        "Stepsize": expected_error(lambda: ctx.Solution.Stepsize, AttributeError, "no attribute 'Stepsize'"),
    }
    return {"normalize": {"before": before, "after_default_base": default_base, "explicit_bases": bases},
            "text_mult_alias": source.PMult.tolist(),
            "like": {"npts": copy.NPts, "pmult": copy.PMult.tolist(), "qmult": copy.QMult.tolist(),
                     "text_copy_agrees": True},
            "keyword_errors": errors}


def check_stepping():
    python_readings = run_path(str(EXAMPLES / "daily_steps.py"))["solve_profile"]()
    ctx = altdss.NewContext()
    ctx.Commands((EXAMPLES / "daily_monitor.dss").read_text(encoding="utf-8"))
    monitor = ctx.Monitor["load_power"]
    samples = monitor.AsMatrix()
    equal(len(samples), 3, "DSS monitor sample count")
    equal(ctx.Load["demo"].Daily.FullName(), "LoadShape.daily_demo", "DSS daily name binding")
    equal(ctx.Solution.Converged, True, "DSS example converged")
    dss_readings = []
    p_columns = [index + 2 for index, label in enumerate(monitor.Header()) if label.startswith("P")]
    equal(len(p_columns), ctx.Load["demo"].NumConductors(), "DSS monitor power channels")
    for hour, (record, expected_kw) in enumerate(zip(samples, (50, 100, 150), strict=True), start=1):
        equal((record[0], record[1]), (hour, 0), "DSS monitor hour and seconds")
        kw = sum(float(record[column]) for column in p_columns)
        near(kw, expected_kw, "DSS monitor load kW")
        dss_readings.append({"hour": int(record[0]), "load_kw": kw})

    ctx = circuit()
    load = add_load(ctx)
    count = ctx.NumCircuitElements
    shape = ctx.LoadShape.new("daily24", NPts=24, PMult=[0.5] + [1.0] * 22 + [1.5])
    load.edit(Daily=shape)
    equal(load.Daily, shape, "Load.Daily accepts a shape object")
    equal(ctx.NumCircuitElements, count, "The data shape does not increase circuit element count")
    shape_names = [entry.Name for entry in ctx.LoadShape]
    equal(shape_names, ["default", "daily24"], "Built-in and authored shape names")
    configure_daily(ctx.Solution, 24)
    start_hour = ctx.Solution.Hour
    ctx.Solution.Solve()
    equal((start_hour, ctx.Solution.Hour, ctx.Solution.Converged), (0, 24, True), "Number=24 runs 24 steps")
    kw = float(sum(load.TotalPowers()).real)
    near(kw, 150, "Full-day solve stops on the final multiplier")
    return {"python_by_name": python_readings, "dss_text_by_name": dss_readings,
            "alt_dss_by_object": load.Daily.FullName(), "shape_names": shape_names,
            "circuit_elements_before_and_after": [count, ctx.NumCircuitElements],
            "number_24": {"start_hour": int(start_hour), "after_one_solve": int(ctx.Solution.Hour), "load_kw": kw}}


def check_use_actual():
    ctx = circuit()
    load = add_load(ctx)
    shape = ctx.LoadShape.new("actual", NPts=3, Interval=1.0, PMult=[50, 90, 65],
                              QMult=[10, 30, 45], UseActual=True, PBase=200, QBase=100)
    load.edit(Daily=shape)
    equal((load.kW, load.kvar, shape.PMax, shape.QMax), (90, 30, 90, 30), "Actual shape uses Q at the P peak")
    configure_daily(ctx.Solution, 1)
    ctx.Solution.Solve()
    power = sum(load.TotalPowers())
    equal((ctx.Solution.Converged, ctx.Solution.Hour), (True, 1), "Actual first step")
    near(power.real, 50, "Actual active sample")
    near(power.imag, 10, "Actual reactive sample")
    return {"bases_kw_kvar": [shape.PBase, shape.QBase], "assigned_nominal_kw_kvar": [load.kW, load.kvar],
            "first_hour": int(ctx.Solution.Hour), "first_step_kw_kvar": [float(power.real), float(power.imag)]}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    defaults, empty_error = defaults_and_empty_statistics()
    lengths, growth = check_lengths()
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": defaults,
        "empty_shape_csvfile": empty_error,
        "length_contract": lengths,
        "npts_growth": growth,
        "interval_units": check_intervals(),
        "actions_and_alias": check_actions_and_alias(),
        "stepping": check_stepping(),
        "use_actual": check_use_actual(),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
