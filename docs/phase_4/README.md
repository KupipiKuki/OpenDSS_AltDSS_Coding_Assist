# Phase 4 — Validation with golden fixtures

**Status** Package 4.1 passed coder validation. Both revision 1 snapshot goldens are recorded and ready for independent QA/QC. [Build audit](../audits/phase4_fixture_harness_audit.md) · [QA/QC handoff](../handoffs/Phase_4_Fixture_Harness_QAQC_handoff.md)
**Governs** [Implementation plan §6](../implementation_plan.md) (intent) · [manifest](../../opendss_altdss_library/manifest.json) (state)
**Pinned stack** AltDSS-Python `0.2.4` · DSS-Python `0.15.7` · DSS C-API backend `0.14.5`; cross-interface checks add `opendssdirect.py` `0.9.4`.

This document resolves the open items in plan §6 and records what was measured rather than assumed. Where §6 and this document disagree, this document is newer and the plan is corrected in the same commit.

## 1. Stop gate

The owner decision of 2026-11-21 stands: **the Phase 4 exit requires recorded golden fixture results.** Cross-interface agreement alone is not acceptance, because all three Python interfaces wrap the same DSS C-API backend — agreement between them tests the API layer, not the solver.

## 2. Fixture source (resolved)

| Item | Value |
|---|---|
| Repository | `dss-extensions/electricdss-tst` |
| Commit | `3b208397160213cae4a9e2d0a7d1aa3528ce26e1` |
| Commit date | 2024-06-24 |
| Licence | BSD-3-Clause, `License.txt` at the repository root: *Copyright (c) 2018-2024, DSS-Extensions contributors · Copyright (c) 2008-2024, Electric Power Research Institute, Inc.* Redistribution permitted with the notice retained; the EPRI name may not endorse derived products |
| Attribution requirement | `License.txt` is copied verbatim into the fixtures tree and every `PROVENANCE.md` names the upstream repository, commit, and both copyright holders |
| Why not the EPRI installer | It offers no commit hash, so a fixture could not be reproduced bit-for-bit. `electricdss-tst` is a filtered mirror of the OpenDSS SVN `Version8/Distrib` tree and gives a git pin |

The repository's own `README.md` explains that since June 2024 duplicated files were replaced by relative `redirect`/`compile` commands. That detail decides the fixture layout in §3: a fixture is the **closure** of its redirects, not the contents of one folder.

## 3. Fixture set and layout (resolved)

Copied unmodified, with the upstream relative directory layout preserved so that every `redirect` resolves with zero edits. Nothing is flattened, renamed, or annotated.

```
opendss_altdss_library/examples/fixtures/
├── License.txt                              upstream root licence, verbatim
├── ieee13/
│   ├── PROVENANCE.md
│   ├── golden.json
│   └── IEEETestCases/
│       ├── IEEELineCodes.DSS                12032 B, shared by both fixtures
│       └── 13Bus/
│           ├── IEEE13Nodeckt.dss             8354 B
│           ├── IEEELineCodes.DSS               30 B, a stub: redirect ../IEEELineCodes.DSS
│           └── IEEE13Node_BusXY.csv           243 B, used by BusCoords at line 150
└── ieee34/
    ├── PROVENANCE.md
    ├── golden.json
    └── IEEETestCases/
        ├── IEEELineCodes.DSS                12032 B, byte-identical to the ieee13 copy
        └── 34Bus/
            ├── ieee34Mod1.dss              14341 B, no Solve of its own
            ├── IEEELineCodes.DSS              30 B, a stub: redirect ../IEEELineCodes.DSS
            └── IEEE34_BusXY.csv              506 B, auxiliary, not read by the circuit file
```

SHA-256 of every copied file is recorded in the fixture record and in `PROVENANCE.md`. Verified values for the source commit:

| File | Bytes | SHA-256 |
|---|---:|---|
| `License.txt` | 1816 | `f13543277f32a6437d4f583200858f0988d3acc9598a6a1a292d710009ec21ef` |
| `IEEETestCases/IEEELineCodes.DSS` | 12032 | `71bc16ef9c6084b9e3bab74fbdf967080b79624683465e1483b787ff160f58b3` |
| `13Bus/IEEE13Nodeckt.dss` | 8354 | `033ccd4005c6538e9de5b2218e83001802ce14fbc5b6c312896ae8cbc5d4a504` |
| `13Bus/IEEELineCodes.DSS` | 30 | `40ef533dfcb22738edb1125b1e15e4a1a5d41b2cca4a2f969f5d955c9784daeb` |
| `13Bus/IEEE13Node_BusXY.csv` | 243 | `f8dd1528c72f339ebf41bf1355ed64ef12fbe30864fcc839ed5e5e9dc527846e` |
| `34Bus/ieee34Mod1.dss` | 14341 | `648f12f7f611ccf89bce68aea2142f0225ddcba78e81d16bd02e52e3a4b058f8` |
| `34Bus/IEEELineCodes.DSS` | 30 | `40ef533dfcb22738edb1125b1e15e4a1a5d41b2cca4a2f969f5d955c9784daeb` |
| `34Bus/IEEE34_BusXY.csv` | 506 | `6e022bbb3adb3c7f29ccb7bbdee2013517ae55e19ad25cda815616c5d4a37958` |

Both `IEEELineCodes.DSS` stubs share one checksum because they contain the same single `redirect` line.

**Deliberately not copied**, and why — recorded in each `PROVENANCE.md` so the omission is auditable:

| Upstream file | Reason |
|---|---|
| `34Bus/Run_IEEE34Mod1.dss`, `Run_IEEE34Mod2.dss` | Driver scripts containing `plot circuit` / `Plot profile` and two `Compile` passes with forced regulator taps. They cannot run headless and they are not the circuit definition |
| `34Bus/ieee34Mod2.dss` | The second variant, reserved for a later scenario. Adding it now would widen the fixture before the first golden exists |
| `34Bus/nmsu_linecode2_ABC.txt` | Referenced by neither circuit file in this commit |

## 4. What the fixtures exercise (measured)

Measured on the pinned stack by compiling each circuit and solving; these are the sanity checks a harness run must reproduce, **not** golden values:

| Fixture | Buses | Elements | Converged | Iterations | Control iterations | Lines | Transformers | Loads | Capacitors | RegControls | Lowest pu bus |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| ieee13 | 16 | 38 | yes | 2 | 1 | 12 | 5 | 15 | 2 | 3 | `611`, 0.960843 |
| ieee34 | 37 | 117 | yes | 25 | 6 | 32 | 8 | 68 | 2 | 6 | `890`, 0.923099 |

Notes that shaped the design:

- The 34-node case needs **6 control iterations**, so its 25 total iterations exceed the default `MaxIterations` of 15. Solver options are part of the golden metadata for exactly this reason.
- Each circuit reports a single `LoadShape` named `default`: that is the engine's built-in shape, not a fixture-authored one. Neither circuit defines a shaped load, so Phase 4 does not claim LoadShape coverage from the fixtures.
- Both fixtures exercise **RegControl** (3 and 6 instances) and capacitor banks (2 each), and neither control class is catalogued. The owner resolved this on 2026-11-21 by adding a RegControl catalog to Phase 4 (decision 13).
- `IEEE13Nodeckt.dss` ends with `calcv` and `Solve` (L148-L149) and then `BusCoords IEEE13Node_BusXY.csv` (L150). `ieee34Mod1.dss` ends at `CalcVoltageBases` (L246) with **no solve**. The harness must therefore issue its own `Solve` for both and must not assume either file leaves the circuit solved.
- Compile-plus-solve costs about 3 ms per fixture, so the daily time-series scenario in package 4.3 is affordable.

## 5. Golden result format

`examples/fixtures/<fixture>/golden.json`, **generated by the harness and never hand-typed**:

```json
{
  "fixture": "ieee13",
  "golden_revision": 1,
  "revision_date": "2026-11-22",
  "scenario": "snapshot",
  "source": {
    "repository": "https://github.com/dss-extensions/electricdss-tst",
    "commit": "3b208397160213cae4a9e2d0a7d1aa3528ce26e1",
    "retrieved": "2026-11-22",
    "license": {"identifier": "BSD-3-Clause", "path": "examples/fixtures/License.txt",
                "bytes": 1816, "sha256": "f1354327…c21ef"},
    "files": [{"path": "IEEETestCases/13Bus/IEEE13Nodeckt.dss", "bytes": 8354,
               "sha256": "033ccd40…d4a504"}]
  },
  "environment": {"python_version": "3.14.6", "altdss_version": "0.2.4",
                  "dss_python_version": "0.15.7", "backend_version": "0.14.5",
                  "platform": "Windows 11 AMD64"},
  "solver": {"mode": "SnapShot", "max_iterations": 15, "tolerance": 0.0001,
             "control_mode": "Static", "max_control_iterations": 10, "base_freq": 60.0},
  "solution": {"converged": true, "iterations": 2, "total_iterations": 2,
               "control_iterations": 1},
  "totals": {"load_kw": 0.0, "load_kvar": 0.0, "losses_kw": 0.0, "losses_kvar": 0.0,
             "source_kw": 0.0, "source_kvar": 0.0},
  "buses": {"611": {"nodes": [3], "pu_vmag": [0.0], "pu_vangle_deg": [0.0]}},
  "elements": {"Line.L1": {"powers_kw_kvar": [[0.0, 0.0]], "losses_kw_kvar": [0.0, 0.0]}},
  "controls": {"RegControl.reg1": {"tap": 0.0}, "Capacitor.C1": {"states": [1, 1, 1]}},
  "generated_by": "tools/run_fixtures.py --update-golden",
  "update_reason": "initial golden"
}
```

Rules:

- **Key sets are part of the contract.** Bus and element names must match exactly between golden and run; a missing or extra name is a failure, not a tolerance question.
- **Angles are degrees, powers kW/kvar, voltages per unit.** Node order follows the bus's own node order, recorded so a reordering is detectable.
- **Stored precision** is full `repr` float precision. Comparison applies the tolerance; the file is not pre-rounded, so a later tolerance change does not require regenerating goldens.
- **Solver options and engine versions are data**, not commentary. Any change to mode, tolerance, iterations, control settings, or base frequency is a new `golden_revision`.
- `update_reason` records the owner-approved justification for the revision that produced the file.

## 6. Tolerances

| Quantity | Comparison | Value |
|---|---|---|
| Bus per-unit magnitude | absolute | `1e-6` |
| Bus angle (degrees) | absolute | `1e-6` |
| Element powers and losses (kW, kvar) | relative, with absolute floor | `1e-6` relative, `1e-6` kW absolute |
| Totals | relative, with absolute floor | `1e-6` relative, `1e-6` kW absolute |
| Integer and enum quantities (tap steps, capacitor states, iteration counts) | exact | — |

Same engine on the same platform should reproduce to about `1e-9`; `1e-6` leaves headroom for platform floating-point differences without hiding a real regression. Any wider tolerance requires a written reason in the fixture record — a tolerance is a claim, so it is documented like one.

## 7. Harness contract

| Tool | Contract |
|---|---|
| `tools/run_fixtures.py` | Compile each fixture from its recorded file set, apply the recorded solver options, solve, build the golden structure, and diff against `golden.json`. Exit 0 only when every fixture matches and every checksum matches. `--fixture NAME` limits the run; `--report path` writes a machine-readable diff. |
| `tools/run_fixtures.py --update-golden --reason "…"` | Refuses without `--reason`. Increments `golden_revision`, writes the file, and requires the owner approval record in `references/fixtures.json` to be updated in the same commit. Refuses when the working tree has uncommitted fixture-file changes, so a golden can never be regenerated against altered inputs in the same step. |
| `tools/compare_interfaces.py` (package 4.4) | Run the same fixture through `altdss`, `dss`, and `opendssdirect` on the pinned versions; report per-quantity deltas. Its header must state that all three share DSS C-API 0.14.5, so a pass means API-layer agreement, not independent validation. |
| `tools/validate_catalogs.py` | Extended to validate `references/fixtures.json` against `schemas/catalogs/fixtures.schema.json`. The existing contract is unchanged. |

Checksum verification happens before compilation: a fixture whose bytes do not match the record is a failure even if it still solves.

Run from the repository root or invoke the tool by absolute path from another directory. The runner stages the verified redirect closure in a temporary directory and uses a fresh AltDSS context each time.

```powershell
python opendss_altdss_library/tools/run_fixtures.py
python opendss_altdss_library/tools/run_fixtures.py --fixture ieee13 --report ieee13-diff.json
```

For a new revision, record the owner's approval as the next entry in `golden_updates` for each selected fixture. Keep the approved reason identical to `--reason`. The runner advances `golden_revision` and records the approval date and reason in the golden. Commit the updated catalog and generated goldens together.

## 8. Catalog additions

`references/fixtures.json` + `schemas/catalogs/fixtures.schema.json`, one record per fixture:

`fixture_id`, `name`, `upstream_repository`, `upstream_commit`, `retrieved`, `license` (identifier and notice path, bytes and SHA-256), `files` (path, bytes, sha256), `entry_script`, `source_ids`, `golden_path`, `golden_revision`, `golden_updates` (revision, date, reason, approver), `tolerances`, `engine_versions`, `solver`, `notes`.

The input `files` and `entry_script` paths are relative to each fixture directory. The license and golden paths are relative to the library root. Solver settings come from the catalog. The golden records the applied values. The report records both golden and run environments so platform and Python version differences are visible while engine and wrapper versions remain pinned.

`source_ids` resolve against `sources.json`, so the pinned fixture commit and the pinned engine tags are cited in the same index as every other claim in the library.

## 9. Package sequence

| Package | Content | Depends on |
|---|---|---|
| **4.1 Fixture harness and snapshot goldens** | Fixture tree with `License.txt`, `PROVENANCE.md`; `fixtures.json` + schema; `tools/run_fixtures.py`; `golden.json` for both snapshots; `validate_catalogs.py` extension | Phase 3 complete |
| **4.2 RegControl catalog** | The Phase 3 six-artifact template for a control class: property catalog, workflow, examples, readback matrix, build audit, QA/QC | 4.1 goldens, because tap positions are already in validated output |
| **4.3 Daily time-series fixture** | Daily run on `ieee13` with regulators and the two capacitor banks operating; golden for the 24-step profile | 4.1 stable |
| **4.4 Cross-interface tool** | `tools/compare_interfaces.py` with `opendssdirect.py` 0.9.4 added to `requirements-validation.txt` | 4.1 |
| **4.5 Phase 4 exit** | `troubleshooting.json` seeded from Phase 3 and Phase 4 QA findings, documentation pass, manifest and plan reconciliation, exit checklist, owner review | 4.1–4.4 |

## 10. Owner decisions recorded

| # | Date | Decision |
|---|---|---|
| 13 | 2026-11-21 | Fixtures come from `dss-extensions/electricdss-tst` pinned at commit `3b20839`, with the BSD-3-Clause `License.txt` copied verbatim and attribution recorded per fixture |
| 14 | 2026-11-21 | `RegControl` is catalogued in Phase 4, not deferred, because both fixtures depend on it and the golden results carry tap positions |
| 15 | 2026-11-21 | Cross-interface comparison is in Phase 4 scope, adding `opendssdirect.py` 0.9.4 to the pinned stack, with its shared-backend limitation stated in the tool and the docs |

## 11. Risks

| Risk | Mitigation |
|---|---|
| A fixture is silently altered so the golden still "passes" | SHA-256 checked before compilation; `--update-golden` refuses with uncommitted fixture changes |
| Redirect closure is incomplete after copying | The layout in §3 preserves upstream relative paths; the harness fails loudly on a missing `redirect` target rather than solving a partial circuit |
| Golden values drift with a platform or engine bump | Versions and platform are inside the golden; a bump produces a visible diff, and the tolerance table governs the verdict |
| Controls are bypassed to make results easy | The coverage table in §4 lists the control counts; the golden stores tap and state values, so a bypassed regulator shows up as an unchanged tap |
| Licence terms are lost in transcription | `License.txt` copied verbatim into the fixtures tree, and both copyright holders named in every `PROVENANCE.md` |
| Cross-interface pass is mistaken for validation | Stated in the tool header, this document, and the plan §6.3: one backend, so it is an API-layer check |

## 12. Exit checklist

1. Both fixtures compile, converge, and match `golden.json` within tolerance from a clean environment built from `tools/requirements-validation.txt`.
2. Checksums of every fixture file match `fixtures.json`.
3. Golden metadata records upstream source, commit, checksums, licence, engine versions, solver options, date, environment and `golden_revision`.
4. `validate_catalogs.py` passes with the fixtures schema included.
5. The element classes the fixtures touch are catalogued or explicitly recorded as deferred: Line, LineCode, Transformer, Load, Capacitor, Vsource, RegControl.
6. Golden regeneration happens only through `--update-golden` with an owner-approved reason and a new revision.
7. The time-series scenario passes if package 4.3 is delivered; otherwise its absence is recorded as a scope limit.
8. `troubleshooting.json` is seeded from the Phase 3 and Phase 4 findings.
