# Phase 3B Package 1 Architect/Auditor Review

- **Date** 2026-11-21
- **Reviewer role** Architect/auditor (DeepSeek), independent of the coder (GPT-6.2 Sol) and of the QA/QC reviewer (Mistral 4)
- **Reviewed branch** `wp/phase3`
- **Package revision** `2cd9b33` (LineGeometry, LineSpacing, and conductor data package); QA handoff pin `bdc429b`; QA report `f8738ce`
- **Baseline** `ab444fd`
- **Reviewed working tree** one auditor correction applied on top of `f8738ce` (A-1, two citation spans in `dss_capi.json`), recorded with this audit. No other working-tree changes.
- **Targets** AltDSS-Python 0.2.4 (tag commit `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee`), DSS-Python 0.15.7, DSS C-API backend 0.14.5 (tag commit `87d85c2622c8281b92255335bc7c09b11191b21d`)
- **Review environment** fresh venv from `tools/requirements-validation.txt`; Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, `jsonschema` 4.26.0
- **Sources inspected** wrapper modules `LineGeometry.py`, `LineSpacing.py`, `WireData.py`, `CNData.py`, `TSData.py`, `Line.py` from the pinned 0.2.4 install; engine files `LineGeometry.pas`, `LineSpacing.pas`, `WireData.pas`, `CNData.pas`, `TSData.pas`, `ConductorData.pas`, `CableData.pas`, `Line.pas` fetched at tag `0.14.5`; EPRI `LineGeometry`, `LineSpacing`, `WireData`, `CNData`, and `TSData` pages

[Property catalog](../../opendss_altdss_library/references/lines/line_geometry_wires_properties.json) · [Schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json) · [Build audit](phase3b_line_geometry_wires_audit.md) · [QA/QC report](phase3b_line_geometry_wires_qaqc.md) · [Readback matrix](phase3b_line_geometry_wires_readback.json) · [Workflow](../workflows/line_geometry_wires.md)

## STATUS: PASS

No blocking findings. One optional citation-precision correction (A-1) confirmed independently and applied by this review. The package meets the element-package definition of done in plan §5.4 items 1–7 and is ready for owner disposition before Phase 3B package 2.

Source review and runtime execution are reported separately below; neither substitutes for the other.

## Independent verification performed

| Check | Method | Result |
| --- | --- | --- |
| Schema pairs | `tools/validate_catalogs.py` | PASS 10/10, exit 0 |
| Example execution | `tools/run_examples.py` | PASS 4/4, exit 0, environment block matches pins |
| Readback matrix | `tools/readback_line_geometry_wires.py` compared to the committed JSON | identical except `environment`/date fields: 82 cells = 76 `read back`, 5 `action`, 1 `unavailable` |
| Catalog structure | parse of the five element records | 5 classes, 82 rows, counts 15/7/15/23/22, no duplicate row names, every row has a non-empty `source_refs` |
| Citation resolution | all `source_refs`, element `sources`, and conditional `source_refs` mapped to pinned files | 353 references (184 unique), 0 unresolved, 0 out of range, 0 mutable `master`/`main`/`latest` refs; tags 0.2.4 (92) and 0.14.5 (88) |
| Wrapper correspondence | `*Properties` TypedDict keys extracted from the pinned 0.2.4 install and compared with catalog rows | 14/6/14/22/21 keys; every key cataloged; no uncataloged key; every `altdss_keyword` matches the pinned casing exactly; only alias is `Conductors` → row `wires` |
| Engine correspondence | enum blocks and constructors in the pinned `.pas` files | LineGeometry 19 enum entries (6 object-reference aliases folded into `wires`), LineSpacing 5, TConductorDataProp 13, TCNDataProp 4, TTSDataProp 3; arithmetic 13+4+(4 or 3) reproduces the 23/22 row counts |
| Defaults | constructor blocks and matrix values compared field by field | catalog `default_value` equals every `read back` cell; `null` defaults are exactly the constructor sentinels (`-1.0`, `-2.0`) and the unavailable `LineGeometry.Units` cell |
| Baseline preservation | `git diff ab444fd..2cd9b33` | zero removed lines in `dss_capi.json` (26→45), `sources.json` (18→34), `examples.json` (2→4); 11 added files, 6 modified docs/tools, no stray downloads |
| Link check | 96 relative links across the changed docs | 0 missing targets |
| EPRI availability | HTTP checks | `LineGeometry`, `LineSpacing`, `WireData`, `CNData` return 200; `TSData` returns 404, matching the null `epri_doc_url` |

## PROPERTY FINDINGS

None blocking.

- **Coverage is exact.** Row counts reconcile with the pinned sources: LineGeometry 13 properties + `name` + `like`; LineSpacing 5 + 2; WireData 13 + 2; CNData 4 own + 4 inherited cable + 13 conductor + 2; TSData 3 own + 4 + 13 + 2. Inherited attribution is arithmetically correct against `ConductorData.pas` and `CableData.pas`.
- **Alias folding is acceptable and disclosed.** `TLineGeometryProp` declares 19 entries, of which `Cond`, `Wire`, `CNCable`, `TSCable`, `CNCables`, `TSCables`, and `Wires` share conductor storage (`LineGeometry.pas` L275-L299, L338-L355). The catalog represents them as the single `wires` row with `altdss_keyword: Conductors` and a note listing the DSS text entries; `capi-line-geometry-conductors` records the shared storage and states that individual alias writes were inspected, not executed. This matches the Line/LineCode precedent and the pinned Python keyword set.
- **No duplicates, no unsupported rows.** No row name repeats within a class; `supported_in_target` is never false, which is correct — all five classes are present in 0.2.4. `LineGeometry.Units` is supported for writing and marked `unavailable` for reading, not `unsupported`.
- **Sentinels handled correctly.** `WireData`, `CNData`, and `TSData` rows leave `default_value` null where the engine seeds `-1.0` (`RDC`, `RAC`, `GMRAC`, `Radius`, `NormAmps`, `EmergAmps`, `CapRadius`, `Ratings[0]`) or `-2.0` for the derived `Diam`; the matrix records the raw sentinel and the row descriptions explain the derivation. `LineGeometry` and `LineSpacing` rows carry usable defaults because their constructors initialize real values.

## EVIDENCE FINDINGS

- **Version metadata stays pinned.** `target_versions` records "EPRI online documentation; page version not stated"; element `sources` scope the EPRI entry as "Undated OpenDSS documentation for model concepts." No label implies a current EPRI release, and `TSData` cites no EPRI page because none exists (`404` verified).
- **Types, defaults, and derived values verified against source, not inferred.** Confirmed at `0.14.5`: `RAC = 1.02 × RDC` and the inverse (`ConductorData.pas` L226-L231, reproduced as 0.306 from RDC 0.30); `Radius → CapRadius = Radius` and `Diam → Radius = 0.5 × Diam` via `PropertyScale 1/2` (L242-L260, L205-L209); `GMRStrand = 0.7788 × 0.5 × DiaStrand` (`CNData.pas` L144-L147); `EmergAmps = 1.5 × NormAmps` (L252-L255); `LineGeometry` constructor `NConds=0`, `NPhases=0`, `NormAmps=0`, `EmergAmps=0`, `LineType=1` (OH), `Reduce=FALSE`, `Ratings[0]=0` (L621-L654); `LineSpacing` constructor `NConds=3`, `NPhases=3`, `Units=ft`, zeroed `X`/`H` (L194-L215); `CNData` `k=2`; `CableData` `EpsR=2.3`; `TSData` `TapeLap=20.0`.
- **Range and unit statements are supported.** `TapeLap` 0–100 (`TSData.pas` L129-L134), `k ≥ 2` (`CNData.pas` L150-L152), `EpsR ≥ 1` (`CableData.pas` L136-L138), `NConds` assignment resetting units to feet and reallocating arrays (`LineSpacing.pas` L128-L143, `LineGeometry.pas` L411-L457).
- **`LineGeometry.Units` limitation is stated where a reader will meet it.** The row description names the `ValueError` risk of the scalar enum getter and points to the spacing object or DSS conductor entries; the engine record adds the probe context. Confirmed against `LineGeometry.pas` L301-L305 (`OnArray`) and the 0.2.4 getter (`LineGeometry.py` L164-L177).
- **A-1 (applied, optional).** `capi-cable-data-rows` cited `TCableDataProp … L18-L25` and `capi-ts-data-rows` cited `TTSDataProp … L19-L25`. Both enums close with `);` at L24 and are followed at L25 by the `…PropLegacy` alias, so the exact spans are `L18-L24` and `L19-L24`. Correction applied in `dss_capi.json`; schema validation re-run afterwards (PASS 10/10). Content of both records was already correct.
- **Every other engine range lands on the claimed code.** Verified span by span, including `SetWires` L214-L252, `PropertySideEffects` L399-L478 and L524-L564, `UpdateLineGeometryData`/`LoadSpacingAndWires` L918-L950 and L967-L1018, `PropertyFlags` L311-L365, `Line.pas` L637-L737, L795-L828, L1838-L1903, L1905-L1938. Note for the record: the new engine records place line ranges in `section_or_record` with a bare pinned file URL, whereas the Phase 2 catalog embedded `#L` anchors in the URL. Both resolve to the same pinned content; the style difference is harmless and not a defect.
- **Example evidence is honest.** Both new `examples.json` records are `Observed-working` with a committed file, a harness run, an environment block, and a date; expected results match the observed stdout. The `tested` split of the 19 new engine records is 6 `pass` / 13 `not-run`, and every `pass` claim reproduces in my run; `not-run` records are static source facts with null environment.

## REQUIREMENT FINDINGS

- **Engine specification sets are distinguished from minimum inputs.** `LineGeometry.property_requirements` records the complete coordinate specification sets `[[spacing], [x, h]]` as alternatives against `LineGeometry.pas` L262-L269, while `required_properties` stays the object identifier only. LineSpacing, WireData, CNData, and TSData carry ordered conditional guidance (units, dimension, and derivation prerequisites) rather than a flat required list.
- **Collection mappings and keyword casing confirmed at runtime.** `altdss_mapping` values `altdss.LineGeometry`, `altdss.LineSpacing`, `altdss.WireData`, `altdss.CNData`, `altdss.TSData` match the live `ctx.<Class>.new(...)` calls used by the examples and the readback harness. All keyword casings (`NConds`, `NPhases`, `Conductors`, `X`, `H`, `Units`, `RDC`, `RAC`, `RUnits`, `GMRAC`, `GMRUnits`, `RadUnits`, `NormAmps`, `EmergAmps`, `CapRadius`, `DiaStrand`, `GMRStrand`, `RStrand`, `EpsR`, `InsLayer`, `DiaIns`, `DiaCable`, `DiaShield`, `TapeLayer`, `TapeLap`, `Seasons`, `Ratings`, `Reduce`, `Spacing`, `LineType`, `Like`) match the pinned TypedDict exactly, and `Conductors` is confirmed as the Python keyword for the DSS `Wires` row in both wrapper and engine (`PropertyNameJSON[ord(TProp.wires)] := 'Conductors'`).
- **Construction-order requirements are correct.** The workflow's "set `NConds` before coordinates and units" and "`Line.Spacing` before `Line.Conductors`/`Wires`" instructions follow `LoadSpacingAndWires` (which assigns `NConds` from the spacing, then fills `X`, `H`, `Units`, and conductor references) and the `Line` setter path.
- **Reduction and side-effect statements are correct.** `if FNConds > FNPhases then FReduce := TRUE` in `LoadSpacingAndWires` supports the "reduction enabled when the spacing has more conductors than phases" claim; `KillGeometrySpecified` in the `geometry`/`spacing`/`wires` branch supports the "assigning Geometry clears the prior LineCode and spacing definition" warning.
- **Same-frequency cache limitation is stated as observed, not as a rule.** The workflow and `capi-line-geometry-frequency-cache` describe the probe result (RMatrix unchanged at 60 Hz after `rho` 100→1000 Ω·m, changed after solving at 50 Hz) and advise rebuilding or verifying, which matches `Line.pas` L764-L771 and L1905-L1938 without asserting a general engine contract.

## SCHEMA RESULT

**pass.** `tools/validate_catalogs.py` exits 0 with 10/10 pairs on the reviewed tree, including `line_geometry_wires_properties.json` against `element_properties.schema.json`. The schema requires per-row `source_refs` (`minItems: 1`, `uniqueItems: true`) and a version-pinned `target_versions` block, permits a null `epri_doc_url`, and accepts any nonempty `element_class`, so it generalizes the Line/LineCode field shape without weakening the citation requirement.

## RUNTIME RESULT

**pass.** Executed by this review in a fresh venv on the pinned stack (Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, `jsonschema` 4.26.0).

- `run_examples.py`: 4/4 examples PASS; both `line-geometry-spacing-*` examples report three phases, 1 km, four conductor positions, `Reduce=True`, and no version-drift warning.
- `readback_line_geometry_wires.py`: exit 0; output equals `docs/audits/phase3b_line_geometry_wires_readback.json` after removing `environment`/date, including the geometry/spacing solve, `rho` cache behavior, spacing-unit reset after `NConds`, WireData derivations (`RAC` 0.306, `Radius` = `CapRadius` 0.009, `GMRAC` 0.0070092, `EmergAmps` 450), and the separate CNData and TSData cable probes with 3×3 resistance matrices.
- The harness asserts observed values against catalog defaults, so a stale catalog or a changed engine would fail the run rather than silently reproduce the JSON.

## Required corrections

| ID | Status | Change | Source |
| --- | --- | --- | --- |
| A-1 | applied in this review | `capi-cable-data-rows`: enum citation `L18-L25` → `L18-L24`; `capi-ts-data-rows`: enum citation `L19-L25` → `L19-L24` | [CableData.pas](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/CableData.pas#L18-L24) · [TSData.pas](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/TSData.pas#L19-L24) |

No other correction is required. A-1 was optional in the QA report and does not affect schema validity or runtime results; validation was re-run after the edit.

## Accepted limitations

1. `LineGeometry.Units` cannot be read reliably through the pinned scalar Python getter; the matrix records it `unavailable` and the workflow routes unit reads through `LineSpacing.Units` or DSS conductor entries.
2. A same-frequency `rho` edit can leave the cached geometry impedance matrix in place; the matrix and workflow describe the observed behavior and the rebuild guidance.
3. Constructor sentinels are recorded in the matrix while catalog defaults stay null where a sentinel would be unusable input.
4. Examples use synthetic conductor data and homogeneous cable constructions; engineering accuracy, mixed cable cases, and feeder regressions remain Phase 4 scope.

## Disposition

The package delivers the catalog, generalized schema, source index additions, engine records, workflow, two executed examples, runtime matrix, build audit, and independent QA/QC report that plan §5.4 requires. Property rows, defaults, units, engine mappings, and keyword casing were re-derived from the pinned sources rather than accepted from the coder's or the QA reviewer's report, and every runtime claim reproduced on a clean environment.

Recommended owner action: accept package 1 and open Phase 3B package 2 (Circuit and Vsource) on the same six-artifact template. No coder remediation is outstanding for package 1.
