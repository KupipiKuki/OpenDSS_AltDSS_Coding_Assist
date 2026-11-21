# Phase 3A Coder Revisions — QA/QC Report (review of remediation commit)

**Reviewed branch:** `wp/phase3` — tip `2a0fa39` ("Phase 3A coder revisions"), reviewed against the QA/QC findings in `phase3a_api_catalogs_qaqc.md` (commit `cb24007`) and the catalog baseline `45a004d`.
**Reviewed state:** `git status --porcelain` clean at review start.
**Review date:** 2026-11-21. **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0; fresh venv with `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; DSS C-API `Line.pas`/`LineCode.pas` at tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`.
**Scope of this review:** the coder's remediation of the Phase 3A QA/QC findings — did commit `2a0fa39` apply the required corrections exactly, and did it change anything else?

**STATUS:** PASS WITH FINDINGS

## What was checked

- Full diff of `2a0fa39` vs `45a004d` (6 files, 27 insertions / 27 deletions: `README.md`, `docs/audits/phase3a_api_catalogs_audit.md`, `docs/implementation_plan.md`, `opendss_altdss_library/README.md`, `opendss_altdss_library/manifest.json`, `references/dss_capi.json`). `altdss_python_api.json`, `sources.json`, schemas, and tools are untouched, so generator determinism is unaffected.
- Field-level diff of `references/dss_capi.json` between `45a004d` and `2a0fa39`: exactly 5 lines changed, all intended (4 citation strings + 1 note reword); 26 records, identical ids, `tested` split unchanged at 17 `pass` / 9 `not-run`.
- Every corrected citation re-verified against the pinned 0.14.5 sources (see SOURCE FINDINGS for exact line spans).
- Re-ran `tools/validate_catalogs.py` at `2a0fa39` and `tools/run_examples.py` in the pinned venv.
- Checked every doc edit for accuracy against the underlying artifacts (coverage split, `Like` keyword claim, links to the QA/QC report, anchors).
- Grepped the whole repo for the new governance wording to establish what the evidence actually supports.

## COVERAGE FINDINGS

- Finding **C-1 resolved:** the audit coverage table now reads "49 object classes, 49 collection interfaces, and 1 context class. 1,094 properties and 180 methods." — matches the independently verified wheel split.
- Finding **C-2 resolved:** the audit's Known limitations and `manifest.json` `known_gaps` now state that non-element context interfaces (`IBuses`, `ISettings`, `ISolution`, …) and the `Element`/`PCElement`/`PDElement` batch proxies are outside catalog scope.
- No catalog content was added, removed, or relabelled by the coder commit; record counts and evidence labels are unchanged.

## SOURCE FINDINGS

- **S-1/S-2 resolved (with a residual boundary nit, R-1):** both `TLineProp` citations (`capi-line-prop-enum`, `capi-line-no-epsrmedium`) now read `L60-L91`. In `Line.pas` @ 0.14.5 the enum opens at L60 (`TLineProp = (`), the last enumerator `LineType = 30` is at L91, and the closing `);` is at **L92** — so the exact block is **L60-L92**. `L60-L91` covers the declaration and all 31 enumerators but not the closing delimiter line. (Note: my original report also said L60-L91, so the nit is shared; the coder applied the recommendation faithfully.) Non-blocking; exact range recorded here for the record.
- **S-3 resolved exactly:** `capi-linecode-prop-enum` now cites `TLineCodeProp enum, L60-L89`; in `LineCode.pas` @ 0.14.5 the enum opens at L60 and closes at L89 — exact.
- **S-4 resolved (with a residual boundary nit, R-2):** `capi-linecode-b1-b0` now cites "B1/B0 rows, L308-L315". The rows actually span **L308-L316** (B1: L308-L311; B0: L313-L316, with `PropertyRedundantWith[ord(TProp.B0)]` at L316). `L308-L315` covers all substantive scaling lines (`PropertyOffset2 … @GetC1C0Scale` at L309 and L314) but not the final row line. Non-blocking.
- **S-5 resolved:** the `capi-line-prop-enum` note now reads "35 properties … 28 map to rows in TLineProp, including Wires as Conductors … the other seven come from the engine's parent classes. CNCables and TSCables have no separate wrapper properties." — accurate (verified against the 0.2.4 wheel: 35 Line properties = 28 enum-row mappings + `NormAmps`, `EmergAmps`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, `Enabled`).
- **S-6 resolved:** `docs/implementation_plan.md` §5.1 now records that Phase 3A migrated the 15 records into `references/sources.json` "with the same IDs and removed the superseded index and schema" — matches the verified migration (15 records byte-identical, 3 added, old pair deleted).
- The audit's reworded check #3 ("The Line/LineCode property catalog also records creation keywords for actions such as `Like`") was verified: `references/lines/opendss_line_linecode_properties.json` does record `"altdss_keyword": "Like"`.
- **NEW FINDING F-1 (out-of-scope, inaccurate governance edit — required correction):** `docs/implementation_plan.md` §8 "Roles" was changed from "Codex is the primary coder; Mistral is the independent QA/QC reviewer; the project owner decides which findings block merge and approves scope changes." to "**DeepSeek is the architect and also contributed Phase 3A QA/QC.** Codex is the primary coder; …", and version-history row 0.5 adds "recorded DeepSeek's architect role." The evidence does not support this: (a) the Phase 1 documents identify DeepSeek solely as the owner-selected **external auditor** for the Phase 1 audit (`docs/phase_1/PHASE_1_EXTERNAL_AUDIT_REPORT.md`: "Auditor: DeepSeek (external model, owner-selected)"); (b) nothing in the repo names DeepSeek as architect — plan §3 is titled "Architect verification performed for this plan" and records no DeepSeek role; (c) the Phase 3A independent QA/QC was performed by Mistral Vibe — see `phase3a_api_catalogs_qaqc.md` (commit `cb24007`) and §8's own retained sentence naming Mistral as the independent QA/QC reviewer; (d) §11 Owner decisions records no decision authorizing a role change, and §8 states the owner approves such changes. This edit is unrelated to the remediation scope and misattributes both a role and a Phase 3A QA/QC contribution.
- All new cross-links resolve: audit → `phase3a_api_catalogs_qaqc.md` (same dir), library README → `../docs/audits/phase3a_api_catalogs_audit.md#independent-qaqc-disposition` (anchor exists), plan → `audits/phase3a_api_catalogs_qaqc.md`, README → QA/QC report.

## EVIDENCE FINDINGS

- No evidence labels changed; `tested` statuses untouched (17 `pass` / 9 `not-run`), so no new runtime claims were introduced by the coder commit.
- Doc status lines (root README, library README, manifest `validation.source_review`, plan status) now say QA/QC "passed with findings" and that corrections are applied — accurate with respect to findings C-1/C-2/S-1…S-6; note F-1 above is a new issue introduced by this same commit, not covered by that wording.
- `manifest.json` `next_actions` correctly dropped the Phase 3A QA/QC item; Phase 3B/4 actions retained.

## SCHEMA RESULT

**PASS** — `python opendss_altdss_library/tools/validate_catalogs.py` at `2a0fa39` exits 0: 9/9 manifest-and-catalog schema pairs pass (Draft 2020-12 with format checking, `jsonschema` 4.26.0, Python 3.14.6). The edited `dss_capi.json` remains schema-valid.

## RUNTIME RESULT

**PASS** — `python opendss_altdss_library/tools/run_examples.py` at `2a0fa39` in a fresh venv (Windows 11 AMD64, Python 3.14.6, altdss 0.2.4, dss-python 0.15.7, dss-python-backend 0.14.5; no drift vs `manifest.json` support_targets): both examples PASS, matching their recorded `Observed-working` environments. (The coder commit did not touch the examples or the API catalog, so this re-confirms rather than re-establishes runtime evidence.)

## REQUIRED CORRECTIONS

1. **`docs/implementation_plan.md` §8 "Roles" (finding F-1) — required.** Revert the roles line to the `45a004d` wording: "Codex is the primary coder; Mistral is the independent QA/QC reviewer; the project owner decides which findings block merge and approves scope changes." Remove "DeepSeek is the architect and also contributed Phase 3A QA/QC." If the owner genuinely intends a DeepSeek architect role, record it as an explicit decision in §11 Owner decisions first — Phase 1 records show DeepSeek only as the owner-selected external auditor (`docs/phase_1/PHASE_1_EXTERNAL_AUDIT_REPORT.md`), and the Phase 3A QA/QC report at `cb24007` was produced by Mistral Vibe.
2. **`docs/implementation_plan.md` history row 0.5 (finding F-1) — required.** Drop the clause "and recorded DeepSeek's architect role"; keep "Recorded the Phase 3A QA/QC disposition, clarified the source-index migration".
3. **Optional precision (R-1):** `references/dss_capi.json` `capi-line-prop-enum` and `capi-line-no-epsrmedium` section "TLineProp enum, L60-L91" → "L60-L92" (closing `);` at L92), source <https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas> tag `0.14.5` = `87d85c2622c8281b92255335bc7c09b11191b21d`. Non-blocking: L60-L91 already covers all enumerators.
4. **Optional precision (R-2):** `capi-linecode-b1-b0` "B1/B0 rows, L308-L315" → "L308-L316" (same source file as S-3). Non-blocking: the scaling lines are inside the cited range.

No files were modified by this review; this report is the only file added.
