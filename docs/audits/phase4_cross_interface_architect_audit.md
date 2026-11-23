# Phase 4.4 cross-interface comparison — Architect/Auditor Review

**Reviewed branch:** `wp/phase4`, tip `0b1c085` (QA/QC report commit), clean working tree at review start.
**Package revision under review:** `159fce02c6a1753ea84933441f2f74f6e8f4dc88` (comparison tool, accessor catalog, workflow, example, report, requirements).
**Inputs/baseline revision:** `5e323265cda7447f8e933231014b5ffe1ce4db3c`.
**Review date:** 2026-11-22 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`, `jsonschema 4.26.0`; the reviewer installed `opendssdirect.py 0.9.4` into the validation environment to reproduce the run, which resolves the already-pinned `dss-python 0.15.7` and changes nothing else.

**STATUS:** PASS (no required corrections; four observations)

## Run verification (reproduced by me, not taken from the report)

| Check | Result |
|---|---|
| `tools/compare_interfaces.py --report <tmp>` | exit 0 in 6.9 s; **report byte-identical to the committed `phase4_cross_interface_report.json`** |
| `tools/validate_catalogs.py` | 18/18 pairs, PASS — including the now-populated `references/python_interface_comparison.json` (13 records) against the existing schema |
| `tools/run_examples.py` | 19 examples PASS, including `ieee13-snapshot-cross-interface` |
| `tools/run_fixtures.py` | 3/3 PASS — ieee13 snapshot, ieee13 daily, ieee34 snapshot |
| Golden freeze | `f72d59d8…ef5f4`, `b06282a6…2709f` and `0f8d5400…8223` are identical in the baseline blob, the current blob and the working tree |

Both fixtures compare clean: `ieee13` 16 buses / 38 elements / 2 total and 1 control iterations; `ieee34` 37 / 117 / 25 and 6; three pairs per fixture; **zero out-of-tolerance differences and zero nonzero numeric deltas**, meaning the three surfaces are numerically bit-identical. Taps agree as 9/6/9 on `ieee13` and 14/4/5 and 13/13/13 on `ieee34`.

## The premise is stated, and it is load-bearing

Every interface reports the same engine build line: `DSS C-API Library version 0.14.5 revision 87d85c2622c8281b92255335bc7c09b11191b21d …`. The scope sentence — *"A pass demonstrates wrapper agreement only. Independent numerical validation is outside this comparison."* — appears in the tool's `SCOPE` constant, in its printed output, in the report's `scope` field and in the argparse epilogue, and is restated in the workflow page's first paragraph and in the build audit's result line. Acceptance item 5 is met in four places rather than one.

I confirmed the facade relationship independently when issuing this package: `opendssdirect.py 0.9.4` declares `dss-python==0.15.7` and its wheel imports `dss` and `dss_python_backend`. Nothing in the package overstates what the result means.

## Guards actually bite

I tested the comparison machinery directly rather than trusting that a green run implies a working assertion:

| Seeded change | Result |
|---|---|
| Wrapper version line differs, values identical | pass — correct, wrapper identity is excluded by design |
| One bus `pu_vmag` shifted by 1e-3 | **fail**, `buses/611/pu_vmag/0` reported |
| `RegControl.reg1` tap 8 versus 9 | **fail** |
| One totals value wrong | **fail** |
| `verify_loss_scale` given W-scale losses (112391.709 with 3567 kW supplied) | **raises**, naming the expectation |

`comparison_pair` compares the full worker snapshots, so bus voltages, element powers and losses are all in scope; the report stores summaries plus diffs rather than the full snapshots. The excluded key is `version` only — `engine_version` (the first line, the engine build) is compared, which is what makes the shared-backend claim checkable rather than asserted.

## Process isolation and accessor mapping

- Each interface runs in its own subprocess (`sys.executable -B compare_interfaces.py --worker <iface>`, request on stdin, 60 s timeout), each with its own `TemporaryDirectory` holding a checksum-verified copy of the redirect closure and `cwd` set to it. This is the trap I flagged in the handoff and it is handled at the process boundary, not papered over.
- The accessor split is implemented the way the catalog describes: `dss-python` reads through properties (`getattr`/`setattr`, `Text.Command = …`, `Totaliterations` with lower-case `i`, `Tolerance`), `opendssdirect` through methods (`Text.Command(…)`, `TotalIterations()`, `Convergence(tol)`).
- **Taps are read by the text query** `? {name}.TapNum` on both classic surfaces and by `reg.TapNum` on altdss — the route I verified as the only trustworthy one. The workflow states why: the active-class probe returned 9, 9, 9 through `RegControls.TapNumber` while the true taps are 9/6/9.
- Names are casefolded for matching and duplicates are rejected, so the comparison is name-keyed rather than index-keyed.
- `Losses` is scaled by `0.001` at the boundary with the comment "TotalPowers is already kW/kvar. Losses is W/var", and `verify_loss_scale` backstops it.

## Catalog claims checked against the installed packages

I verified all 13 concepts live rather than reading them: `ctx.TextResult` exists and reads `''`; `dss.Text.Command = cmd` genuinely executes (38 elements present afterwards); `dss…Solution.Totaliterations` is spelled with lower-case `i` and returns 2; `Solution.Tolerance` reads 0.0001 while `odd.Solution.Convergence(0.0001)` is a method that reads back 0.0001; `dss…ActiveClass.First` is an `int` property while `odd.ActiveClass.First()` is callable; `odd.Capacitors.Name("cap1")` then `States()` returns `[1]`; and the tap query returns `6` for `reg2` through the property-assignment form. Every row matched. All 8 new `sources.json` records are pinned to tags or release pages and none were removed (119 → 127).

## Observations recorded without action

- **O-1.** The committed report holds per-interface summaries (version, solver, totals, controls, counts) plus the diffs and deltas, not the full snapshots. That is a defensible size choice and the tool reproduces the file byte-identically, but it means a reader cannot re-verify agreement from the artifact alone — they must re-run. Package 4.5's documentation pass should describe it as a result summary rather than a snapshot set, so nobody later treats it as evidence of the level the goldens provide.
- **O-2.** `examples/interfaces/compare_ieee13.py` is a nine-line driver that shells out to the tool and relies on its exit code. It validates the comparison but teaches nothing about the accessor differences; that knowledge lives in the workflow table. Acceptable split, worth knowing before someone reads the example as the tutorial.
- **O-3.** The new example is recorded with `language: "python_altdss"` because `examples.schema.json` offers only `dss`, `python_altdss`, `python_dss` and `python_opendssdirect`. A three-interface driver is none of those. Either add a cross-interface value in 4.5 or annotate the record; as it stands the field is the least accurate statement in the package.
- **O-4.** `verify_loss_scale` is a magnitude heuristic — losses must be below the supplied source kW — rather than a unit assertion. It catches the 1000× error on these loaded feeders, which is the failure that actually happens, but it would pass on a feeder with near-zero losses. Fine as a backstop, not a proof of units.

## REQUIRED CORRECTIONS

None. No files were modified by this review other than the report this audit adds.

| Scope item | Verdict |
|---|---|
| Both fixtures across three interfaces, exit 0 | met, reproduced |
| Goldens and fixtures byte-identical | met, proven by hash |
| Accessor catalog non-empty, schema-valid, matches code | met, 13 records verified live |
| Scope limitation stated in tool, workflow, catalog, audit | met in four places |
| Tap read by a route reproducing 9/6/9 | met, with the reason documented |
| `Losses` conversion visible and backstopped | met |
| Diff confined to `docs/`, `references/`, `examples/`, `tools/` | met, 11 files |
