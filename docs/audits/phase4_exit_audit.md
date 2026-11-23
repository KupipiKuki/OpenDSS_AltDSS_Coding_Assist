# Phase 4.5 exit build audit

- **Validation date** 2026-11-22
- **Inputs revision** `cc8aa92ecaf14bbc4f54a2ee78b177adbf130bb8` on `wp/phase4`
- **Result** Coder validation passed. The troubleshooting catalog contains 16 confirmed issues. Independent QA/QC, architect reconciliation of the plan and manifest, and owner acceptance are pending. [Coder handoff](../handoffs/Phase_4_Exit_Coder_handoff.md) · [Exit checklist](../phase_4/exit_checklist.md)

## Environment

| Item | Recorded value |
| --- | --- |
| Platform | Windows 11 AMD64 |
| Python | 3.14.6 |
| AltDSS-Python | 0.2.4 |
| DSS-Python | 0.15.7 |
| DSS-Python backend and DSS C-API | 0.14.5 |
| OpenDSSDirect.py | 0.9.4 |
| jsonschema | 4.26.0 |

The troubleshooting rechecks used isolated contexts on the pinned Phase 4 stack and a temporary copy of the verified IEEE 13 redirect tree. The exit harness runs used a fresh virtual environment installed from the validation requirements.

Schema validity checks record structure. Runtime evidence comes from the rechecks, examples, and fixture runs below. The behavior records use direct observations and tagged engine or wrapper source. No engine behavior was inferred from an EPRI page.

## Validation commands and output

Run from the repository root with the fresh validation environment active. During this audit the interpreter was launched by its full path. The comparison report was written outside the repository and compared as raw bytes with the accepted Git blob.

~~~powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
$report = Join-Path ([IO.Path]::GetTempPath()) 'phase4-exit-interface-report.json'
python -B opendss_altdss_library/tools/compare_interfaces.py --report $report
python -B -c "import pathlib,subprocess,sys; assert pathlib.Path(sys.argv[1]).read_bytes() == subprocess.check_output(['git','show','cc8aa92:docs/audits/phase4_cross_interface_report.json'])" $report
git diff --check
~~~

| Command | Captured result |
| --- | --- |
| `validate_catalogs.py` | `PASS  references/troubleshooting.json  (16 record(s))`, `18/18 schema pairs passed`, `RESULT: PASS` |
| `run_examples.py` | 19 `PASS` entries followed by `RESULT: PASS`. The cross-interface driver ran with evidence label `Observed-working`. |
| `run_fixtures.py` | `PASS ieee13 snapshot` with 16 buses and 38 elements. `PASS ieee13 daily` with 24 hours, 73,416.540 kWh and a peak of 4,004.671 kW at hour 18. `PASS ieee34 snapshot` with 37 buses and 117 elements. |
| `compare_interfaces.py` | `PASS ieee13 snapshot` and `PASS ieee34 snapshot`. All six pairs recorded zero differences and zero nonzero numeric deltas on the shared backend. The reproduced report matched the accepted blob byte-for-byte. |

The report's SHA-256 is `578d56f9a4d024205e9f652b49e17371da2b58b74b49191c639905595ab8c97a`. It records wrapper agreement on the same DSS C-API 0.14.5 engine. Independent numerical validation requires a separate reference. [Accepted comparison report](phase4_cross_interface_report.json)

## Troubleshooting rechecks

The IEEE 13 cases used the pinned redirect entry and a snapshot solve on the named wrapper. The LoadShape cases used a fresh circuit. The context-sharing case deliberately used the default classic instances in the same test process. Exact error messages and safe fixes are stored in the catalog. [Troubleshooting catalog](../../opendss_altdss_library/references/troubleshooting.json)

| Record | Focused command or readback | Observation |
| --- | --- | --- |
| `ts-tapnumber-not-indexed` | Walk `odd.ActiveClass` for RegControl, read `odd.RegControls.TapNumber()`, then query `? RegControl.reg1.TapNum` and repeat for reg2 and reg3. | Cursor reads gave 9/9/9 and name queries gave 9/6/9. With reg2 selected, `TapNumber(7)` set it to 7. |
| `ts-dss-text-command-property` | Call `dss.Text.Command("Solve")` and then `dss.Text.Commands("Solve")`. | The first raised `TypeError` for calling a string and the method solved successfully. |
| `ts-dss-solution-via-active-circuit` | Read `dss.Solution` and `dss.ActiveCircuit.Solution`. | The former raised `AttributeError`. The latter returned an `ISolution`. |
| `ts-totaliterations-accessor-casing` | Read `dss.ActiveCircuit.Solution.TotalIterations`, `dss.ActiveCircuit.Solution.Totaliterations`, and `odd.Solution.TotalIterations()`. | DSS-Python rejected the capitalized spelling. The applicable accessor on each wrapper returned 2. |
| `ts-active-class-first-property` | Read and then call `dss.ActiveCircuit.ActiveClass.First`. Call `odd.ActiveClass.First()`. | DSS-Python's property and OpenDSSDirect.py's method returned 1. Calling the property raised `TypeError` for calling an integer. |
| `ts-losses-watts-vs-kilowatts` | Select `Line.650632` with `odd.Circuit.SetActiveElement`. Compare `odd.CktElement.Losses()` to the terminal sum of `odd.CktElement.TotalPowers()`. | 60,728.502802 W and 195,986.078557 var reconciled after conversion to 60.728503 kW and 195.986079 kvar. |
| `ts-controlled-solve-retaps` | Edit IEEE 13 reg2 to tap 5, solve in Static, then write 5 again and call `SolveNoControl()`. | The immediate read was 5, the controlled result was 6, and the one-off no-control result held 5 with Static still selected. |
| `ts-ptphase-out-of-range` | `Edit RegControl.reg2 PTPhase=7` and `? RegControl.reg2.PTPhase`. | The text and typed getters both returned 1. The cause is the local positive-index guard. |
| `ts-capacitor-no-spectrum` | Check `hasattr(..., "Spectrum")` on Capacitor and Load in DSS-Python and AltDSS. | Capacitor was false and Load was true on both surfaces. |
| `ts-python-context-isolation` | Read `NumCircuitElements` in a second AltDSS context. Create a circuit through default DSS-Python and a load through default OpenDSSDirect.py in the same process. | The first AltDSS context had 38 elements and the second raised `#8888`. Both classic facades saw the same circuit and load. A duplicate circuit command raised `#266`. |
| `ts-loadshape-new-duplicates` | `New LoadShape.s1 npts=3 pmult=[1,2,3]`, then `ctx.LoadShape.new("s1")` and `ctx.LoadShape["s1"]`. | The constructor returned zero points, the collection contained 3- and 0-point entries of that name, and lookup returned the original 3-point shape. |
| `ts-loadshape-lowercase-new` | Call `ctx.LoadShape.New("x")` and check that `ctx.LoadShape.new` is callable. | Uppercase `New` raised `AttributeError`. |
| `ts-loadshape-missing-csv` | Create a three-point shape with `CSVFile` pointing at a missing file in the scratch directory. | The creation command immediately raised `#613`. |
| `ts-loadshape-empty-statistics` | On a fresh shape, read `CSVFile`, then `Mean`, then `CSVFile` twice. | The first file read returned an empty string and the mean returned 0.0. The next read raised `#61107` and the following read returned an empty string. |
| `ts-loadshape-pmult-length` | Write a two-value `PMult` at `NPts=0`. On a populated four-point shape attempt two values and five values. | All three writes raised `#20200425`. Rejected edits preserved the four original samples. |
| `ts-loadshape-npts-without-array` | Set `NPts=4` on a fresh shape, read `PMult`, then write `[1, 2, 3, 4]` and read again. | The first array was empty and the second contained all four values. The probe used a fresh buffer. Use a replacement when increasing the size of a populated shape. |

## Documentation and schema dispositions

| Item | Change |
| --- | --- |
| 4.4 O-1 | The workflow identifies the comparison report as a result summary and links the separate fixture goldens for complete snapshots. |
| 4.4 O-2 | The workflow identifies the IEEE 13 example as a small driver and points to the accessor table for explanation. |
| 4.4 O-3 | The existing example language enum adds `python_cross_interface`. Only the IEEE 13 comparison driver's `language` field changes in the accepted example catalog. All 19 examples executed through the existing runner. |
| 4.4 O-4 | The workflow describes `verify_loss_scale` as a magnitude heuristic and records the accessor units separately. |

The handoff requires `tested` on confirmed issues, but the issue schema omitted that property and rejected it under `unevaluatedProperties: false`. The issue schema now references the existing common `tested` definition. Validation still rejects an undeclared `resolution` field and an invalid `tested.result`. The example enum and issue property are the two additive schema changes. [Issue schema](../../opendss_altdss_library/schemas/records/issue.schema.json) · [Example schema](../../opendss_altdss_library/schemas/catalogs/examples.schema.json)

The documentation pass updates both READMEs and the library instructions with the delivered harnesses. The Phase 4 design links the delivered artifacts and corrects the daily `States` description to count configured steps. The accepted engine data, fixture runners, and comparison code were preserved. The manifest and plan remain with the architect for final status reconciliation.

## Baseline preservation

All 15 tracked fixture-tree files matched their baseline blobs byte-for-byte. SHA-256 of every previously populated reference catalog matched after accounting for Git text line endings, with the single example classification change verified by restoring that value in memory and comparing the bytes. The three revision 1 goldens retained the hashes below.

| Golden | SHA-256 |
| --- | --- |
| IEEE 13 snapshot | `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4` |
| IEEE 34 snapshot | `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f` |
| IEEE 13 daily | `0f8d5400e4558223dcd19d16a0e9a6370bc07e2e6f7bed3d6bf5a284541012f2` |
