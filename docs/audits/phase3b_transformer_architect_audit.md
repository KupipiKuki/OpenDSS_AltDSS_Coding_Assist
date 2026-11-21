# Phase 3B Package 3 Architect/Auditor Review

- **Date** 2026-11-21
- **Reviewer role** Architect/auditor (DeepSeek), independent of the coder (GPT-6.2 Sol) and of the QA/QC reviewer (Mistral 4)
- **Reviewed branch** `wp/phase3`
- **Package revision** `a7b485d` (Transformer and XfmrCode package); QA handoff pin `04463b8`; QA report `4605787`
- **Baseline** `30103e6`
- **Reviewed working tree** clean; one auditor correction applied (E-1, five citation spans in the Transformer catalog), recorded with this audit
- **Targets** AltDSS-Python 0.2.4 (tag commit `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee`), DSS-Python 0.15.7, DSS C-API backend 0.14.5 (tag commit `87d85c2622c8281b92255335bc7c09b11191b21d`)
- **Review environment** fresh venv from `tools/requirements-validation.txt`; Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, `jsonschema` 4.26.0
- **Sources inspected** wrapper `Transformer.py`, `TransformerExtras.py`, `XfmrCode.py` from the pinned 0.2.4 install; engine `Transformer.pas`, `XfmrCode.pas`, `CktElement.pas`, `CktElementClass.pas`, `PDElement.pas`, `PDClass.pas`, `CAPI_Alt.pas` and the other files the catalogs cite, at tag `0.14.5`; EPRI `Transformer1`, `Properties16`, `Transformer`, `XfmrCode`, and `AutoTrans` pages

[Property catalog](../../opendss_altdss_library/references/transformers/transformer_properties.json) · [Workflow](../workflows/transformer.md) · [Build audit](phase3b_transformer_audit.md) · [QA/QC report](phase3b_transformer_qaqc.md) · [Readback matrix](phase3b_transformer_readback.json) · [Coder handoff](../handoffs/Phase_3B_Transformer_Coder_handoff.md)

## STATUS: PASS

No blocking findings. One correction was required and is applied: five rows cited a `PDClass.pas` range that runs six lines past the end of the file (E-1). One non-blocking observation concerns how the harness records the `Windings = 1` error (E-2). With E-1 applied, the package meets the element-package definition of done in plan §5.4 items 1–7 and is ready for owner disposition before Phase 3B package 4.

Source review and runtime execution are reported separately; neither substitutes for the other.

## Independent verification performed

| Check | Method | Result |
| --- | --- | --- |
| Schema pairs | `tools/validate_catalogs.py` | PASS 12/12, exit 0 (re-run after E-1) |
| Example execution | `tools/run_examples.py` | PASS 8/8, exit 0, environment block matches pins |
| Readback matrix | `tools/readback_transformer.py` compared to the committed JSON | identical except `environment`/date; 104 entries = 85 `read back` + 17 `DSS text readback` + 2 `action` |
| Catalog structure | parse of both element records | Transformer 60 rows (50 keywords + 9 text-only + identifier), XfmrCode 44 rows (35 + 8 + 1); no duplicate names; every row has `source_refs` |
| Wrapper correspondence | `*Properties` TypedDicts parsed from the pinned 0.2.4 install | Transformer 50 keys = 50 keywords, XfmrCode 35 = 35, exact case, nothing missing on either side |
| Engine correspondence | `TTransfProp` (L88-L149, 49 members), `TXfmrCodeProp` (L68-L114, 39 members), winding struct L162-L187 | rows map one-to-one; inherited `CktElement`/`PDElement`/`PDClass` fields attributed to their own files |
| Citation resolution | every anchored reference mapped to a pinned file | 374 references (204 unique), 0 unresolved, 0 mutable refs; **5 out-of-range spans found (E-1), now 0** |
| Defaults | catalog `default_value` compared with every `read back` cell | only null defaults differ from the matrix (derived, generated, or dynamic fields); percent values differ only by float representation (7 vs 7.000000000000001) |
| Baseline preservation | `git diff 30103e6..a7b485d` | zero removed lines in `dss_capi.json` (59→75), `sources.json` (51→67), `examples.json` (6→8); 10 added files, 8 modified, no stray downloads |
| Counts asserted in the build audit | recount | 75 engine records, 67 sources, 8 examples, 104 matrix entries, 14 `pass` / 2 `not-run` additions — all confirmed |
| Link check | 116 relative links across the changed docs | 0 missing targets |

## PROPERTY FINDINGS

None blocking.

- **The winding model is represented correctly.** Per-winding scalars are text-only rows with no `altdss_keyword` (`wdg`, `bus`, `conn`, `kv`, `kva`, `tap`, `%r`, and `rneut_scalar`/`xneut_scalar`), and their descriptions name the DSS keyword and state that the pinned wrapper has no winding-selector accessor. The `_scalar` suffix avoids colliding with the array rows `rneut`/`xneut`, and the descriptions make the pairing explicit.
- **Array rows match the wrapper exactly** for `Buses`, `Conns`, `kVs`, `kVAs`, `Taps`, `pctR`, `RNeut`, `XNeut`, `XSCArray`, `RDCOhms`, `MaxTap`, `MinTap`, `NumTaps`, `Ratings`, and the thermal block. `XfmrCode` correctly omits `Buses`, `Sub`, `SubName`, `Bank`, `XfmrCode`, `XRConst`, `LeadLag`, `Core`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, and `Enabled`.
- **The three result methods are not miscatalogued as properties.** `WindingCurrents()`, `WindingVoltages(winding)`, and `LossesByType()` are documented as methods with the open-terminal caveat, matching `TransformerExtras.py`.
- **Defaults are honest where the constructor literal and the readback differ.** `pctR` 0.2 (0.002 pu), `XHL`/`XHT`/`XLT` 7/35/30 as percent, `RDCOhms` 0.088117 Ω, `NormHkVA`/`EmergHkVA` 1100/1500, generated bus names, and `XSCArray` `[7]` are all stated as readback values with the engine literals cited alongside.
- **`XfmrCode`'s rating shortcut is captured.** The code's `Ratings[0]` starts at 600, not 1100 as for a Transformer; the catalog and matrix both record it.

## EVIDENCE FINDINGS

- **E-1 (found by this review, applied).** Five inherited-rating rows (`normamps`, `emergamps`, `faultrate`, `pctperm`, `repair`) cited `src/PDElements/PDClass.pas#L95-L116`. That file has 110 lines at `0.14.5`, so the last six lines of every such link do not exist. The correct block is `TPDClass.DefineProperties` at **L92-L108**, which registers exactly those five properties at L100-L104. Corrected in the catalog; schema validation re-run (12/12). The QA report's statement that all 374 references are in range did not hold for these five.
- **My coder handoff had the wrong EPRI page, and the coder caught it.** `Transformer.html` is the RegControl property page (eight `RegControl` mentions); the Transformer element page is `Transformer1.html`, with `Properties16.html` as the property-vocabulary page. The package cites the correct pages and keeps `Transformer.html` in the source index as a scope note explaining the mismatch. Recorded in my favour as a correction to the architect's input, not a coder defect.
- **Code claims verified at the pinned tag:** the `Windings` side effect re-initializing each record, regenerating terminals, and reallocating `XSC`/`TermRef`/Y matrices (L630-L665); `GreaterThanOne` on `Windings` (L446-L448); bus length validation through `Buses` (error `#20200424`); tap registration and the separate control setter (L462-L477, L1391-L1426); `pctR`/`pctRs` at scale 0.01 (L482-L493); `pctLoadLoss` rewriting windings 1–2 (L679-L703); `XSCArray` sizing and rebuild (L340-L343, L963-L978); `RDCOhms` derivation (L479-L480, L980-L1010); kVA rating updates (L666-L686, L1016-L1038); code copy (L2040-L2098); `WdgCurrents` as a read-only string property (L345-L366).
- **`tested` is accurate:** 14 `pass` / 2 `not-run`, every `pass` corroborated by the reproduced matrix, and the two `not-run` records are static specification-set facts with a null environment.
- **E-2 (non-blocking observation).** In `check_invalid_windings`, the recorded `edit_error` names `one_direct`, the object that performed the invalid *direct* write, not `one_edit` where the edit was called. The direct write posts error `#2020031` without raising, and the next property write that checks errors surfaces it. I verified separately, in a clean context with no prior direct write, that `edit(Windings=1)` raises `#2020031` naming its own object and leaves the value at 2 — so the documented behavior is correct, but the harness's edit-path evidence is not independent. Fix for a later pass: run the direct-write probe in one context and the edit probe in a fresh one.

## REQUIREMENT FINDINGS

- **The engine specification sets are reproduced exactly.** Transformer declares `XfmrCode` (applied first), `X12, X13, X23, kV`, and `XscArray, kV` (`Transformer.pas` L379-L388); XfmrCode declares `X12, X13, X23` and `XscArray` (`XfmrCode.pas` L214-L220). The catalog's `requirement_groups` match member for member, including the `kV` partner entry and the ordering note for `XfmrCode`.
- **`required_properties` follows the published convention:** Transformer `["name", "buses"]` and XfmrCode `["name", "kvs"]`, matching the engine's `Required` flags (`buses`/`bus`, `kVs`/`kV`) and the Line/Vsource precedent where the list records identity plus model inputs, not the Python signature. Both conditional notes state that `new` can allocate with a name alone.
- **`target_support` gains a `dss_text` key** for both classes. That is a useful, schema-valid addition: these elements genuinely have a text-only surface, and the key names it.
- **No property is claimed that the stack cannot reach,** and the text-only rows carry no Python keyword, so nothing generates an invalid call.

## SCHEMA RESULT

**pass.** `tools/validate_catalogs.py` exits 0 with 12/12 pairs on the reviewed tree, including `references/transformers/transformer_properties.json` (2 records) under the generalized element schema. Re-validated after E-1.

## RUNTIME RESULT

**pass.** Executed by this review in a fresh venv on the pinned stack.

- `run_examples.py`: 8/8 PASS. The two-winding example reports 12 winding-current values, winding-1 voltages, and total = load ≈ 40.035 + j701.612 VA with zero no-load loss; the three-winding `XfmrCode` DSS example converges with three buses.
- `readback_transformer.py`: exit 0; output equals the committed matrix after removing `environment`/date.
- **Independent probes outside the harness** reproduced every load-bearing claim: a 2→3 winding resize reset kV/kVA/conn/tap/pctR and extended `XSCArray` to `[7, 30, 30]` while scalar `X13` stayed 35; `Windings = 1` was ignored (value unchanged) while the checked edit raised `#2020031`; a three-name `Buses` array on a two-winding object raised `#20200424`; `Taps = [1.5, 1.0]` stored 1.5 with `MaxTap` 1.1; `pctLoadLoss = 1.0` moved `pctR` to [0.5, 0.5]; an explicit `XSCArray = [11, 21, 31]` write left the scalar fields intact and a later `XHT = 40` rebuilt the array to `[7, 40, 30]`; `RDCOhms = [0.5, 0.6]` retained only the second value after recalculation, while per-winding `wdg=1/2 RDCOhms` edits persisted both; `XfmrCode` copied at assignment, ignored later code edits, and re-copied on reassignment; conductors per terminal were 4 with 3 terminals on a three-winding three-phase unit.

## Required corrections

| ID | Status | Change | Source |
| --- | --- | --- | --- |
| E-1 | applied in this review | `Transformer.normamps`, `emergamps`, `faultrate`, `pctperm`, `repair`: `PDClass.pas#L95-L116` → `PDClass.pas#L92-L108` | [PDClass.pas](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/PDClass.pas#L92-L108) (file ends at L110) |

No other correction is required.

## Observations (non-blocking)

| ID | Observation | Assessment |
| --- | --- | --- |
| E-2 | The `windings_one` harness entry records the error text from the preceding direct write (`one_direct`) under `edit_error`; the edit path was not independently exercised in that probe. | Behavior is correct and verified separately; harness fix recommended for a later pass (separate contexts for the two probes). |

## Accepted limitations

1. Scope is two- and three-winding models. `Windings` above 3 is unvalidated; the `1` then `4` sequence segfaulted the pinned engine in the architect's preparation (exit 139) and is correctly excluded from the automated harness.
2. `AutoTrans` is deferred with an explicit scope note in the source index and the manifest.
3. Array-versus-scalar quirks (`XSCArray`, `RDCOhms`) are documented with the per-winding DSS workaround.
4. Examples are illustrative single-load solves; multi-source, harmonic, thermal, and Phase 4 feeder fixtures remain out of scope.

## Disposition

The package delivers the two-class catalog, workflow, two executed examples, readback matrix, sixteen engine records, sixteen source records, build audit, and independent QA/QC report that plan §5.4 requires for Transformer and its shared definition. The winding model, percent scaling, specification sets, reset semantics, tap behavior, code-copy semantics, and result methods were re-derived from the pinned sources and re-executed on a clean environment rather than accepted from the coder's or the QA reviewer's report; the one broken citation was found here rather than in QA.

Recommended owner action: accept package 3 and open Phase 3B package 4 (`Load`) on the same template. No coder remediation is outstanding for package 3; E-2 is a harness improvement for a later pass.
