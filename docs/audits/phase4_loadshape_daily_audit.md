# Phase 4.3 LoadShape and daily profile build audit

- **Validation date** 2026-11-22
- **Inputs revision** `5efeaf1a97f4a63b5f4ec828cc63df71ded4ee2e` on `wp/phase4`
- **Result** Coder validation passed. [Coder handoff](../handoffs/Phase_4_LoadShape_DailySeries_Coder_handoff.md) · [Workflow](../workflows/loadshape.md) · [LoadShape readback matrix](phase4_loadshape_readback.json)

## Environment and sources

| Item | Recorded value |
| --- | --- |
| Platform | Windows 11 AMD64 |
| Python | 3.14.6 |
| AltDSS-Python | 0.2.4 |
| DSS-Python | 0.15.7 |
| DSS-Python backend / DSS C-API | 0.14.5 |
| jsonschema | 4.26.0 |

Validation reused the pinned Phase 4 environment. The EPRI LoadShape page documents the property vocabulary, interval conventions, and file forms. The AltDSS-Python public documentation showed 0.2.3 and the repository release entry showed 0.2.4. Its release notes describe engine synchronization and a Bus collection change. The DSS C-API 0.14.5 release covers a LineGeometries correction and header changes. The catalog's 22 keys match the 0.2.4 wrapper. All 133 row citation occurrences have version-pinned, in-bounds line ranges. [EPRI LoadShape](https://opendss.epri.com/LoadShape.html) · [AltDSS documentation and changelog](https://dss-extensions.org/AltDSS-Python/changelog.html) · [AltDSS-Python releases](https://github.com/dss-extensions/AltDSS-Python/releases) · [DSS C-API 0.14.5 release and changelog](https://github.com/dss-extensions/dss_capi/releases/tag/0.14.5)

## Commands and results

Run from the repository root with the pinned environment active.

~~~powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
python -B opendss_altdss_library/tools/run_fixtures.py --fixture ieee13 --scenario daily --report phase43-daily-diff.json
$observed = (& python -B opendss_altdss_library/tools/readback_loadshape.py) -join "`n"
if ($LASTEXITCODE -ne 0) { throw 'LoadShape readback failed.' }
$expected = (Get-Content -LiteralPath docs/audits/phase4_loadshape_readback.json) -join "`n"
if ($observed -cne $expected) { throw 'LoadShape matrix differs.' }
git diff --check
~~~

The readback matrix reproduces exactly on the captured stack after normalizing text line endings. On a later date, substitute the committed capture date on the `environment.date` line before the text comparison.

The initial generation used the recorded Package 4.3 coding release approval at daily revision 0. To reproduce revision 1, start with a disposable tree where that initial catalog state is committed and the daily golden is absent. [Fixture catalog](../../opendss_altdss_library/references/fixtures.json)

~~~powershell
python -B opendss_altdss_library/tools/run_fixtures.py --fixture ieee13 --scenario daily --update-golden --reason "Initial IEEE 13 daily golden for Phase 4 package 4.3"
~~~

| Check | Result |
| --- | --- |
| Catalog validation | 18 of 18 schema pairs passed. |
| Examples | 18 ran successfully. Both new examples verified hours 1–3 at 50, 100 and 150 kW. The dedicated readback checks DSS monitor samples. |
| Fixture comparisons | IEEE 13 snapshot, IEEE 13 daily and IEEE 34 snapshot matched their goldens. |
| Reproducibility | A second generation in a disposable Git tree produced the identical daily golden. The tool also ran by absolute path from outside that tree. |
| Invalid cases | Missing reason, wrong approval, a request for IEEE 34 daily, invalid energy, and the wrong peak hour all failed. Changing one hourly voltage generated the expected single-path diff. |
| Snapshot update compatibility | The prior targeted snapshot update command advanced only IEEE 13 to a disposable revision 2. The daily golden and IEEE 34 golden stayed byte-identical. Full compare then passed. |
| Scope | The two RegControl changes are confined to the requested F-1 clause and sentence. Prior catalog records, upstream fixture inputs, the RegControl matrix, and the implementation plan and manifest were preserved. |

## IEEE 13 daily golden

The synthetic residential-style profile ranges from 0.60 to 1.16 and is applied to all 15 loads as `Load.daily`, with `UseActual=False`. Daily mode uses Static controls, starts at hour zero and runs one 3,600-second solution per readback. All 24 hours converged. The three regulator tap ranges were 7–11, 6–7, and 7–11. Both capacitor banks held state `[1]` throughout. The peak step records 16 buses and 38 circuit elements.

| Quantity | Result |
| --- | --- |
| First step | Hour 1, 2,399.365305 kW |
| Peak step | Hour 18, 4,004.670550 kW |
| Lowest bus sample | Bus 611, 0.952044439 pu at hour 18 |
| Load energy from the solve loop | 73,416.54014883187 kWh |
| Load energy reconstructed from recorded steps | 73,416.54014883189 kWh |

The peak hour is derived from the maximum recorded load kW. The integral uses each step's load kW multiplied by the step length in hours. The two stored energy values agree within the fixture tolerance. The fixture checks use the same exact and numeric comparisons as the snapshots. [Daily golden](../../opendss_altdss_library/examples/fixtures/ieee13/golden_daily.json) · [Result format](../phase_4/README.md#51-daily-profile-golden-package-43)

SHA-256 verification compared each baseline Git blob with the working-tree file before and after the daily generation.

| Golden | SHA-256 |
| --- | --- |
| IEEE 13 snapshot revision 1 | `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4` |
| IEEE 34 snapshot revision 1 | `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f` |
| IEEE 13 daily revision 1 | `0f8d5400e4558223dcd19d16a0e9a6370bc07e2e6f7bed3d6bf5a284541012f2` |

## Findings from the pinned readback

- `PMult` writes before `NPts`, or with too few or too many values, returned `#20200425`. Growing `NPts` changes the count without reallocating populated buffers. The matrix verifies the supported replacement-and-rebind workflow from four to six points and records the unsafe resize path from source.
- A fresh `CSVFile` read succeeds. Calling `Mean` or `StdDev` on an empty shape returns zero and queues `#61107`. The next checked read surfaces it. The matrix includes the exact error and the succeeding filename read.
- Normalization uses `PBase` and `QBase` when positive and the absolute sample peaks otherwise. `PMax` and `QMax` report the active peak and corresponding reactive sample. Explicit bases produced a normalized peak of 2, and the action cleared `UseActual`. A separate actual shape supplied 50 kW and 10 kvar at hour 1 despite explicit normalization bases of 200 kW and 100 kvar.
- The Python typed `Hour` setter preserves `Interval`. Writing `Hour=(...)` in DSS text switches the interval to zero. One solve with `Number=24` advanced from hour 0 to 24, while both standalone examples verified the first three samples with `Number=1`.

File reads, memory mapping, binary saves, and nondefault interpolation have pinned source coverage. Runtime validation exercised the standard in-memory shape paths. The Package 4.5 plan and manifest reconciliation remains scheduled for the exit pass.
