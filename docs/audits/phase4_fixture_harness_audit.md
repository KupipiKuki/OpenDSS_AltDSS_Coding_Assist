# Phase 4.1 Fixture Harness build audit

- **Date** 2026-11-22
- **Branch** `wp/phase4`
- **Status** Coder validation complete. Independent QA/QC and architect review pending.

## Scope and method

The package adds the IEEE 13-node and IEEE 34-node Mod 1 snapshot fixtures. The fixtures and license came directly from the pinned upstream commit. The two redirect closures retain upstream names and bytes. `wp/phase4` starts at Phase 4 preparation commit `f8fac0c`, which contains the accepted Phase 3 packages and the Phase 4.1 handoff. [Design](../phase_4/README.md) · [Pinned upstream files](https://github.com/dss-extensions/electricdss-tst/tree/3b208397160213cae4a9e2d0a7d1aa3528ce26e1/Version8/Distrib/IEEETestCases)

The fresh validation virtual environment loaded the pinned distributions from the earlier validation environment through a local path entry. Schema validation used jsonschema 4.26.0 with Draft 2020-12 format checking.

```json
{
  "python_version": "3.14.6",
  "altdss_version": "0.2.4",
  "dss_python_version": "0.15.7",
  "backend_version": "0.14.5",
  "platform": "Windows 11 AMD64"
}
```

## Results

| Fixture | Buses | Circuit elements | Converged | Total iterations | Control iterations | Lowest phase voltage |
|---|---:|---:|---|---:|---:|---|
| IEEE 13-node | 16 | 38 | Yes | 2 | 1 | Bus `611`, 0.960843 pu |
| IEEE 34-node Mod 1 | 37 | 117 | Yes | 25 | 6 | Bus `890`, 0.923099 pu |

Both runs used snapshot mode, 15 maximum power-flow iterations, tolerance 0.0001, static controls, 10 maximum control iterations, and 60 Hz. The harness applies options whose values differ and checks all resulting settings. Reassigning the already-active snapshot mode reset the IEEE 13 solve state in a separate probe and led to four iterations. Keeping the existing mode preserved the handoff's two-iteration repeat solve. IEEE 34 needed six control iterations with the recorded limits. [Fixture catalog](../../opendss_altdss_library/references/fixtures.json)

Per-terminal powers follow the engine's into-element sign convention. Total load is summed from solved load terminal powers. The loss fields convert W and var to kW and kvar. Buses carry the engine's node order. The IEEE 13 and IEEE 34 goldens respectively recorded three and six regulator tap numbers and two capacitor state arrays each. The only LoadShape is the built-in `default`. [IEEE 13 golden](../../opendss_altdss_library/examples/fixtures/ieee13/golden.json) · [IEEE 34 golden](../../opendss_altdss_library/examples/fixtures/ieee34/golden.json)

## Committed byte proof

The inputs were committed first at `9736d46a3b30b7c3f7c10322bd3886f61fe78991`. The fixture tree sets `* -text`, and `git check-attr text` reported `unset`. For each upstream path, Python captured raw bytes from `git cat-file -p <revision>:<repo-path>` and checked SHA-256, byte count, and equality to the working copy. This avoids text conversion in the Windows shell pipeline.

| Path under the fixtures tree | Bytes | Committed SHA-256 |
|---|---:|---|
| `License.txt` | 1816 | `f13543277f32a6437d4f583200858f0988d3acc9598a6a1a292d710009ec21ef` |
| `ieee13/IEEETestCases/IEEELineCodes.DSS` | 12032 | `71bc16ef9c6084b9e3bab74fbdf967080b79624683465e1483b787ff160f58b3` |
| `ieee13/IEEETestCases/13Bus/IEEE13Nodeckt.dss` | 8354 | `033ccd4005c6538e9de5b2218e83001802ce14fbc5b6c312896ae8cbc5d4a504` |
| `ieee13/IEEETestCases/13Bus/IEEELineCodes.DSS` | 30 | `40ef533dfcb22738edb1125b1e15e4a1a5d41b2cca4a2f969f5d955c9784daeb` |
| `ieee13/IEEETestCases/13Bus/IEEE13Node_BusXY.csv` | 243 | `f8dd1528c72f339ebf41bf1355ed64ef12fbe30864fcc839ed5e5e9dc527846e` |
| `ieee34/IEEETestCases/IEEELineCodes.DSS` | 12032 | `71bc16ef9c6084b9e3bab74fbdf967080b79624683465e1483b787ff160f58b3` |
| `ieee34/IEEETestCases/34Bus/ieee34Mod1.dss` | 14341 | `648f12f7f611ccf89bce68aea2142f0225ddcba78e81d16bd02e52e3a4b058f8` |
| `ieee34/IEEETestCases/34Bus/IEEELineCodes.DSS` | 30 | `40ef533dfcb22738edb1125b1e15e4a1a5d41b2cca4a2f969f5d955c9784daeb` |
| `ieee34/IEEETestCases/34Bus/IEEE34_BusXY.csv` | 506 | `6e022bbb3adb3c7f29ccb7bbdee2013517ae55e19ad25cda815616c5d4a37958` |

[IEEE 13 provenance](../../opendss_altdss_library/examples/fixtures/ieee13/PROVENANCE.md) · [IEEE 34 provenance](../../opendss_altdss_library/examples/fixtures/ieee34/PROVENANCE.md)

## Acceptance checks

Commands from the repository root in the validation environment:

```powershell
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py --update-golden --reason "Initial snapshot goldens for Phase 4 package 4.1"
python -B opendss_altdss_library/tools/run_fixtures.py
```

The initial update used the approval recorded for the owner's Package 4.1 coding release. It advanced both catalog records from revision 0 to 1 and wrote both goldens. All 16 schema pairs and all 14 existing examples passed. The fixture runner validated both source ID lists.

For determinism, two disposable Git trees were made from `git archive --format=zip 9736d46a3b30b7c3f7c10322bd3886f61fe78991`, with the fixture inputs committed in each test tree. Each used the same harness and initial approval records. In both cases the initial update command and comparison ran by absolute script path from the parent directory, with spaces in the working-tree path. The two generated files matched each other and the package goldens byte for byte.

| Golden | SHA-256 |
|---|---|
| `ieee13/golden.json` | `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4` |
| `ieee34/golden.json` | `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f` |

In a disposable tree, adding 0.01 pu to IEEE 13 bus `611`'s first recorded voltage and running `python -B <absolute-tool-path> --fixture ieee13 --report <report-path>` returned exit 1 and a single JSON value difference at `["buses", "611", "pu_vmag", 0]`. Removing the bus from the golden also failed with an extra-key difference. Replacing a declared checksum with 64 zeroes failed before compilation.

`--update-golden` without a reason returned exit 2. An unmatched reason and a deliberately untracked file inside the disposable fixture tree each returned exit 1 and wrote no golden. The same targeted update with a matching disposable approval and clean fixture inputs advanced IEEE 13 to revision 2, wrote the reason, and preserved IEEE 34 at revision 1. Both disposable results then passed comparison. [Harness](../../opendss_altdss_library/tools/run_fixtures.py)

Package 4.1 covers snapshots on the pinned stack. RegControl catalogue coverage, variable time-series behavior, cross-interface results, and Phase 4 exit remain separate packages. Manifest reconciliation remains in Package 4.5. [QA/QC handoff](../handoffs/Phase_4_Fixture_Harness_QAQC_handoff.md)
