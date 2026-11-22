"""Solve a standalone load one hour at a time and verify its profile."""
from math import isclose

from altdss import altdss
from dss.enums import SolveModes


def solve_profile():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.loadshape_python BasekV=12.47 Bus1=source")
    shape = ctx.LoadShape.new("daily_demo", NPts=3, Interval=1.0, UseActual=False, PMult=[0.5, 1.0, 1.5])
    ctx.Commands("New Load.demo Bus1=source.1.2.3.0 Phases=3 Conn=wye kV=12.47 kW=100 PF=0.95")
    load = ctx.Load["demo"]
    load.edit(Daily=shape.Name)
    if load.Daily != shape:
        raise RuntimeError("Daily shape name did not resolve to the expected object")

    solution = ctx.Solution
    solution.Mode = SolveModes.Daily
    solution.StepSize = 3600
    solution.Number = 1
    solution.Hour = 0
    solution.Seconds = 0
    readings = []
    for hour, expected_kw in enumerate((50, 100, 150), start=1):
        solution.Solve()
        kw = float(sum(load.TotalPowers()).real)
        if not solution.Converged or solution.Hour != hour or not isclose(kw, expected_kw, abs_tol=0.001):
            raise RuntimeError(f"Expected hour {hour} at {expected_kw} kW, got hour {solution.Hour} at {kw} kW")
        readings.append({"hour": int(solution.Hour), "load_kw": kw})
    return readings


if __name__ == "__main__":
    for reading in solve_profile():
        print(f"Hour {reading['hour']}: {reading['load_kw']:.3f} kW")
