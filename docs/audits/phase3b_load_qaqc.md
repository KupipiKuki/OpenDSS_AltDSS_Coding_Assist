# Phase 3B Package 4 (Load) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3` (synced with `origin/wp/phase3`). **Package revision under review:** `37854f664369e61c9c2a7f22ee05a7295152685c` (per the pinned handoff; tip `ea04f3a` only re-pins the handoff). **Baseline for comparison:** `b896db8a298ad9fe1963d692c6a53649cf9b7ed0`. **Reviewed state:** tree clean at review start; all package-4 artifacts reviewed are byte-identical to `37854f6` (verified via `git diff 37854f6 -- opendss_altdss_library/ docs/audits/ docs/workflows/`, empty). During the review the working tree gained unrelated, uncommitted package-5 preparation (`docs/implementation_plan.md` modified to plan 0.18 and untracked `docs/handoffs/Phase_3B_Capacitor_Coder_handoff.md`); those files are outside this package and were not reviewed.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; wheel `altdss-0.2.4-py3-none-any.whl`; engine `Load.pas` (and inherited `PCElement.pas`/`CktElement.pas`/`Spectrum.pas`) at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`; EPRI pages checked live over HTTP.

**STATUS:** PASS (no blocking findings; no required corrections)

## Schema and runtime results

- **Schema: PASS, 13/13 pairs.** `tools/validate_catalogs.py` at `37854f6` exits 0, including the new `references/loads/load_properties.json` under the generalized element schema; `dss_capi.json` 88 records, sources 77, examples 10.
- **Examples: PASS, 10/10.** `tools/run_examples.py` exits 0; both new examples (`load-power-family-comparison-altdss`, `load-zipv-snapshot-dss`) pass as recorded `Observed-working`; no version drift.
- **Readback matrix: PASS, reproduced.** `tools/readback_load.py` exits 0 and its stdout is **identical to the committed `phase3b_load_readback.json`** except `environment`/`date` (matching the pinned stack). All 43 catalog rows are accounted for in the matrix (42 readback cells incl. one enum-typed row, plus the `Like` action).

## Coverage findings

- Catalog shape matches the audit: one Load record, 43 rows = 42 case-sensitive Python creation keywords + 1 identifier row; every row has non-empty versioned `source_refs`; all 213 blob refs (rows + conditionals + record sources) are pinned-tag (`0.2.4`/`0.14.5`), in-range, known files — no mutable refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** `LoadProperties` TypedDict = 42 keys = the 42 catalog keywords exactly (only `Like` is action-only); all 41 wrapper `property()` names (excl. `_str`) are cataloged. Casing verified (`kW`, `kvar`, `PF`, `AllocationFactor`, `pctSeriesRL`, `puXHarm`, …).
- **Engine correspondence (0.14.5):** `TLoadProp` at Load.pas L111-L151 (38 members); the catalog's 42 rows = 38 own members (engine legacy name `cls` = catalog row `class`/keyword `Class`, same legacy/new-name pattern as `wdg`) + inherited `Spectrum`/`BaseFreq`/`Enabled` from PCElement/CktElement, which the rows mark as inherited — attribution correct.
- **Baseline preservation:** diff `b896db8..37854f6` shows zero deletions/modifications in `dss_capi.json` (75→88, +13), `sources.json` (67→77, +10), `examples.json` (+2 records); packages 1–3 catalogs and `altdss_python_api.json` untouched. All example `source_ids` resolve; no duplicate ids.
- **EPRI pages verified live:** `Load1.html` 200 (element page, used as `epri_doc_url`; `Load.html` is 404, so the link is the correct one), `Properties7.html` 200 (Load property vocabulary), `Properties17.html` 200 (Fault page, as the audit states). LoadShape/GrowthShape deferral is recorded in their scope notes; their pages return 200 and are cited for vocabulary only.

## Source findings

- All 13 new `dss_capi.json` records cite `blob/0.14.5/Load.pas`; every cited range was checked against the pinned file and lands on the claimed construct: spec sets L368-L381 + required flags L402-L405/L448-L457 (billing set declares PF second — confirmed in source), kW/PF branch and selector branches L562-L717, EndEdit L725-L737, RecalcElementData L1152-L1198, allocation writes L586-L601/L676-L690 + math L2167-L2191, conductor counts L479-L492, voltage-base setters L516-L560, percent properties L407-L413, constructor L801-L888, shape assignment L425-L433/L620-L643/L989-L1014, ZIPV registration L396-L400 + flag L719-L720 + DoZIPVModel L1525-L1541 + dispatch L1901-L1912 + low-voltage branches L1581-L1652, voltage-limit fallback L855-L861/L2030-L2048. `tested` split of additions: 10 `pass` / 3 `not-run`; all `pass` claims corroborated by the reproduced matrix; `not-run` records are static source facts (shape runtime dispatch, ZIPV low-voltage branches, voltage-limit service evaluation) with null environment.

## Runtime findings (probes reproduced on the pinned stack)

- **Five specification families** (kW/PF, kW/kvar, kVA/PF, kWh billing, connected-kVA/XfkVA) exercised in both Python and DSS text with identical results; family switching and the PF-only edit under kW/kvar return the implied PF (0.9285…) in attributes, `edit(...)`, and DSS text.
- **Allocation order effect:** PF-last gave 44 kW, PF-first 45 kW, reapply-with-PF restored 45 kW — identical in Python kwargs and DSS text, matching the audit's note that `Ordering_Last` does not fix DSS command execution order.
- **Edit finalization:** bare `Load.new(name)` separate writes left kvar/kVA stale until EndEdit/completed kwargs/DSS command — reproduced; the completed-kwargs comparison behaves as recorded.
- **kVA paths:** fresh billing-family load with explicit PF reads zero kVA; a billing edit on an existing kW/kvar load keeps the reference-based kVA — matches Load.pas L1189-L1198.
- **Topology/shapes:** connection table (wye 3-phase → 4 conductors, delta → 3, etc.), Daily's Yearly fill with explicit-Yearly preservation, `UseActual` with specified PF or kvar, percent scaling (pctMean 75, pctStdDev 12, pctSeriesRL 30), defaultload Spectrum reference, voltage-limit defaults (VMaxPU 1.05 etc.) — all reproduced.
- **Solves:** both Python loads served 60 kW + ≈19.721 kvar; the DSS ZIPV example converged (60 kW, 15 kvar, four terminal currents); a six-coefficient ZIPV write raised `#20200423` (expected 7, got 6).
- Docs (README, plan v0.17, manifest) honestly state package 4 "awaits independent QA/QC"; manifest records 13/13 schema and 10/10 examples.

## Limitations (as documented, confirmed)

- LoadShape and GrowthShape property catalogs are deferred; their EPRI pages are cited for vocabulary only, with scope notes.
- Shape time-series dispatch, ZIPV low-voltage/cutoff sweeps, and voltage-limit service evaluation are source-reviewed only (`not-run`); runtime evidence covers assignment and snapshot cases.
- Examples are illustrative single-load circuits; Phase 4 feeder fixtures remain out of scope.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
