# Phase 4.4 cross-interface comparison — Independent QA/QC Report

**Reviewed branch:** `wp/phase4` (tip `5328247`, synced with `origin/wp/phase4`; the tip is docs-only — it pins the handoff's package-revision line, verified by `git diff 159fce0..5328247`, one line in the QA/QC handoff). **Package revision under review:** `159fce02c6a1753ea84933441f2f74f6e8f4dc88` (per the pinned handoff at `5328247`). **Inputs/baseline revision:** `5e323265cda7447f8e933231014b5ffe1ce4db3c`. **Reviewed state:** `git status --porcelain` clean; `git diff --check 5e32326..5328247` clean.
**Review date:** 2026-11-22. **Reviewer environment:** fresh venv installed from `tools/requirements-validation.txt` (now including `opendssdirect.py==0.9.4`), Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine self-reports `DSS C-API Library version 0.14.5 revision 87d85c2622c8281b92255335bc7c09b11191b21d`), `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`; wrapper sources = installed wheels at the pinned versions.

**STATUS:** PASS (no blocking findings; no required corrections)

## Run verification (fresh environment, `python -B` from the repo root)

- `tools/compare_interfaces.py --report …` → exit 0. Both snapshot fixtures PASS through all three interfaces; the regenerated report is **byte-identical** to the committed `phase4_cross_interface_report.json` (SHA-256 `578d56f9a4d024205e9f652b49e17371da2b58b74b49191c639905595ab8c97a`, matching the build audit). The report records **six worker results** (2 fixtures × 3 interfaces, each with its full version string, solver echo, summary, totals and controls) and **three pairwise comparisons per fixture** (`altdss`×`dss_python`, `altdss`×`opendssdirect`, `dss_python`×`opendssdirect`), all pass with 0 out-of-tolerance diffs and 0 nonzero numeric deltas. ieee13 taps 9/6/9 and ieee34 taps 14/4/5/13/13/13 in full-name order on all three interfaces; 16/38/2/1 and 37/117/25/6 match the fixture goldens' counters.
- `tools/validate_catalogs.py` → exit 0, **18/18 schema pairs**, including the now-populated `references/python_interface_comparison.json` (13 records) against the **existing** `python_interface_comparison` schema (no schema change).
- `tools/run_examples.py` → exit 0, **19/19 PASS**, including the new `ieee13-snapshot-cross-interface` (Observed-working).
- `tools/run_fixtures.py` → exit 0, **3/3 PASS** (ieee13 snapshot, ieee13 daily, ieee34 snapshot) — the golden checks are unaffected by the package.

## Pins, dependency chain, and process boundaries

- Each worker's version string contains `DSS C-API Library version 0.14.5 revision 87d85c2…`; the tool asserts this per interface (`verify_engine`) and the report compares the full engine build line exactly (only the wrapper-identification `version` field is excluded from pairwise comparison). All three report the identical engine build line.
- `opendssdirect.py 0.9.4` wheel metadata declares `dss-python==0.15.7` (confirmed via `importlib.metadata.requires`), so all three interfaces resolve to one backend — the facade relationship is real, and the tool's header, printed `SCOPE`, and report `scope` all state that a pass demonstrates wrapper agreement only, not numerical validation. The same caveat appears in the workflow page, the catalog's first record notes, and the build audit.
- The manifest pin `support_targets.opendssdirect_py = "0.9.4"` pre-existed at the inputs revision and is asserted against the installed version at runtime; `manifest.json` is unchanged by the package.
- Worker boundaries: each interface runs in its own subprocess (`sys.executable -B compare_interfaces.py --worker <iface>`, request on stdin, 60 s timeout), each with its own `TemporaryDirectory` holding a checksum-verified copy of the fixture's full redirect closure (`checked_inputs`), `cwd` set to that directory — so the shared-state hazard between `dss` and `opendssdirect` (both importable as `dss`) cannot occur. `--report` is rejected inside the fixture tree or onto the fixture catalog.

## Catalog vs. tool accessor spellings

- The 13 `python_interface_comparison.json` records were matched row-by-row against `compare_interfaces.py`: `ctx.Version()` / `dss.Version` / `odd.Version()`; `ctx.Commands` + `ctx.TextResult` vs `Text.Command` property + `Text.Result` vs method calls; solver tolerance `Tolerance` vs `Convergence`; `Totaliterations` vs `TotalIterations()`; `NumCktElements`/`AllElementNames`/`SetActiveBus`/`SetActiveElement`/`ActiveBus`/`ActiveCktElement` vs `odd.Bus`/`odd.CktElement` methods; capacitor selection via `Capacitors.Name`/`States`; `ActiveClass.First` property vs method. Every spelling in the catalog matches the code.
- All **70** row `source_refs` are pinned to the three package tags (`AltDSS-Python` `0.2.4`, `DSS-Python` `0.15.7`, `OpenDSSDirect.py` `v0.9.4`) and bounds-checked against the installed wheels (pyproject.toml fetched from the tag) — zero out-of-bounds, zero wrong-tag. Spot check: `OpenDSSDirect.py` `RegControls.py#L267-L279` is exactly the `TapNumber(self, *args)` getter/setter split the catalog warns about.

## Probe reproductions (disposable contexts, pinned stack)

- ieee13 snapshot per interface in separate processes: text queries `? RegControl.<name>.TapNum` returned **9, 6, 9** on both `dss-python` and `opendssdirect`; altdss object properties gave 9/6/9; all converged 2 total / 1 control iteration. Bus 611 reports node `[3]` with one pu/angle pair (0.960842743, 115.738202°) on all three.
- Active-tap hazard reproduced: an opendssdirect element-walk of `RegControls.TapNumber()` returned **[9, 9, 9]** (active-control proxy, reg2's true tap is 6); with `RegControls.Name("reg2")` active, `TapNumber()` returned 6, and `TapNumber(7)` returned **None** while the query showed the tap **changed 6 → 7**. dss-python `TapNumber` is the active-control property (6) and `TapNumber(7)` raises `TypeError: 'int' object is not callable`. The tool uses the named text query on both classic interfaces, as the workflow requires.
- Unit conversion: circuit `Losses` reads W/var (112391.7090551033 W on ieee13) and the tool multiplies both components by 0.001 → 112.391709 kW, matching the golden's `totals.losses_kw`; element `Losses` is likewise converted; `verify_loss_scale` rejects an unconverted W-scale value (0 ≤ losses_kw < |source_kw|). `TotalPower`/`TotalPowers` are already kW/kvar and are normalized from complex/array to (kw, kvar) pairs before comparison.

## Name-order independence, tolerances, and fault injection (disposable worktree at `159fce0`)

- Patching the opendssdirect worker to enumerate buses and elements in **reversed** order still produced exit 0 with 0 diffs on all three pairs — the comparison is name-keyed (casefolded) with duplicate-name rejection, not index-based.
- Tolerances: pairwise comparison reuses `run_fixtures.compare` with the fixture tolerance table — voltages/angles absolute 1e-6, powers relative 1e-6 with 1e-6 kW floor, iteration counts/taps/states exact; `nonzero_deltas` records any nonzero numeric delta (zero-tolerance pass) so sub-tolerance drift stays visible.
- Injecting +0.01 pu into bus `611` `pu_vmag[0]` of the opendssdirect worker readback: CLI **exit 1**, report status `fail`, and exactly the two opendssdirect pairs fail with the fully qualified diff `buses/611/pu_vmag/0` (expected 0.9608427430890604, actual 0.9708427430890604) plus a recorded delta of +0.01; the `altdss`×`dss_python` pair still passed. A wrong engine version string is rejected by `verify_engine` (audit confirmed 0.14.50 fails).

## Hash proof and baseline preservation

- All three goldens are byte-identical across the inputs revision, HEAD and the working tree: ieee13 snapshot `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4`, ieee34 snapshot `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f`, ieee13 daily `0f8d5400e4558223dcd19d16a0e9a6370bc07e2e6f7bed3d6bf5a284541012f2`.
- `git diff 5e32326..159fce0` touches exactly 10 files, all inside `docs/`, `references/`, `examples/`, `tools/`: no schema, no golden, no fixture input, no Phase 3/4.1–4.3 catalog changed. `sources.json` 119 → 127 (+8, zero removed/changed), `examples.json` 18 → 19 (+1 `ieee13-snapshot-cross-interface`, Observed-working with environment block), and `python_interface_comparison.json` went from 0 to 13 records against the unchanged schema. `requirements-validation.txt` gained exactly the commented `opendssdirect.py==0.9.4` line. The 4.3 architect audit (`30aa14a`) was PASS WITH FINDINGS with both findings correcting the architect's own documents, so no rider affects this package.

## Limitations (as documented, confirmed)

- A pass demonstrates API-layer agreement among three wrappers over one DSS C-API 0.14.5 backend; it is not independent numerical validation, which remains the golden-fixture stop gate (design §1). Stated in the tool header/output, the report `scope`, the workflow, the catalog record, and the build audit.
- Comparison covers the snapshot scenario only (per scope); the daily scenario stays with the fixture harness.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
