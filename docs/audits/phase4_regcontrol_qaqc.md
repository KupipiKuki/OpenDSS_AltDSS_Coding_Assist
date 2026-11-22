# Phase 4.2 RegControl Catalog — Independent QA/QC Report

**Reviewed branch:** `wp/phase4` (synced with `origin/wp/phase4`; tip `4e4791c` is the owner's docs-only decision-17 scoping commit, which leaves the library untouched — verified by `git diff 35a2b7c..4e4791c -- opendss_altdss_library/`, only `manifest.json` next-actions text changed). **Package revision under review:** `35a2b7cc4de10c1f8515f5996eca2cdec088bbee` (per the pinned handoff at `6c43ba6`). **Inputs/baseline revision:** `eb7aca4aac119b1c4478efd958a2aae10fd9d463`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-22. **Reviewer environment:** validation venv, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine self-reports `DSS C-API 0.14.5 revision 87d85c2…`), `jsonschema 4.26.0`; wrapper source = extracted `altdss-0.2.4` wheel at tag `2b6fa7e…`; engine sources = `RegControl.pas`, `Transformer.pas`, `CktElement.pas`, `CktElementClass.pas`, `Solution.pas` at DSS C-API tag `0.14.5` (`87d85c2…`), fetched live from raw.githubusercontent.com.

**STATUS:** PASS (no blocking findings; no required corrections)

## Run verification (fresh runs on the pinned stack, `python -B` from the repo root)

- `tools/validate_catalogs.py` → exit 0, **17/17 schema pairs**, including the new `references/regcontrols/regcontrol_properties.json` paired with the **existing** `element_properties.schema.json` (no schema change, as the coder handoff required; `validate_catalogs.py` gained exactly the one pair entry).
- `tools/run_examples.py` → exit 0, **16/16**, both new RegControl examples `Observed-working` with full environment blocks.
- `tools/run_fixtures.py` → exit 0, **both revision-1 goldens still pass** (ieee13 16/38/2 iter, lowest 611 @ 0.960843; ieee34 37/117/25 iter/6 ctrl, lowest 890 @ 0.923099) — the goldens that carry the regulator taps are unmoved.
- `tools/readback_regcontrol.py` → exit 0, and its stdout is **identical to the committed `phase4_regcontrol_readback.json`** including the environment block (same pinned stack, same capture date 2026-11-22); all sections populated: 35 defaults, tap paths, tap range/winding, max-tap-change, sensing, enabled/power, actions/casing, guards, standalone examples.

## Surface correspondence (pinned sources, independent parse)

- Catalog: 1 record, `element_class: RegControl`, **35 properties** = 32 engine members + `BaseFreq` + `Enabled` + `Like`; `required_properties` = `name`, `transformer`; record-level sources name the EPRI element + properties pages, the 0.2.4 wrapper, and the 0.14.5 engine.
- Wrapper (AST parse of `RegControl.py` @0.2.4): `RegControlProperties` TypedDict has exactly the same **35 keys** as the catalog's `altdss_keyword` set; the `RegControl` class has 35 `property(...)` assignments, all but `Like`/`Reset` matching catalog keywords case-insensitively (the two actions are methods, catalogued with `python_method`/`dss_text_write`/`python_creation_status` fields instead — the trap is recorded, not repeated as prose).
- Engine (`RegControl.pas` @0.14.5, L69-L103): `TRegControlProp` = INVALID + **32** members; lowercased, exactly the catalog names minus `basefreq`/`enabled`/`like`.
- All **177** row `source_refs` are pinned-tag (`0.2.4`/`0.14.5`) blob URLs with in-range lines against the fetched files (including cross-file refs to `enums.py`, `DSSObj.py`, `Transformer.pas`, `CktElement*.pas`, `Solution.pas` — all fetched and bounds-checked; zero past-EOF, zero mutable refs). Spot checks land on the claimed content (e.g. `tapnum` → RegControl.pas L312-L317 property registration; `enabled` → Solution.pas L1974-L1985 `SampleControlDevices`; `ptphase` → wrapper L629 TypedDict line).
- `dss_capi.json`: 119 → 134, **+15 records, all `capi-regcontrol-*`, zero pre-existing records changed** (id-keyed comparison, not just line counts). Each record's `source` URL is pinned `0.14.5` and all 32 cited `Lxx-Lyy` ranges are in-bounds against the fetched Pascal files. `tested` values are pass-with-environment or `not-run` (source-only) — consistent with the `#123` source-only labelling.
- `examples.json`: 14 → 16; the two new records (`regcontrol-controlled-voltage-altdss`, `regcontrol-fixed-tap-voltage-dss`) have resolving `source_ids`, full environment blocks, `Observed-working` status, and **no duplicate example_ids**. Both example files build their own two-winding transformer + load (no fixture dependency) and assert a tap readback **and** a regulated-voltage readback, stating the control path (Python: Static controlled solve → tap 3, PT 122.16480 V; DSS: `ControlMode=Off` + `TapNum=4`, PT ≈122.91429 V).
- `sources.json`: 100 → 110, **+10 records, purely additive** (zero removed lines in the git diff), covering the EPRI pages, wrapper, engine, phase-selection enum, transformer tap bounds, and Solution solve paths.
- EPRI pages checked live: `RegControl.html` **200**, `Properties23.html` **200** (the two cited); `RegControl1.html` and `Regulators.html` **404** and are not cited — matching the handoff.

## Baseline preservation and scope

`git diff eb7aca4..35a2b7c` touches exactly 12 files, all inside `docs/`, `references/`, `examples/`, `tools/` (acceptance #7): the build audit, readback matrix, QA/QC handoff, workflow, two examples, `dss_capi.json`, `examples.json`, the new `regcontrols/regcontrol_properties.json`, `sources.json`, the new `readback_regcontrol.py`, and the one-line pair registration in `validate_catalogs.py`. **No Phase 3/4.1 catalog, no fixture file, no golden, no schema, and neither `run_fixtures.py` nor `run_examples.py` changed** (verified by path-filtered diff — empty).

## Probe reproductions (independent, on the pinned stack)

- Guards: `new` without transformer / unknown name / **Line name** as transformer → `(#124)` each; `Winding=5` on a two-winding transformer → `(#122)` "Winding no. 5 does not exist"; `MaxTapChange=1` from tap 0 → `(#485) Warning Max Control Iterations Exceeded`; `Vreg` attribute → `AttributeError: 'RegControl' object has no attribute 'Vreg'`; `Like=`/`Reset=` constructor keywords → `AttributeError ... read-only`. All match the matrix strings, which themselves reproduced byte-identically.
- Tap paths on ieee13: solved tap **9**; manual write 5 + controlled `Solve()` → back to **9** in **12 total iterations**; `ControlMode=Off` + `Solve()` → held **5**; `SolveNoControl()` → held **5**. Clamping: `TapNum=99` → reads **16**, `−99` → **−16** (32-tap 0.9–1.1 winding). `PTRatio=50` after `RemotePTRatio=10` reads 50/50; ordered writes give distinct values. `Enabled=False` + `VReg=100` + solve → tap unchanged. `RegControl.reg1.TotalPowers()` → `[0.+0.j]`.
- `#123` is labelled `"source-only for the supported reference paths"` in the matrix and marked source-only in the workflow — the typed-reference boundary (`str | Transformer | AutoTrans`) is respected; no reproduction is claimed.
- Note: my ad-hoc bare-`new()`-then-solve probe on a *different* hand-built circuit surfaced `(#99)` instead of `(#482)`; the committed matrix's `(#482)` comes from the coder's bare probe and was reproduced exactly by the harness rerun, so this is a circuit-dependent wrapper code, not a package discrepancy.

## Limitations (as documented, confirmed)

- Runtime coverage is forward snapshot regulation plus manual-tap scenarios on a standard Transformer; reverse/cogen transitions, line-drop compensation, time-driven delays, and event-log diagnostics are pinned-source-only (`not-run`) records.
- `#123` remains source-only for the supported reference paths; an out-of-scope direct Python-object injection is explicitly not claimed.
- Plan/manifest reconciliation stays with package 4.5; the scoping commit `4e4791c` moved `LoadShape` into 4.3 by owner decision 17.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
