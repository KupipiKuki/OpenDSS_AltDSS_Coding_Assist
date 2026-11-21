# Phase 3B Package 1 (LineGeometry, LineSpacing, WireData, CNData, TSData) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3`. **Package revision under review:** `2cd9b335e83f7a3d61134a8400ccd6800ddc1f57` (per the pinned handoff; tip `bdc429b` only re-pins the handoff). **Baseline for comparison:** `ab444fd`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (per `tools/requirements-validation.txt`); wheel `altdss-0.2.4-py3-none-any.whl` from PyPI; engine sources `Line.pas`, `LineGeometry.pas`, `LineSpacing.pas`, `WireData.pas`, `CNData.pas`, `TSData.pas`, `ConductorData.pas`, `CableData.pas` at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`.

**STATUS:** PASS (no blocking findings; two optional citation-precision notes below)

## Verdict summary

The package delivers what the build audit claims, the baseline is preserved, and every runtime claim I could re-execute reproduced exactly on the pinned stack.

## Schema and execution results

- **Schema: PASS, 10/10 pairs.** `python opendss_altdss_library/tools/validate_catalogs.py` at `2cd9b33` exits 0 — manifest, Line/LineCode catalog (2), new `line_geometry_wires_properties.json` (5), sources (34), examples (4), the three empty Phase 1 catalogs, `altdss_python_api.json` (99), `dss_capi.json` (45), plus the new `element_properties.schema.json` pairing added to `SCHEMA_PAIRS`.
- **Examples: PASS, 4/4.** `tools/run_examples.py` exits 0; both Phase 2 examples and both new `line-geometry-spacing-*` examples run clean, recorded `Observed-working`, environment block matches the pins (no drift warning).
- **Readback matrix: PASS, reproduced.** `tools/readback_line_geometry_wires.py` exits 0 and its stdout is **identical to the recorded `docs/audits/phase3b_line_geometry_wires_readback.json`** except the environment/date fields (which match the pinned stack). Matrix cells: 82 total = 76 `read back` + 5 `action` (Like) + 1 `unavailable` (LineGeometry.Units) — exactly the audit's claim. Side-effect probes reproduced: geometry/spacing solve with 4 conductors, 3 retained phases, 1 km, Reduce=True, first-conductor ampacities [300, 450]; `rho` 100→1000 Ω·m at 60 Hz left RMatrix unchanged (`r_matrix_changed_at_60_hz: false`) and changed only after solving at 50 Hz; `NConds` edit reset spacing units to `ft`; WireData derived values RAC=0.306 (=1.02×0.30), Radius=CapRadius=0.009, GMRAC=0.0070092, EmergAmps=450; separate CNData and TSData spacing probes solved with 3 phases, 3 typed conductors each, 9-element RMatrix.

## Coverage findings

- 82 property rows across five classes — 15/7/15/23/22 for LineGeometry/LineSpacing/WireData/CNData/TSData — matching the audit table, including one `name` and one `like` row per class. Every row carries a non-empty `source_refs` array (schema-required); I checked all 318–319 refs: all are `blob/0.14.5/…`, `blob/0.2.4/…`, or EPRI pages — no mutable `master` refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** every catalog `altdss_keyword` exists in the element's `*Properties` TypedDict, and the only TypedDict key not cataloged is `Like` (recorded as an action row). Wrapper property sets match catalog row names case-insensitively, modulo the documented engine alias `wires` → wrapper `Conductors` (catalog row `wires` carries `altdss_keyword: Conductors`).
- **Engine correspondence (0.14.5 .pas):** LineSpacing 5/5, WireData 13/13 (all `TConductorDataProp`), CNData 21/21 (13 ConductorData + 4 CableData + 4 own), TSData 20/20 (13 + 4 + 3) — inherited conductor/cable attribution is arithmetically exact. LineGeometry has 19 enum rows in the engine; the catalog's 13 rows fold the six object-reference alias rows (`wire`, `cncable(s)`, `tscable(s)`, `cond`) into the single `wires` row, and engine record `capi-line-geometry-conductors` cites those alias rows (LineGeometry.pas L275-L299, L338-L355) — acceptable, noted for the record.
- **Baseline preservation:** diff `ab444fd..2cd9b33` shows zero deletions or modifications in `dss_capi.json` (26→45, +19) and `sources.json` (18→34, +16); the Line/LineCode catalog, `altdss_python_api.json`, QA reports, and the generator are untouched; `examples.json` gained exactly the two new records. All `source_ids` in `examples.json` resolve in `sources.json`; no duplicate ids.
- **TSData EPRI absence disclosed:** `epri_doc_url` is `null` for TSData and `capi-ts-data-engine`'s scope note states the EPRI TSData URL was unavailable and no standalone page is cited — no invented citation.

## Source findings

- All 19 new `dss_capi.json` records cite `blob/0.14.5` URLs; I checked every cited range's content at the pinned tag: enum blocks (TLineGeometryProp L58-L79, TLineSpacingProp L28-L35, TConductorDataProp L45-L60, TCNDataProp L26-L32 — all exact), constructors, PropertySideEffects blocks, SetWires L795-L828, FetchLineSpacing L1838+, rho branch L764-L771, FMakeZFromGeometry L1905-L1938 — all land on the claimed code. `tested` split of the additions: 6 `pass` / 13 `not-run`; every `pass` claim is corroborated by the reproduced matrix (defaults, ratings, reduction, rho cache, units reset, derived values, cable probes); `not-run` records are static source facts with null environment.
- **Optional precision note (S-1):** in `capi-cable-data-rows` and `capi-ts-data-rows`, the enum citations `TCableDataProp … L18-L25` and `TTSDataProp … L19-L25` include the `…PropLegacy = …;` alias line; the enums close at L24 (`);`). Content is correct; exact ranges would be L18-L24 and L19-L24. Non-blocking.
- Property-row anchors: representative spot checks land on the right code (e.g. LineSpacing.pas L128-L143/L160-L173/L194-L215 for NConds allocation + unit reset + constructor; LineGeometry.pas L301-L305 `OnArray` units storage; L621-L654 constructor; wrapper LineGeometry.py L164-L177 scalar `Units` getter via `Obj_GetInt32`; Line.py L484-L512 `Conductors` setter). A few rows cite constructor blocks (e.g. ConductorData.pas L282-L300) where the literal name doesn't appear in-range because fields are PascalCase — these are legitimate default/behavior citations, verified representative cases (RAC=1.02×RDC at ConductorData.pas L228).

## Runtime findings and the two documented limits

- Both limits were verified against source **and** by execution: (1) `LineGeometry.Units` is array-backed in the engine (`OnArray` flag, LineGeometry.pas L301-L305) and the pinned scalar getter (AltDSS-Python 0.2.4 `LineGeometry.py` L164-L177, `Obj_GetInt32` on property 7) can raise `ValueError` — the matrix records that cell `unavailable`, and the workflow routes unit reads through the spacing object / DSS entries. (2) A `rho` edit at unchanged frequency leaves the cached geometry impedance matrix in place (Line.pas rho branch L764-L771 sets `YprimInvalid` but `FMakeZFromGeometry` L1905-L1938 reuses the matrix at the same frequency) — the probe observed `r_matrix_changed_at_60_hz: false`, `r_matrix_changed_after_switching_to_50_hz: true`. Both limits are accurately stated in the workflow and audit.
- Both example files exercise the two construction paths correctly: geometry path (`LineGeometry` with NConds/NPhases, `Spacing` copy, `Conductors`, `Reduce`, then `Line.Geometry` + `Length`) and direct spacing path (`Line.Spacing` before `Line.Conductors` in Python kwargs and before `Wires` in the DSS text). Phase/conductor counts (4 positions, 3 phases), reduction, units (m positions, km length), and typed cable readback all match the recorded results.
- Docs (root README, plan v0.7, library README, skill, manifest) consistently describe the package as coder-validated and awaiting independent QA/QC — no overclaiming.

## Prior-phase carryover checks

- Phase 3A finding F-1 is properly resolved: `ab444fd` records the role assignment as owner decision #4 in plan §11 (DeepSeek architect/auditor, GPT-6.2 Sol coder, Mistral 4 QA/QC) and §8 references it; the stray `.linecode.pas` accidentally added in `0b5469e` was removed in `9ef0289`; repo root is clean. R-1/R-2 citation widenings (L60-L92, L308-L316) are in place and match the 0.14.5 sources exactly.

## Limitations (as documented by the coder, confirmed)

- `LineGeometry.Units` scalar Python getter can raise `ValueError` (array-backed engine field); recorded as `unavailable` in the matrix.
- Same-frequency `rho` edits can leave the cached impedance matrix unchanged; matrix changes only on a frequency change.
- Constructor sentinel values (e.g. -1.0) are recorded in the matrix; catalog defaults left unspecified where a sentinel would be unusable input.
- Examples use synthetic parameters and homogeneous cable constructions; engineering accuracy, mixed cable cases, and feeder regressions are Phase 4 scope.

## Required corrections

None. Optional: adjust the two enum citations noted in S-1 (`CableData.pas` L18-L24, `TSData.pas` L19-L24) if exact enum spans are wanted.

No files were modified by this review; this report is the only file added.
