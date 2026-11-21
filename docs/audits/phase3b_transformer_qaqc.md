# Phase 3B Package 3 (Transformer and XfmrCode) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3` (synced with `origin/wp/phase3`). **Package revision under review:** `a7b485de98c1ecf7a68778634e53c30d6e4d7b33` (per the pinned handoff; tip `04463b8` only re-pins the handoff). **Baseline for comparison:** `30103e6f85cb7c2f935fe5db3fbf8fe2b8765c46`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; wheel `altdss-0.2.4-py3-none-any.whl`; engine sources (`Transformer.pas`, `XfmrCode.pas`, `CAPI_Alt.pas`, `CktElement.pas`, `CktElementClass.pas`, `PCElement.pas`, `PDElement.pas`, `PDClass.pas`, …) at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`; EPRI pages checked live over HTTP.

**STATUS:** PASS (no blocking findings; no required corrections)

## Schema and runtime results

- **Schema: PASS, 12/12 pairs.** `tools/validate_catalogs.py` at `a7b485d` exits 0, including the new `references/transformers/transformer_properties.json` (2 records) under the generalized element schema; `dss_capi.json` 75 records, sources 67, examples 8.
- **Examples: PASS, 8/8.** `tools/run_examples.py` exits 0; both new examples (`transformer-two-winding-altdss`, `transformer-three-winding-xfmrcode-dss`) pass and are recorded `Observed-working`; no version drift.
- **Readback matrix: PASS, reproduced.** `tools/readback_transformer.py` exits 0 and its stdout is **identical to the committed `phase3b_transformer_readback.json`** except `environment`/`date` (matching the pinned stack). Matrix: 104 entries = 85 `read back` + 17 `DSS text readback` + 2 `action` (Like) — exactly the 104 catalog rows. The documented four-winding crash sequence was correctly kept out of the test run; only the single invalid `Windings=1` write is exercised.

## Coverage findings

- Catalog shape matches the audit exactly: Transformer 60 rows (50 Python keywords + 9 DSS scalar paths + 1 identifier), XfmrCode 44 rows (35 + 8 + 1); total 104. Every row has non-empty `source_refs`; all 374 blob refs (rows + conditionals + record sources) are pinned-tag (`0.2.4`/`0.14.5`), in-range, known files — no mutable refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** `TransformerProperties` = 50 keys = the 50 catalog keywords (only `Like` is an action, not a `property()`); all 49 wrapper `property()` names (excl. `_str`) are cataloged. Same for XfmrCode: 35 = 35, 34 props all cataloged. Casing verified (`pctR`, `XSCArray`, `RDCOhms`, `ppm_Antifloat`, `NormHkVA`, …).
- **Engine correspondence (0.14.5):** `TTransfProp` (Transformer.pas L88) and `TXfmrCodeProp` (XfmrCode.pas L68) enums, winding struct `TWinding` L162-L187, and inherited registrations (CktElement/PDElement/PDClass) all line up with the catalog rows; the 9+8 DSS-scalar rows are the struct-array scalar paths (`wdg`, `bus`, `conn`, `kv`, `kva`, `tap`, `%r`, `RNeut`, `XNeut`) with no Python keyword — correctly marked and described.
- **Baseline preservation:** diff `30103e6..a7b485d` shows zero deletions/modifications in `dss_capi.json` (59→75, +16), `sources.json` (51→67, +16), `examples.json` (+2 records); packages 1–2 catalogs, `altdss_python_api.json`, and prior QA reports untouched. All example `source_ids` resolve; no duplicate ids.
- **EPRI link correction verified live:** `Transformer1.html` (element page, used as `epri_doc_url`/`epri-transformer`) returns 200; `Transformer.html` returns 200 and does document `RegControl` — the source index keeps it as `epri-regcontrol-transformer-property` with an explicit scope note. `XfmrCode.html` and `AutoTrans.html` return 200; AutoTrans carries a "deferred pending owner approval" scope note. No invented citations.

## Source findings

- All 16 new `dss_capi.json` records cite `blob/0.14.5` files; every cited range was checked against the pinned sources and lands on the claimed construct (winding struct L162-L187, windings flag/side effects L446-L448/L633-L665, winding init L1361-L1381, spec sets L379-L403 / XfmrCode L214-L221, scalar/array scales L482-L493 & XfmrCode L284-L287/L355-L361, XSCArray size/scale L340-L343/L410-L414 & XfmrCode L233-L237/L305-L324, tap registration/effects L462-L477/L509-L514/L723-L739 and control setter L1391-L1426, code copy L2040-L2098, RDCOhms L479-L480/L706-L707 + derivation L980-L1010, kVA ratings L666-L686/L1016-L1038, WdgCurrents L345-L366/L1512-L1577, CAPI_Alt result interfaces L1623-L1655). `tested` split of additions: 14 `pass` / 2 `not-run`; all `pass` claims corroborated by the reproduced matrix; `not-run` records are static spec-set facts with null environment.

## Runtime findings (probes reproduced on the pinned stack)

- **Winding resize/reset:** 2→3 windings reset Conns/kVs/kVAs/Taps/pctR and extended `XSCArray` to `[7, 30, 30]` (Transformer) and `[0, 30, 30]` (XfmrCode) while scalar `X13` still read 35 — exactly as documented; bus names retained and lowercased; a 4-name `Buses` array on 2 windings raised `#20200424`.
- **`Windings=1` probe:** direct assignment and `edit(Windings=1)` both left the value at 2 and the checked edit reported `(#2020031) … Value (1) must be greater than one` — matching the `GreaterThanOne` flag (Transformer.pas L446-L448). The architect's four-winding segfault sequence was not run, per the handoff.
- **Impedance array vs scalar:** fresh Transformer reads `XSCArray=[7]`, bare XfmrCode `[0]`; array write `[11,21,31]` leaves scalar readbacks unchanged; a later scalar edit rebuilds the array — matches the workflow and Transformer.pas L963-L978 / XfmrCode.pas L473-L571.
- **DC resistance:** initial 0.088117 Ω per winding (default wye base), bare-code init 0.26435153 Ω (line-to-line kV); array write `RDCOhms=[0.5,0.6]` retained only the second value after recalculation, while explicit per-winding DSS edits (`wdg=1 RDCOhms=0.5`, `wdg=2 RDCOhms=0.6`) persisted both — the documented behavior and its workaround are accurate.
- **Taps/losses/ratings:** Python `Taps` stored 1.5 with `MaxTap=1.1` (direct storage, no clamping — the clamping path is the separate tap control, source-reviewed at L1391-L1426); `pctLoadLoss`/`pctR`/`pctRs` update paths and both kVA rating paths (from `kVAs` array: 880/1200; from winding-1 kVA: 770/1050 = 1.1/1.5×) reproduced.
- **Solves:** the 100 kW unity-PF two-winding solve converged; `WindingCurrents()` returned 12 complex values (zeros before solve), `LossesByType()` returned total=load≈40.035+j701.612 VA with no-load 0 — matching the audit; the three-winding XfmrCode DSS example converged with 3 buses/terminals and code copy-on-assignment plus reassignment bringing later code edits across.
- Docs (README, plan v0.13, library README, skill, manifest) honestly state package 3 "awaits independent QA/QC"; manifest records 12/12 schema, 8/8 examples, and the two-winding/three-winding scope limit with AutoTrans deferred.

## Limitations (as documented, confirmed)

- Scope is two- and three-winding models only; the `Windings=1`→`Windings=4` segfault hazard (architect report, exit 139) is real and the matrix deliberately exercises only the invalid single write; AutoTrans deferred pending owner decision.
- Array vs scalar impedance and `RDCOhms` recalculation quirks are documented with the correct DSS per-winding workaround.
- Winding result methods have the open-terminal caveat (source-reviewed via TransformerExtras.py).
- Examples are illustrative single-load solves; multi-source, harmonic, thermal, and Phase 4 feeder fixtures remain out of scope.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
