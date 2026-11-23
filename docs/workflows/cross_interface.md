# Compare snapshot readbacks across Python interfaces

AltDSS-Python 0.2.4, DSS-Python 0.15.7, and OpenDSSDirect.py 0.9.4 all use DSS C-API 0.14.5 in this project. OpenDSSDirect.py pins DSS-Python 0.15.7. A pass demonstrates wrapper agreement only. Independent numerical validation requires a separate reference. Run the fixture harness separately to check the recorded goldens. [OpenDSSDirect.py dependency](https://github.com/dss-extensions/OpenDSSDirect.py/blob/v0.9.4/pyproject.toml#L24-L30) · [DSS-Python backend pin](https://github.com/dss-extensions/DSS-Python/blob/0.15.7/pyproject.toml#L25-L29) · [Fixture validation design](../phase_4/README.md#1-stop-gate)

## Run both snapshot fixtures

Use the environment installed from `opendss_altdss_library/tools/requirements-validation.txt` and run from the repository root.

~~~powershell
python -B opendss_altdss_library/tools/compare_interfaces.py --report cross-interface-report.json
python -B opendss_altdss_library/tools/compare_interfaces.py --fixture ieee13
python -B opendss_altdss_library/tools/run_fixtures.py
~~~

The comparison verifies the input checksums and starts one subprocess per fixture and interface, each with a copy of the same redirect tree. The default DSS-Python and OpenDSSDirect.py contexts can share active circuit state in one process. A new AltDSS context has its own circuit, and `from dss import dss` and `from opendssdirect import dss` bind the same Python name unless aliased. Each worker selects one API and performs its circuit work within that process. Each worker asserts the required engine release, and the report compares the full engine build identification line. [Comparison tool](../../opendss_altdss_library/tools/compare_interfaces.py) · [Committed report](../audits/phase4_cross_interface_report.json)

## Use the accessor for the pinned interface

In the table, `ctx = altdss.NewContext()`, `ac = dss.ActiveCircuit`, and `odd` is imported with `from opendssdirect import dss as odd`.

| Task | AltDSS-Python | DSS-Python | OpenDSSDirect.py |
| --- | --- | --- | --- |
| Submit DSS text | `ctx.Commands(command)` | `dss.Text.Command = command` | `odd.Text.Command(command)` |
| Read text result | `ctx.TextResult` | `dss.Text.Result` | `odd.Text.Result()` |
| Solve | `ctx.Solution.Solve()` | `ac.Solution.Solve()` | `odd.Solution.Solve()` |
| Set solver tolerance | `ctx.Solution.Tolerance = tol` | `ac.Solution.Tolerance = tol` | `odd.Solution.Convergence(tol)` |
| Read total iterations | `ctx.Solution.TotalIterations` | `ac.Solution.Totaliterations` | `odd.Solution.TotalIterations()` |
| Read source power and circuit losses | `ctx.TotalPower()`, `ctx.Losses()` | `ac.TotalPower`, `ac.Losses` | `odd.Circuit.TotalPower()`, `odd.Circuit.Losses()` |
| Count circuit elements | `ctx.NumCircuitElements` | `ac.NumCktElements` | `odd.Circuit.NumCktElements()` |
| Enumerate elements | `[e.FullName() for e in ctx.Element]` | `ac.AllElementNames` | `odd.Circuit.AllElementNames()` |
| Read a selected bus | `bus.Nodes`, `bus.puVMagAngle` | `ac.SetActiveBus(name)`, then `ac.ActiveBus.Nodes`, `ac.ActiveBus.puVmagAngle` | `odd.Circuit.SetActiveBus(name)`, then `odd.Bus.Nodes()`, `odd.Bus.puVmagAngle()` |

Classic DSS-Python readbacks in the table are properties. OpenDSSDirect.py uses methods for the corresponding reads. `dss.Text.Commands(...)` also accepts a command block. The same property-versus-method distinction applies to `ac.ActiveClass.First` and `odd.ActiveClass.First()`. The tool takes the full element name from the enumeration before selecting each element. [Pinned accessor catalog](../../opendss_altdss_library/references/python_interface_comparison.json)

Read `reg.TapNum` on each AltDSS object. Use `? RegControl.<name>.TapNum` and parse the text result with either classic interface. The OpenDSSDirect.py active-class probe returned 9, 9, and 9 through `RegControls.TapNumber()` while the named queries returned 9, 6, and 9. `TapNumber` uses the active control. Passing one argument to the OpenDSSDirect.py method sets its tap. [AltDSS TapNum](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/RegControl.py#L510-L521) · [DSS-Python TapNumber](https://github.com/dss-extensions/DSS-Python/blob/0.15.7/dss/IRegControls.py#L251-L265) · [OpenDSSDirect.py TapNumber](https://github.com/dss-extensions/OpenDSSDirect.py/blob/v0.9.4/opendssdirect/RegControls.py#L267-L279)

## Interpret the comparison

Normalize AltDSS complex powers and the classic arrays and lists to kW/kvar pairs. `TotalPower` and `TotalPowers` already use kW/kvar. `Losses` uses W/var, so the tool multiplies both components by 0.001. The `verify_loss_scale` magnitude heuristic checks whether the normalized active loss is below the magnitude of source kW on these fixtures. The unit conversion follows the accessor contracts. [DSS-Python circuit accessors](https://github.com/dss-extensions/DSS-Python/blob/0.15.7/dss/ICircuit.py#L521-L606)

Bus and element names are matched case-insensitively. Each bus retains the actual node number sequence and its corresponding per-unit magnitudes and angles in degrees. For example, bus 611 has one node, numbered 3. Terminal powers retain their terminal order within each element. Node numbers, iteration counts, regulator taps, and capacitor states compare exactly. Floating-point readbacks use the fixture voltage, angle and power tolerances. [Phase 4 tolerances](../phase_4/README.md#6-tolerances)

The committed report is a result summary with versions, solver settings, totals, controls, and pairwise deltas. Use the fixture goldens for complete bus and element snapshots. Each report pair names the reference and candidate. `total_deltas` gives candidate minus reference for every circuit total. `nonzero_deltas` identifies the path and values for any nonzero numeric delta, including those inside tolerance. `diffs` contains out-of-tolerance values and structural discrepancies. A nonconverged worker, pin mismatch, or failed pair makes the tool exit nonzero. [Comparison report](../audits/phase4_cross_interface_report.json) · [Golden result format](../phase_4/README.md#5-golden-result-format)

The IEEE 13 example is a small driver that asserts agreement by requiring a successful tool exit. The accessor table above explains the interface calls. [IEEE 13 driver](../../opendss_altdss_library/examples/interfaces/compare_ieee13.py)
