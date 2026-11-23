# Phase 4.5 exit package — Independent QA/QC Report

**Reviewed branch:** `wp/phase4` (tip `2c51fc1`, synced with `origin/wp/phase4`; the tip is docs-only — it pins the handoff's package-revision line, verified by `git diff 75c6e1c..2c51fc1`, one line in the QA/QC handoff). **Package revision under review:** `75c6e1ca9adf8e06f704a31d7d42593cb5ba57c5` (per the pinned handoff at `2c51fc1`). **Inputs/baseline revision:** `cc8aa92ecaf14bbc4f54a2ee78b177adbf130bb8`. **Reviewed state:** `git status --porcelain` clean; `git diff --check cc8aa92..2c51fc1` clean.
**Review date:** 2026-11-22. **Reviewer environment:** fresh venv installed from `tools/requirements-validation.txt`, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine `DSS C-API 0.14.5 revision 87d85c2…`), `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`.

**STATUS:** PASS (no blocking findings; no required corrections)

## Run verification (fresh environment, `python -B` from the repo root)

- `tools/validate_catalogs.py` → exit 0, **18/18 schema pairs**, including `references/troubleshooting.json` with **16 records** against the existing troubleshooting schema.
- `tools/run_examples.py` → exit 0, **19/19 PASS**, including `ieee13-snapshot-cross-interface` (now classified `python_cross_interface`).
- `tools/run_fixtures.py` → exit 0, **3/3 PASS** (ieee13 snapshot 16/38/2/1, lowest 611 @ 0.960843; ieee13 daily 24 h, 73416.540 kWh, peak 4004.671 kW @ hour 18; ieee34 snapshot 37/117/25/6, lowest 890 @ 0.923099).
- `tools/compare_interfaces.py --report <tmp>` → exit 0, both fixtures PASS; the regenerated report is **byte-identical** to the committed blob at both the inputs revision and HEAD (SHA-256 `578d56f9a4d024205e9f652b49e17371da2b58b74b49191c639905595ab8c97a`).

## Troubleshooting records — all 16 reproduced in disposable contexts

Every `confirmed` record was re-observed on the pinned stack in a fresh context (IEEE 13 cases on a checksum-verified temporary copy of the redirect tree; LoadShape cases on fresh circuits), matching the recorded symptom, exact exception text, and safe fix:

- `ts-tapnumber-not-indexed`: element-walk `RegControls.TapNumber()` → `[9, 9, 9]`; named queries → `9/6/9`; with reg2 selected, `TapNumber(7)` returned `None` and moved the tap 6 → 7.
- `ts-dss-text-command-property`: `dss.Text.Command("Solve")` → `TypeError: 'str' object is not callable`; `Text.Commands("Solve")` converged.
- `ts-dss-solution-via-active-circuit`: `dss.Solution` → `AttributeError: 'IDSS' object has no attribute 'Solution'`; `dss.ActiveCircuit.Solution` is an `ISolution`.
- `ts-totaliterations-accessor-casing`: `Solution.TotalIterations` → `AttributeError` on dss-python; `Totaliterations` returned 2; `odd.Solution.TotalIterations()` works.
- `ts-active-class-first-property`: dss-python `ActiveClass.First` is `int` 1 (calling it → `TypeError: 'int' object is not callable`); `odd.ActiveClass.First()` returns 1.
- `ts-losses-watts-vs-kilowatts`: `Line.650632` `Losses()` ≈ `[60727, 195981]` **W/var** (raw magnitude ≫ 1000, so W not kW); divided by 1000 it reconciles with the terminal `TotalPowers` sum to < 1e-8.
- `ts-controlled-solve-retaps`: reg2 tap 5 after write → 6 after controlled `Solve()` → held 5 after `SolveNoControl()` with Static still selected.
- `ts-ptphase-out-of-range`: `PTPhase=7` reads back `1` in both the typed getter and the `?` text query.
- `ts-capacitor-no-spectrum`: `hasattr(Capacitors, "Spectrum")` False vs `Loads` True on **both** dss-python and altdss.
- `ts-python-context-isolation`: a second empty AltDSS context raised `(#8888) There is no active circuit!` while the first held 38 elements; in one process, dss-python and opendssdirect saw the same circuit name and each other's elements, and a duplicate `New Vsource.source` raised `(#266)`.
- `ts-loadshape-new-duplicates`: `ctx.LoadShape.new("s1")` on an existing 3-point `s1` returned NPts 0, the collection enumerated NPts `[3, 0]`, and `ctx.LoadShape["s1"]` still returned the 3-point original.
- `ts-loadshape-lowercase-new`: `ctx.LoadShape.New("x")` → `AttributeError: 'ILoadShape' object has no attribute 'New'`; `.new` is callable.
- `ts-loadshape-missing-csv`: `csvfile="phase45_missing_loadshape.csv"` raised `(#613) Error opening file: "phase45_missing_loadshape.csv"` at the assignment — checked **separately** from the statistics error; a fresh shape's `CSVFile` getter returns `''`.
- `ts-loadshape-empty-statistics`: fresh shape — `CSVFile` `''`, `Mean` 0.0, next `CSVFile` read raised `(#61107) LoadShape has no data to be normalized…`, and the following read returned `''` again.
- `ts-loadshape-pmult-length`: all three writes (before `NPts`, too short, too long) raised `#20200425` with the exact "Expected N elements, got M" text; rejected edits preserved `[1,2,3,4]`.
- `ts-loadshape-npts-without-array`: on a **fresh** shape only (no populated buffer was read at an invalid size), bare `NPts=4` left `PMult` an empty array; the first full write then read back `[1,2,3,4]` — matching the record's own re-observation.

Schema guardrails re-verified through the same registry `validate_catalogs.py` builds: the committed catalog validates; an undeclared `resolution` field, an invalid `tested.result` value, and an invented `resolved` status are each rejected (`unevaluatedProperties: false` intact). All 16 records are `confirmed` / `Observed-working` with a `tested` block carrying `result: "pass"` and the pinned environment. No record cites an EPRI page for wrapper or engine behaviour; sources are tagged upstream URLs or repository paths.

## Documentation pass and 4.4 dispositions

- Library README now states 144 `dss_capi` records, 19 examples, lists `regcontrols/`, `loadshapes/`, `fixtures.json`, `python_interface_comparison.json`, the fixtures tree and all five runners (including `readback_regcontrol.py` / `readback_loadshape.py`), and says only `opendss_objects` remains empty — verified against the actual catalogs (144 / 19 counts match `validate_catalogs.py` output).
- Root README and `docs/phase_4/README.md` describe 4.1–4.4 as delivered and 4.5 as the exit package under QA/QC; the phase-4 design's §12 now points at the delivered `exit_checklist.md` instead of restating the checklist inline.
- 4.4 architect observations all dispositioned: **O-1** and **O-2** in `docs/workflows/cross_interface.md` (report described as a result summary with goldens linked for full snapshots; the example described as a driver), **O-3** resolved by adding the single enum value `python_cross_interface` to `examples.schema.json` with exactly one catalog change (`ieee13-snapshot-cross-interface`.language), **O-4** by describing `verify_loss_scale` as a magnitude heuristic next to the accessor unit contracts.
- The two additive schema changes are exactly one line each (`issue.schema.json` gains the `tested` `$ref`; `examples.schema.json` gains one enum value). `skill.md` now points at the fixture runner and exit checklist.

## Exit checklist and scope

All six rows of `docs/phase_4/exit_checklist.md` map to a runnable command and a recorded artifact, and I re-ran each command myself (rows 1–4 and 6 above; row 5 is this report plus the architect's manifest reconciliation, which the checklist correctly marks pending). The scope-limit section states what Phase 4 does **not** cover: no year-long QSTS, harmonics, or unbalanced-fault study; the daily profile exists on ieee13 only; deferred classes per decision 17; `opendss_objects` remains empty for Phase 5. Counts and status are consistent: 18 schema pairs, 19 examples, 3 fixture checks, 16 confirmed troubleshooting records, phase_4 `in-progress` in the manifest pending this sign-off and owner acceptance, plan at v0.39 ("4.1–4.4 accepted; 4.5 issued").

## Hash proof and baseline preservation

- All three revision-1 goldens are byte-identical across the inputs revision `cc8aa92`, HEAD and the working tree: ieee13 snapshot `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4`, ieee13 daily `0f8d5400e4558223dcd19d16a0e9a6370bc07e2e6f7bed3d6bf5a284541012f2`, ieee34 snapshot `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f`. The comparison report blob is likewise unchanged (`578d56f9…`).
- `git diff cc8aa92..2c51fc1` touches exactly 13 files, all inside `docs/`, `references/`, the root README and the library README/skill; the entire fixture tree (`examples/fixtures/`) is untouched, as are `manifest.json` and `docs/implementation_plan.md` (architect-owned — the coder correctly left them alone; `manifest.validation.runtime` already records the 19 examples, three fixture runs and the cross-interface scope limit as of 4.4, and the architect's final reconciliation lands with owner acceptance). Under `references/` only `troubleshooting.json` (`[]` → 16 records) and the single `language` value in `examples.json` changed; under `schemas/` only the two one-line additive changes. `run_fixtures.py`, `compare_interfaces.py` and every accepted catalog are untouched.

## Required corrections

None.

Owner acceptance of the exit package can follow this sign-off and the architect review; the remaining step after that is the architect's manifest/plan status reconciliation (phase_4 → complete, plan version bump) and the owner merge decision.

No files were modified by this review; this report is the only file added.
