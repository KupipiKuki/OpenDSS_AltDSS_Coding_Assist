# Create and inspect Line and LineCode

These workflows target AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. Each example defines a three-phase main line and two laterals that share one LineCode. The inputs are illustrative. The examples build and inspect objects without solving the circuit.

Both files are recorded as `Observed-working`: they ran through `opendss_altdss_library/tools/run_examples.py` on 2026-11-21 in the pinned environment (Windows 11 AMD64, Python 3.14.6, AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5). The independent QA/QC review ran separate focused creation and readback checks. [Example catalog](../../opendss_altdss_library/references/examples.json) · [QA/QC runtime evidence](../audits/line_linecode_phase2_qaqc.md#runtime-result-pass)

## AltDSS-Python object and batch workflow

1. Start an isolated engine context with `altdss.NewContext()` and create a circuit in it.
2. Define the impedance and units once with `ctx.LineCode.new()`. The example supplies the positive and zero sequence resistance, reactance, and capacitance explicitly.
3. Build a single line with `ctx.Line.new()`. Pass the previously created LineCode, both buses, and explicit length and units.
4. Use `ctx.Line.batch_new(names=..., **properties)` when creating several lines with a common property layout. Pass a shared LineCode and shared units as scalars. Align the bus lists and lengths with the order of `names`. Use `new()` for elements that need different definitions or property order.

Install the pinned stack in a virtual environment. From the repository root, run the example with that environment's Python:

```powershell
python -m pip install altdss==0.2.4 dss-python==0.15.7 dss-python-backend==0.14.5
python opendss_altdss_library/examples/line_linecode/altdss_lines.py
```

Expected readback includes `C1=3.4` and `C0=1.6` nF/km, the main length of 1.0 km, and lateral lengths of 0.25 and 0.40 km in batch order. [Python example](../../opendss_altdss_library/examples/line_linecode/altdss_lines.py) · [Context and text API](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/AltDSS.py#L367-L413) · [Batch input types](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Line.py#L1404-L1426)

## DSS text workflow

Emit `New Circuit` for a standalone model, then `New LineCode` before the `New Line` commands that reference it. Use text property names from the catalog. This sequence is useful when the deliverable is a reviewable DSS script.

Run the file in a fresh DSS context. To run the text through the same pinned engine from the repository root, use:

```python
from pathlib import Path
from altdss import altdss

ctx = altdss.NewContext()
script = Path("opendss_altdss_library/examples/line_linecode/lines.dss")
ctx.Commands(script.read_text(encoding="utf-8"))

print(ctx.Line["main"].Length)
print(ctx.Line["lateral_a"].Length, ctx.Line["lateral_b"].Length)
```

Expected lengths are 1.0, 0.25, and 0.40 km. For an existing circuit, use a separate component script with the LineCode and Line commands and apply it to the intended active circuit. [DSS text example](../../opendss_altdss_library/examples/line_linecode/lines.dss) · [EPRI scripting reference](https://opendss.epri.com/BasicsoftheOpenDSSScriptingLangu.html)

## Property order and units

| When | Use this pattern |
| --- | --- |
| Reusing an impedance definition | Create the LineCode first. Apply it before any deliberate overrides on the Line. |
| Defining impedance directly | Choose one complete specification from the catalog for sequence values, matrices, or geometry. Some setters replace previous impedance definitions. |
| Using a spacing definition | Create the spacing and conductor definitions first. Set `Spacing` before `Wires` in DSS text or `Conductors` in AltDSS-Python. |
| Modeling a switch | Set `Switch` before any intended impedance, length, or units overrides. The pinned setter changes those values. |
| Specifying units | Declare LineCode impedance per unit length and the Line length unit. In these examples, both use km and capacitance is in nF/km. |

[Line/LineCode property catalog](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties.json) · [Source and release index](../../opendss_altdss_library/references/line_linecode_sources.json) · [Pinned Line engine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas)
