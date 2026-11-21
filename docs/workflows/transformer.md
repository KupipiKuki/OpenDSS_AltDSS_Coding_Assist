# Transformer and XfmrCode workflows

Use these workflows for two- and three-winding models on AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. [Property catalog](../../opendss_altdss_library/references/transformers/transformer_properties.json) · [Runtime matrix](../audits/phase3b_transformer_readback.json)

## Set dimensions before winding data

1. Create the circuit. Set `Phases` and `Windings`, or assign an `XfmrCode` that supplies them.
2. Set `Buses` with one entry and the appropriate node order for each winding. A Transformer has one terminal per winding and `Phases + 1` conductors per terminal. The three-phase wye examples explicitly connect the fourth conductor to ground using node `0`.
3. Set any needed winding overrides in winding order. Use `Conns`, `kVs`, `kVAs`, `Taps`, and `pctR` in Python. `Conns` reads back as `Connection` members. For three-phase windings supply line-to-line kV.
4. Supply one impedance family. Set any explicit `NormHkVA` and `EmergHkVA` after winding kVA. A `kVAs` edit or DSS winding-1 `kVA` edit sets these ratings to 1.1 and 1.5 times winding-1 kVA.

A `Windings` write initializes the winding records again. In the two-to-three winding probe the first two bus names survived and the engine generated the third. The winding kV, kVA, connections, taps and resistance reset. Bus names are stored in lowercase. A four-name `Buses` array for two windings raises error `#20200424`. [Engine winding and rating updates](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L618-L705)

## Choose array or selected-winding access

In Python, pass all winding values together. In DSS text, use `wdg` to select a 1-based winding before using `bus`, `conn`, `kV`, `kVA`, `tap`, `%R`, `RNeut`, or `XNeut`. `XfmrCode` supports the same selection for winding data, while the Transformer owns the bus connections. The text array form for winding resistance is `%Rs`. [Python winding properties](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Transformer.py#L889-L939) · [DSS winding properties](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L450-L542)

```dss
Edit Transformer.stepdown wdg=2 bus=secondary.1.2.3.0 kV=4.16
? Transformer.stepdown.wdg
? Transformer.stepdown.bus
? Transformer.stepdown.kV
```

## Reuse a winding and impedance definition

Define `XfmrCode` before the Transformer. Assign it first and then set `Buses` and local overrides. Assignment copies the code's data. Reassign the code to bring later code edits into an existing transformer. Apply local overrides again after reassignment if they overlap copied fields. [Engine code-copy routine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L2040-L2098) · [Runnable DSS example](../../opendss_altdss_library/examples/transformer/three_winding_code.dss)

## Set impedance, losses, and taps

- Use either scalar reactances `XHL`/`X12`, `XHT`/`X13`, and `XLT`/`X23`, or `XSCArray`. Array order is `[X12]` for two windings and `[X12, X13, X23]` for three. Values are percent on winding-1 kVA. The engine stores 7% as 0.07 per unit.
- Set the intended impedance explicitly after sizing. A fresh Transformer reads `XSCArray=[7]`. On resize to three windings, it reads `[7, 30, 30]` even though scalar `X13` reads 35. A bare XfmrCode reads `[0]` and reaches `[0, 30, 30]` after resizing. Scalar reactance edits rebuild the pair array. Writing the array directly updates its pair data and leaves the scalar readbacks intact. Editing a scalar afterward rebuilds the array from the scalar fields. [Transformer array update](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L963-L978) · [XfmrCode array initialization and update](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/XfmrCode.pas#L473-L571)
- Set `pctR` or `pctRs` in percent. The engine stores 0.2% as 0.002 per unit. Writing `pctLoadLoss=1` sets the first two winding resistances to 0.5% each. A resistance write recomputes the loss from those two windings. [Resistance scale](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L482-L493) · [Loss updates](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L679-L703)
- Python `Taps` and DSS `tap` store the requested per-unit value directly. The probe stored 1.5 with `MaxTap=1.1`. Choose tap values within the configured limits for the intended model. The separate tap-control path clamps to `MinTap` and `MaxTap` and derives step size using `NumTaps`. [Tap recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L952-L961) · [Tap-control setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L1391-L1426)
- Transformer derives unspecified `RDCOhms` from `abs(0.85 × Rpu) × VBase² / VABase`, using the winding voltage base and winding-1 VA. In the pinned probe an array edit only preserved the second value after recalculation. Set and verify each explicit winding value through DSS text, for example `Edit Transformer.stepdown wdg=1 RDCOhms=0.5 wdg=2 RDCOhms=0.6`. [Explicit resistance flag](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L704-L709) · [DC resistance recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L980-L1010)

## Inspect solved winding results

- `WindingCurrents()` returns complex amperes, grouped by phase and then by winding, with two entries per winding. The three-phase, two-winding probe returned 12 values and read all zeros before the solve. DSS `? Transformer.stepdown.WdgCurrents` gives a magnitude/angle text result.
- `WindingVoltages(winding)` uses a 1-based winding number and returns one complex voltage per phase. The winding-current and winding-voltage methods can give incorrect results when terminals are open.
- `LossesByType()` returns total, load and no-load losses in that order. The values are complex VA. [Result methods and open-terminal caveat](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/TransformerExtras.py#L7-L29) · [C-API results](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/CAPI/CAPI_Alt.pas#L1623-L1655) · [Runnable Python example](../../opendss_altdss_library/examples/transformer/two_winding.py)

## Winding count limits

Use only 2 or 3 windings. A direct Python `Windings = 1` followed by an immediate read showed the prior value of 2. The checked `edit(Windings=1)` path raised `#2020031` and also left the value at 2. The architect reported a segmentation fault with exit 139 after the sequence `Windings = 1` followed by `Windings = 4`, reproduced twice on Windows 11, Python 3.14.6, and backend 0.14.5. The runtime matrix exercises only the single invalid write of 1. AutoTrans requires a separate scope decision. [Engine winding declaration](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L162-L187) · [Architect coder handoff](../handoffs/Phase_3B_Transformer_Coder_handoff.md)
