# Phase 3B Package 6 (Generator) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3` (synced with `origin/wp/phase3`). **Package revision under review:** `0a88ad3bb2b1199eeb06fbd30f58baa0477b9a61` (per the pinned handoff; tip `fe5f9c2` only re-pins the handoff). **Baseline for comparison:** `f0d487ec9e93fce200e6f30f431ffe0ff77217c8` (includes the applied Capacitor architect findings E-1/E-2). **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; wheel `altdss-0.2.4-py3-none-any.whl`; engine `generator.pas` (lower-case path, as the audit notes), `GenUserModel.pas`, `GenDispatcher.pas`, `DynamicExp.pas`, `Spectrum.pas` at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`; EPRI pages checked live over HTTP.

**STATUS:** PASS (no blocking findings; no required corrections)

## Schema and runtime results

- **Schema: PASS, 15/15 pairs.** `tools/validate_catalogs.py` at `0a88ad3` exits 0, including the new `references/generators/generator_properties.json`. The shared element schema gained three **optional** string fields (`enum_type`, `reference_class`, `dss_text_keyword`) — purely additive; all previously accepted package catalogs still validate unchanged (confirmed by the 15/15 pass). `dss_capi.json` 119 records, sources 99, examples 14.
- **Examples: PASS, 14/14.** `tools/run_examples.py` exits 0; both new examples (`generator-constant-pq-altdss`, `generator-pv-voltage-target-dss`) pass as recorded `Observed-working`; no version drift.
- **Readback matrix: PASS, reproduced.** `tools/readback_generator.py` exits 0 and its stdout is **identical to the committed `phase3b_generator_readback.json`** except `environment`/`date` (matching the pinned stack). All 49 rows accounted for.

## Coverage findings

- Catalog shape matches the audit: one Generator record, 49 rows = 47 Python creation keywords (incl. the `Like`/`Refuel` actions) + identifier + DSS-text-only `mva` (carrying `dss_text_keyword: MVA` and `supported_in_target: false`, since the wrapper advertises `kVA`); every row has non-empty versioned `source_refs`; all 252 blob refs are pinned-tag, in-range, known files — no mutable refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** `GeneratorProperties` = 47 keys = the 47 catalog keywords exactly; all 45 wrapper `property()` names (excl. `_str`) cataloged. Enum spellings recorded via `enum_type` (e.g. `Model` → `GeneratorModel`).
- **Engine correspondence (0.14.5):** `TGeneratorProp` at generator.pas L128-L175 (scoped-enum shorthand) = 44 own members after INVALID — matches the audit; catalog's 48 non-name rows = 44 own (engine legacy `cls` = catalog row `class`/keyword `Class`, same pattern as Load) + inherited `Spectrum`/`BaseFreq`/`Enabled` + `Like` action. Attribution correct.
- **Baseline preservation:** diff `f0d487e..0a88ad3` shows zero deletions/modifications in `dss_capi.json` (102→119, +17), `sources.json` (88→99, +11), `examples.json` (+2); packages 1–5 catalogs and `altdss_python_api.json` untouched. All example `source_ids` resolve; no duplicate ids.
- **EPRI pages verified live:** `Generator.html` 200 (element) and `Properties9.html` 200 (vocabulary) used; `GenDispatcher.html` is 404, so the GenDispatcher scope is carried by a pinned-source scope note instead — correct handling. The two documented doc-vs-engine discrepancies check out in source: EPRI Generator.html states voltage bounds 0.95/1.05 while the pinned constructor sets `Vminpu := 0.90; Vmaxpu := 1.10` (generator.pas L980-981) and `puXdp := 0.28` (L996) vs the wrapper docstring "Default is 0.27" (Generator.py L563-L574); the catalog rows record the **pinned** values (0.9/1.1/0.28) with the discrepancy noted — correct precedence per the evidence policy.

## Source findings

- All 17 new `dss_capi.json` records cite `blob/0.14.5` files; every cited range was checked against the pinned sources and lands on the claimed construct (enum L128-L175, registration L500-L651, spec sets L510-L517, kVA/MVA alias L639-L643, constructor L937-L1049, connection/topology L553-L731, enum construction L449-L462, model routines L1544-L1922, PV model L1288-L1299/L1635-L1692, dispatch checks L1120-L1183, PVFactor L608/L1031/L1658-L1675, GenDispatcher scope L302-L345, shapes L582-L595/L782-L792, model guards L766-L775/L581-L595/L820-L822/L1816-L1836, fuel/refuel L483-L487/L616-L647/L1040-L1044/L2248-L2257, registers L467-L475/L925-L935/L2213-L2258, MakeLike L844-L897). `tested` split of additions: 13 `pass` / 4 `not-run` (dispatch checks, PVFactor sensitivity, GenDispatcher operation, dynamic-model scope — all correctly source-only with null environment); all `pass` claims corroborated by the reproduced matrix.

## Runtime findings (probes reproduced on the pinned stack)

- **Power families and ratings:** kW/PF and kW/kvar reproduced identically in Python and DSS; bare schedule initializes 1000 kW / 60 kvar / PF 0.88 / 1200 kVA with implied PF ≈0.9982; automatic kVA = 1.2× signed kW; explicit kVA or DSS `MVA` kept its value after power edits; negative-kW consumption direction confirmed via solved terminal powers (injection reads negative).
- **Model 3 PV target:** 1.03 pu request with ±3000 kvar limits achieved ≈1.00443 pu with −3000 kvar terminal injection (positive `Maxkvar` injection limit) while nominal kvar stayed ≈431.79; ±120 kvar cases reached ≈0.99473 pu; the 1.00 case with wide limits reached target — matches generator.pas L1635-L1692 clamping.
- **Model 6 / user-model guards:** `#567` on solve without a user model, `#570` at construction with an explicitly missing DLL, `#401` for the missing DynamicEq reference — all reproduced; no compiled model loaded (kept out of scope as required).
- **Actions/shapes/registers:** `Like` works via DSS text and the Python method (creation-keyword path raises, as documented), preserving target bus while copying the source's delta; both `Refuel` paths restored 100% without changing capacity/reserve; Daily/Yearly/Duty shape assignment incl. fallback; one daily register sample with fuel disabled; Model 1/2/4/5/7 snapshots near rated voltage; DispMode numeric write accepted then rejected by the Python enum getter — as documented.
- Both examples converged; the DSS PV example's achieved voltage and terminal power match the matrix. Docs (README, plan v0.26, manifest) honestly state package 6 "awaits independent QA/QC" and record 15/15 schema, 14/14 examples.

## Limitations (as documented, confirmed)

- GenDispatcher, PVSystem, Storage, and other controllers remain deferred (scope notes in the source index); dispatch effects and PVFactor sensitivity are source-only (`not-run`).
- Compiled user models, dynamic-mode studies, and fuel-consumption time series were kept out of the validation run; runtime coverage stops at default readbacks and the guard paths.
- EPRI-vs-pinned discrepancies (voltage bounds 0.95/1.05 vs 0.90/1.10; wrapper docstring Xdp 0.27 vs pinned 0.28) are documented with pinned values taking precedence.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
