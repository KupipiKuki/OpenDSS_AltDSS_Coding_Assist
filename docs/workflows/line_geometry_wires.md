# Model a line from conductor data and positions

This package targets AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API 0.14.5. Both examples use illustrative conductor data and build the same two overhead lines. They solve in an isolated circuit and read back three phases and a length of 1 km per line. [Python example](../../opendss_altdss_library/examples/line_geometry/geometry_and_spacing.py) · [DSS example](../../opendss_altdss_library/examples/line_geometry/geometry_and_spacing.dss) · [Runtime readback](../audits/phase3b_line_geometry_wires_readback.json)

## Choose the construction path

| Path | Creation order | Reduction |
|---|---|---|
| Reusable geometry | Define conductor data. Create `LineGeometry` with `NConds` and `NPhases` before adding conductor references. Supply positions directly or assign a matching `LineSpacing`. Assign `Line.Geometry`, then set the Line length and units. | Set `Reduce=True` or DSS `Reduce=Yes` to remove additional conductors from the matrix through Kron reduction. Put the retained phases before neutrals. |
| Direct spacing | Define conductor data and `LineSpacing`. Set `Line.Spacing` before `Line.Conductors` in Python or `Line.Wires` in DSS text. Set length and units after the construction properties. | The engine builds temporary geometry and enables reduction when the spacing has more conductors than phases. Both examples use four conductor positions and retain three phases. |

The examples use `LineGeometry.Spacing` to copy both coordinate arrays and the unit from a spacing object with matching `NConds`. For positions defined directly in DSS text, set `Cond` for each slot and supply its conductor, `X`, `H`, and units. The pinned engine starts a new geometry with zero slots, so set `NConds` explicitly. [Geometry catalog](../../opendss_altdss_library/references/lines/line_geometry_wires_properties.json) · [Pinned geometry source](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineGeometry.pas#L385-L478) · [Spacing reduction](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineGeometry.pas#L984-L1018)

## Choose the conductor data

- **Overhead.** Create `WireData`. In Python pass the ordered list of `WireData` objects to `Conductors`. In DSS text use `Wires=[...]` with the previously defined wire names.
- **Concentric neutral or tape shield cable.** Create `CNData` or `TSData` with the shared conductor and insulation values plus the strand or shield values. In Python, pass the typed cable objects in the `Conductors` list after assigning `Spacing`. For DSS text, use the construction-specific `CNCables` or `TSCables` entries for phase cables. The engine backs these entries and `Wires` with shared conductor storage. The runtime probe exercised separate CNData and TSData spacing lines. [Conductor storage](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L325-L342) · [Pinned Python setter](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Line.py#L484-L512)

## Set units and property order

1. **Conductor data.** Use `RUnits` for the length denominator of resistance, `GMRUnits` for GMR, and `RadUnits` for physical radii and cable dimensions. Specify the units explicitly. Review the catalog before relying on derived values. For example, when RAC is unset, assigning RDC derives RAC as 1.02 times RDC in this engine. [Conductor setters](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/ConductorData.pas#L220-L259) · [Cable units](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineGeometry.pas#L927-L963)
2. **Positions.** Set `NConds` before the coordinate arrays and units. Changing `LineSpacing.NConds` resets its coordinate units to feet. Use `LineSpacing.Units` or the per-conductor input to establish the geometry's units. The pinned Python `LineGeometry.Units` accessor can raise `ValueError` on this array-backed engine field. [Spacing setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineSpacing.pas#L160-L173) · [Geometry field](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineGeometry.pas#L301-L305)
3. **Line length.** Set the Line's length units independently of coordinate units. The example positions are in metres and the line lengths are in kilometres.
4. **Impedance selection.** Assigning `Line.Geometry` clears the prior LineCode and spacing definition. Assigning `Line.Spacing` clears the prior LineCode and geometry. Direct sequence or matrix edits replace the construction-based definition. Avoid mixing definitions in one creation call unless the replacement is intentional. [Setter paths](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L637-L737) · [Construction selection](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L1838-L1903)
5. **Frequency and earth resistivity.** Geometry constants are calculated at the solution frequency. A `rho` edit propagates to the attached geometry, but the pinned engine can reuse its matrix at the same frequency. The probe changed `rho` from 100 to 1,000 ohm metres at 60 Hz and observed the resistance matrix change only after solving at 50 Hz. Rebuild or verify the matrix when a study depends on a same-frequency earth resistivity change. [Rho setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L764-L771) · [Frequency cache](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L1905-L1938) · [Probe results](../audits/phase3b_line_geometry_wires_readback.json)

## Reproduce the readbacks

Run from the repository root with the pinned validation environment active.

```powershell
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_line_geometry_wires.py
```

The second command prints the constructor matrix and verifies the overhead, cable, and setter probes. [Example catalog](../../opendss_altdss_library/references/examples.json) · [Source index](../../opendss_altdss_library/references/sources.json)
