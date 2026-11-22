# Configure a LoadShape and sample a daily solve

Create the circuit, then define the shape. A fresh circuit comes with `LoadShape.default`. The shape you add appears in `ctx.LoadShape` and leaves `NumCircuitElements` unchanged. [LoadShape catalog](../../opendss_altdss_library/references/loadshapes/loadshape_properties.json) · [Circuit defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/Circuit.pas#L536-L541)

Set `NPts` before the sample arrays. The typed Python setters require exactly that many values for each array you supply. A write before sizing, a short write, or a long write raises `#20200425` on the pinned stack. `Npts` raises `AttributeError`. DSS text uses `npts` and accepts `mult` as an alias for `PMult`. To increase the number of points on a populated shape, create a replacement with the new count and reassign the load. An `NPts` write by itself changes the count while the existing arrays retain their allocated size. [Wrapper property surface](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/LoadShape.py#L414-L436) · [Typed size guard](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/DSSObjectHelper.pas#L3489-L3518) · [Point count and buffer access](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L338-L379)

Choose one interval field. `Interval` is in hours, `SInterval` in seconds, and `MInterval` in minutes. All three change the same setting. For example, `SInterval=1800` reads back as `Interval=0.5` and `MInterval=30`. With variable intervals, set `Interval=0` and provide one ascending `Hour` time per sample. A typed Python `Hour` write leaves the interval as configured. In DSS text, writing `Hour=(...)` switches to variable intervals. [Interval fields](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L434-L447) · [DSS text time setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L772-L783)

Assign a shape object or its name to `Load.Daily`. DSS text uses `daily=shape_name`. `LoadShapeClass` is a solver enum with `none`, `Daily`, `Yearly`, and `Duty` members. The `Load.Daily` property is an object reference. [Load.Daily binding](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Load.py#L256-L280) · [LoadShapeClass enum](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/enums.py#L194-L199)

In the example below, `UseActual=False` scales the load's nominal power. Leaving `QMult` unset uses the active multiplier for reactive power too. With `UseActual=True`, the samples specify kW and kvar directly, and assigning the shape can change the load's nominal rating. `PBase` and `QBase` provide divisors for `shape.Action(LoadShapeAction.Normalize)` when positive. With zero bases, the action divides each array by its largest absolute sample and clears `UseActual`. `PMax` is the active peak and `QMax` records the reactive sample at that point unless explicitly set. [Actual power application](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1108-L1126) · [Normalization](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L1620-L1692) · [Peak fields](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L2044-L2079)

## Read one result per hour

Start from a circuit with a load and select Daily mode before setting the clock and step settings. With a one-hour step starting at zero, the first solved sample reports `Solution.Hour == 1` and uses index 0 of `PMult`. Set `Number=1` and read results immediately after each solve. `Number=24` advances through all 24 steps in one call. Use the exact spelling `StepSize` and supply seconds in Python. [Daily solve loop](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/SolutionAlgs.pas#L160-L204) · [Python solver settings](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Solution.py#L312-L370)

~~~python
from dss.enums import SolveModes

shape = ctx.LoadShape.new("profile", NPts=3, Interval=1.0, UseActual=False, PMult=[0.5, 1.0, 1.5])
load.edit(Daily=shape)
solution = ctx.Solution
solution.Mode = SolveModes.Daily
solution.StepSize = 3600
solution.Number = 1
solution.Hour = 0
solution.Seconds = 0
for expected_hour in range(1, shape.NPts + 1):
    solution.Solve()
    if not solution.Converged or solution.Hour != expected_hour:
        raise RuntimeError(f"Daily solve failed at hour {expected_hour}")
    print(int(solution.Hour), sum(load.TotalPowers()).real)
~~~

The standalone examples assert hours 1, 2 and 3 at 50, 100 and 150 kW. The Python example checks each result directly. The DSS example captures hourly power in a monitor and the dedicated runner checks the recorded hour and summed kW. [Python example](../../opendss_altdss_library/examples/loadshape/daily_steps.py) · [DSS example](../../opendss_altdss_library/examples/loadshape/daily_monitor.dss) · [Readback matrix](../audits/phase4_loadshape_readback.json)

## Read defaults and use actions

Call `shape.Like(name)` to copy the point count and data. Call `shape.Action(...)` for normalization or a binary save. Passing `Like` or `Action` in Python constructor keywords raises `AttributeError`. [AltDSS LoadShape actions](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/LoadShape.py#L193-L216) · [AltDSS Like method](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/LoadShape.py#L403-L411)

Read `Mean` and `StdDev` after defining samples. On an empty shape the pinned Python getters returned zero and left `#61107` pending. The next checked call, such as a `CSVFile` read, can surface that error. A fresh `CSVFile` read returns an empty string. [Engine statistics guard](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L1607-L1618) · [Lazy statistics getters](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LoadShape.pas#L1694-L1754)
