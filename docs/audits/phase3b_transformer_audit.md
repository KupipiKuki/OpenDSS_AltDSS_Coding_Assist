# Phase 3B Package 3 build audit

- **Date** 2026-11-21
- **Branch** `wp/phase3`
- **Status** Coder validation complete. Independent QA/QC and architect review pending.

## Scope and method

Transformer and XfmrCode cover two- and three-winding models. AutoTrans is a separate class deferred pending an owner scope decision. The example load is a fixture for the transformer solve. Control devices, harmonics, thermal studies and IEEE feeder fixtures are outside this package. [Coder handoff](../handoffs/Phase_3B_Transformer_Coder_handoff.md)

Compared the wrapper TypedDicts and accessors at tag 0.2.4 with property tables, constructor code, edit paths and result entry points at DSS C-API tag 0.14.5. Verified that EPRI's `Transformer.html` documents the RegControl field. The catalog cites the Transformer element page `Transformer1.html` for model concepts and keeps the original URL as a scope note in the source index. Used EPRI documentation for model vocabulary and pinned code and runtime for defaults and edit behavior. [Transformer element](https://opendss.epri.com/Transformer1.html) · [RegControl property](https://opendss.epri.com/Transformer.html) · [XfmrCode](https://opendss.epri.com/XfmrCode.html) · [AutoTrans](https://opendss.epri.com/AutoTrans.html)

Ran the validation environment on Windows 11 AMD64, Python 3.14.6, AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5, and jsonschema 4.26.0. A fresh virtual environment reused matching installed distributions from the prior validation environment via a local path entry. No fresh package download was needed. [Runtime matrix](phase3b_transformer_readback.json) · [Validation requirements](../../opendss_altdss_library/tools/requirements-validation.txt)

## Coverage and results

| Check | Result |
|---|---|
| Transformer property rows | 60 rows. 50 pinned Python keywords, 9 DSS scalar paths, and 1 identifier. |
| XfmrCode property rows | 44 rows. 35 pinned Python keywords, 8 DSS scalar paths, and 1 identifier. |
| Source and engine records | 16 source records and 16 engine records appended. Every property row has a versioned citation. |
| Schema validation | 12 of 12 manifest and catalog pairs passed Draft 2020-12 with format checking. |
| Example harness | 8 of 8 examples passed. Both new examples are recorded as `Observed-working`. |
| Readback matrix | 104 entries with checks on defaults and behavior. The two `Like` entries record action-only access. The 100 kW Python solve returned 12 winding currents and losses of approximately 40.035 + j701.612 VA total and load, with zero no-load loss. The three-winding DSS example converged and supplied the expected wiring and copied impedance. |

The matrix confirms winding record resets, bus retention and lowercasing, bus array length validation, direct tap writes outside the control limits, selected-winding DSS edits, percent loss and resistance updates, both kVA rating update paths, conductors per terminal, XfmrCode copy and reassignment, and loading and result methods. Engine specification sets were source reviewed. [Property catalog](../../opendss_altdss_library/references/transformers/transformer_properties.json) · [Engine catalog](../../opendss_altdss_library/references/dss_capi.json) · [Example catalog](../../opendss_altdss_library/references/examples.json)

## Details for independent QA/QC

- `XSCArray` accepts explicit writes and can be rebuilt by a scalar edit. An explicit array write leaves scalar fields unchanged. A fresh Transformer reads `[7]` and a bare XfmrCode reads `[0]`. Resizing yielded `[7, 30, 30]` and `[0, 30, 30]` respectively while `X13` still read 35. The XfmrCode constructor allocates a zero-filled pair array and initializes its scalar fields independently. [Transformer source](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L633-L695) · [XfmrCode source](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/XfmrCode.pas#L532-L571)
- Transformer readback showed about 0.088117 Ω per winding using the default three-phase wye voltage base. The bare code's winding initialization gives about 0.264352 Ω using line-to-line kV. The array edit `RDCOhms=[0.5,0.6]` retained only the second value after recalculation. With explicit selected-winding DSS edits both values persisted. [Winding initialization](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L1361-L1381) · [Transformer derivation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L980-L1010)
- A single `Windings=1` direct assignment followed by immediate read left 2, and the checked edit reported `#2020031` for both classes. The architect's prior hazard report records that `Windings=1` followed by `Windings=4` crashed twice with segmentation fault and exit 139 on Windows 11, Python 3.14.6, backend 0.14.5. A separate four-winding write alone reportedly returned 4 before further use. The coder did not repeat the four-winding probe. The published scope is two and three windings. [Architect evidence](../handoffs/Phase_3B_Transformer_Coder_handoff.md)
- The result probe used a 100 kW, unity-power-factor load and recorded this model's loss values. Winding currents and voltages were checked with closed terminals. The tap-clamping control path was source reviewed. [Result methods](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/TransformerExtras.py#L7-L29) · [Tap-control setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L1391-L1426)

Independent QA/QC and architect review precede owner disposition. [QA/QC handoff](../handoffs/Phase_3B_Transformer_QAQC_handoff.md)
