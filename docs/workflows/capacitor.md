# Capacitor workflow

Use this workflow for Capacitor on AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. [Property catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json) · [Runtime matrix](../audits/phase3b_capacitor_readback.json)

## Wire the bank

Set `Phases` and `Conn` before wiring `Bus1` and `Bus2`. For wye, the engine allocates two terminals with one conductor per phase at each terminal. A wye bank without an explicit second bus defaults to the grounded nodes of `Bus1`. To connect an ungrounded neutral, set `Bus2` to an otherwise unused common node on the first bus, such as `primary.4.4.4` in a three-phase model. For a series capacitor, set an explicitly different bus stem in `Bus2` after `Bus1`. [EPRI connection diagrams and examples](https://opendss.epri.com/Capacitor1.html) · [Pinned bus side effects](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L303-L374)

Delta has one terminal. Three-phase delta uses three conductors, and one- or two-phase delta uses one more conductor than its phase count. Changing an existing wye model to delta removes `Bus2`. Changing it back can generate a new second bus. For series models, configure the intended wye connection and both buses together. [Connection allocation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L323-L374)

## Size the steps, then choose a capacitance family

Set `NumSteps` before setting `kvar`, `Cuf`, `R`, `XL`, `Harm`, or `States`. Supply one entry per step. The wrapper reads the first five arrays as float64 and `States` as int32. The pinned engine rejects a short numeric `kvar` or `Cuf` array. A one-step default bank resized to four steps divides the stored 1200 kvar into four 300 kvar entries and turns all four on. In Cuf mode a one-to-many resize copies the original Cuf into each step. Refill the arrays after resizing an already multistep bank. JSON export can omit `NumSteps` while retaining the arrays. [Property registration](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L226-L279) · [Resize behavior](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L387-L459)

| Family | Inputs | Pinned behavior |
|---|---|---|
| Rated reactive power | `kvar`, `kV` | kvar is the three-phase total per step for a three-phase bank. The backend derives every step's capacitance from the first kvar value, while using all stored kvar values to derive amp ratings. |
| Nodal matrix | `CMatrix` | Supply matrix values in µF. Three phases accept six lower-triangle or nine flattened full-matrix values in Python, with a flat nine-value readback. DSS syntax uses rows such as `[c11 | -c21 c22 | -c31 -c32 c33]`. Every step uses the same matrix. |
| Capacitance per step | `Cuf`, `kV` | Supply µF per phase for each step. The solved admittance uses these entries. Stored kvar can remain from the previous family and automatic amp ratings can be near zero. |

For two or three phases, enter line-to-line `kV`. For one phase, give the voltage across the capacitor branch. The last write of `kvar`, `CMatrix`, or `Cuf` selects the family. Both capacitance inputs scale from µF to farads by `1e-6`. Readbacks can retain inactive inputs after switching families, so use a solve to verify the bank. [Specification sets and scales](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L208-L248) · [Family selector](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L375-L386) · [Recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L614-L692)

For unequal electrical steps on this backend, specify `Cuf` and verify each energized step. The two-step probe with `kvar=[100, 200]` supplied about 100 kvar from either step. The probe with `Cuf=[7, 14]` supplied about 411 and 821 kvar. The Cuf rating accumulator uses farads and phase kV with an inconsistent scale. A separate 10 µF bank supplied about 586.56 kvar while its automatic amp ratings were about 0.0000122 and 0.0000163 A. [Derived capacitance and ratings](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L625-L692) · [Admittance calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L924-L978)

For a tuned bank, use `XL` in ohms at base frequency or specify the harmonic order in `Harm`. An `XL` write disables harmonic-derived reactance. A later `Harm` write enables recalculation. On a one-to-many kvar-family resize the engine multiplies nonzero `R` and `XL` by the new count, and harmonic tuning can recalculate `XL` afterward. Verify the final arrays after setting the filter inputs. [Filter-property side effects](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L387-L473) · [Harmonic-derived reactance](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L673-L682)

## Switch steps and read output

Write the full `States` array through DSS text. Use 1 for on and 0 for off. The pinned Python constructor keyword, attribute assignment, and `edit(States=...)` calls kept the existing values in the probes. Read `bank.States` after the text edit and solve again.

```python
ctx.Commands("Edit Capacitor.steps States=[1 0 0 0]")
ctx.Solution.Solve()
for terminal, power in enumerate(ctx.Capacitor["steps"].TotalPowers(), start=1):
    print(terminal, power.real, power.imag)
```

`TotalPowers()` returns one complex value per terminal in kW and kvar. For a grounded-wye shunt, the first terminal has negative Q when the bank supplies reactive power and the grounded terminal has zero power. Preserve the imaginary part when reporting output. The four-step example supplied about 1201.40 kvar with all steps on and 300.09 kvar with one step on. CapControl can switch bank steps through the engine's add and subtract actions. Its settings belong to the separate controller class. [DSS step example](../../opendss_altdss_library/examples/capacitor/stepped_shunt.dss) · [Python power example](../../opendss_altdss_library/examples/capacitor/wye_shunt.py) · [Control coupling](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/CapControl.pas#L725-L788)

## Verify ratings and copied banks

For automatic ratings in the kvar family, the engine uses 135% of rated phase current for `NormAmps` and 180% for `EmergAmps`. The normal factor differs from the wrapper docstring. An explicit normal or emergency rating persists across kvar edits without setting the other rating. Verify or specify ratings explicitly when using the Cuf or CMatrix families. `pctPerm` takes percent and `Repair` takes hours. [Rating calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L684-L692) · [Inherited properties](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/PDClass.pas#L92-L108)

Use DSS `Like=source` or the Python `bank.Like("source")` method for the copy action. The advertised Python creation keyword raised `AttributeError`. The copy probe kept the target buses and two-terminal allocation after copying a delta source. Check the target's bus and terminal layout after copying. [Wrapper copy method](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Capacitor.py#L367-L375) · [Engine copy routine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L503-L544)

Use the current catalog for property names. The pinned wrapper has no `Model`, `Vmin`, `Vmax`, `StepSize`, `Vharmonics`, `PctLead`, `PctLag`, `PtPhase`, `Userated`, or `Spectrum` on Capacitor. Use the full plural `States`. The DSS parser accepted `State` as an abbreviation with array semantics. [Pinned property enum](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L68-L83)
