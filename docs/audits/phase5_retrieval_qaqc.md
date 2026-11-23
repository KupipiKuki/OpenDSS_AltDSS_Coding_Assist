# Phase 5.2 retrieval tool — Independent QA/QC Report

**Reviewed branch:** `wp/phase5` (tip `9e2628d`, synced with `origin/wp/phase5`; the tip is docs-only — it pins the handoff's package-revision line, verified by `git diff 4b4430b..9e2628d`, one line in the QA/QC handoff). **Package revision under review:** `4b4430b4869f02514111243f3bb998c4ba57b613` (per the pinned handoff at `9e2628d`). **Inputs/baseline revision:** `02fe261e87018d1287a64af21ef9ffc92369a2d5`. **Reviewed state:** `git status --porcelain` clean; `git diff --check 02fe261..9e2628d` clean.
**Review date:** 2026-11-23. **Reviewer environment:** venv from `tools/requirements-validation.txt`, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, backend `0.14.5`, `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`; retrieval probes additionally ran under `python -S -B`, proving the tool is standard-library only (argparse/json/re/difflib/collections/dataclasses/pathlib).

**STATUS:** PASS (no blocking findings; no required corrections)

## The six workflow queries (all exit 0, output matches `docs/workflows/retrieval.md`)

- `--symbol TapNumber` → exactly three alias hits, each labeled `canonical=TapNum` with its citation: `altdss.RegControl:RegControl.TapNum` (API property, tag 0.2.4), `capi-regcontrol-tap-number` (engine record, tag 0.14.5), and `RegControl.tapnum` (element property, `dss=tapnum python=TapNum`) — the classic TapNumber alias is explicit, not silent.
- `--symbol Conductors` → exactly two hits, `LineGeometry.wires` and `Line.wires`, each printing `dss=wires python=Conductors`; in `--json` each carries its generated API property under `related_api` (`altdss.LineGeometry:LineGeometry.Conductors`, `altdss.Line:Line.Conductors`). Both keyword pairs confirmed.
- `--class PVSystem` → the single deferred object record with its EPRI pointer, `status: deferred`, no property catalog row — correct per decision 17.
- `"manual tap static" --class RegControl --evidence observed-working` → `ts-controlled-solve-retaps` in the troubleshooting catalog, with the repository path `docs/workflows/regcontrol.md` printed as recorded (not urlparsed). The `--evidence` label matched case-insensitively across both spellings (`evidence_label`/`evidence_level` are normalised in the adapter; no catalog was edited).
- `"cable modeling technote" --version 0.14.5` → the `TSData` object record and `epri-tsdata-cable-modeling` source both survive with `version=unstated` (records with no stated version are kept, so the null-`version_or_ref` EPRI sources are not erased).
- `--symbol IRegControl --class regcontrol --json` → exit 0; the class filter resolves case-insensitively through the object index and surfaces the `altdss.RegControl:IRegControl` collection class.
- Exit codes: unknown class `--class NotAClassy` → **2** with `Did you mean AutoTrans, CNData, LoadShape?`; no-hit query → **1**; unknown flag → **2**; invalid `--evidence` label → **2** with the enum; a missing catalog file in a copied library → **2** with the file named.

## `--stats` and determinism

- `--stats` prints 926 addressable records across 17 files (2200 including API members), 16 element classes / 461 property rows, 180 API methods / 1094 API properties. My independent count from the files gives identical numbers: 449 base records (132+19+99+144+24+13+16+2) + 16 element class records + 461 property rows = 926; +180+1094 = 2200 searchable. All measured at run time, not hard-coded.
- Two runs of `--symbol Conductors --json` are **byte-identical** (SHA-256 `fb7bccf650fb8436370f15fa0425f0a28c2b79215902a7d8aebd2f06b31f9570`, matching the build audit), and parsed hits are already sorted by `(catalog, record_id, field)` — verified programmatically.

## `--check` (object-index carry-forward from 5.1)

- On the committed index: `Object index check: PASS`, exit 0. The checker re-derives every `property_catalog` count, `engine.record_count`, `example_ids`, `fixture_usage` (golden element maps + entry-script Circuit/LineCode + `fixtures.json` daily LoadShape assignment), and all workflow/readback/source pointers — the same rules as my 5.1 re-derivation.
- In a disposable worktree at `4b4430b`, editing RegControl's `property_row_count` 35→36, `engine.record_count` 15→99, and removing `ieee13 daily` from `fixture_usage` produced exit **1** with all three named diagnostics:
  - `RegControl.property_catalog.property_row_count: recorded 36, derived 35`
  - `RegControl.engine.record_count: recorded 99, derived 15`
  - `RegControl.fixture_usage: recorded ['ieee13 snapshot', 'ieee34 snapshot'], derived ['ieee13 daily', 'ieee13 snapshot', 'ieee34 snapshot']`
- Restoring the file bytes returned the check to PASS (exit 0); the committed index was never modified.

## Regression harnesses and protected artifacts

- `validate_catalogs.py` → 18/18 schema pairs PASS; `run_examples.py` → 19/19 PASS; `run_fixtures.py` → 3/3 PASS.
- `git diff 02fe261..9e2628d` touches exactly the six declared files: `tools/search_catalogs.py`, `docs/workflows/retrieval.md`, `docs/audits/phase5_retrieval_audit.md`, the handoff pin, and one-line additions in the library README and `skill.md`. No catalog, schema, example, fixture, golden, tool other than the new one, `requirements-validation.txt`, `manifest.json`, or `docs/implementation_plan.md` changed — all protected artifacts are byte-identical to the inputs revision.

## Limitations (as documented, confirmed)

- The tool is a reader over the committed catalogs: no ranking or fuzzy matching, no web retrieval, no cache/index file of its own, no writes. Scope is `references/**` only; prose under `docs/` is not indexed. Engine namespaces that are internal type names (`TLineObj` etc.) are searchable as namespaces without implying a public DSS class. Release packaging is package 5.3.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
