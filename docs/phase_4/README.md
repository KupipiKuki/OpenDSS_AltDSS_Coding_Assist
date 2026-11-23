# Phase 4 — Validation with golden fixtures

**Status** The owner accepted the fixture harness and snapshot goldens (decision 16), RegControl catalog (decision 18), LoadShape catalog and daily golden (decision 19), and cross-interface comparison (decision 20). All three revision 1 goldens are frozen. Package 4.5 delivers the confirmed troubleshooting records and exit evidence and is accepted by the owner (decision 21), which closes the Phase 4 stop gate. [Exit review](../audits/phase4_exit_architect_audit.md) [Exit checklist](exit_checklist.md) · [Exit build audit](../audits/phase4_exit_audit.md) · [Package 4.4 review](../audits/phase4_cross_interface_architect_audit.md)
**Governs** [Implementation plan §6](../implementation_plan.md) (intent) · [manifest](../../opendss_altdss_library/manifest.json) (state)
**Pinned stack** AltDSS-Python `0.2.4` · DSS-Python `0.15.7` · DSS C-API backend `0.14.5`; cross-interface checks add `opendssdirect.py` `0.9.4`.

This document resolves the open items in plan §6 and records what was measured rather than assumed. Where §6 and this document disagree, this document is newer and the plan is corrected in the same commit.

## 1. Stop gate

The owner decision of 2026-11-21 stands: **the Phase 4 exit requires recorded golden fixture results.** Cross-interface agreement alone is not acceptance, because all three Python interfaces wrap the same DSS C-API backend — agreement between them tests the API layer, not the solver.

The exit checklist maps each stop-gate item to its validation command and recorded evidence. [Exit checklist](exit_checklist.md)

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
- The upstream snapshot circuits report the engine's built-in `LoadShape.default`. The IEEE 13 daily harness assigns the authored `daily24` shape to all 15 loads. [Daily profile](#51-daily-profile-golden-package-43)
- Both snapshots exercise RegControl (3 and 6 instances) and capacitor banks (2 each). Package 4.2 delivered the RegControl catalog under decision 14. The banks are fixed because these circuits have no CapControl elements. [RegControl catalog](../../opendss_altdss_library/references/regcontrols/regcontrol_properties.json)
- `IEEE13Nodeckt.dss` ends with `calcv` and `Solve` (L148-L149) and then `BusCoords IEEE13Node_BusXY.csv` (L150). `ieee34Mod1.dss` ends at `CalcVoltageBases` (L246) with **no solve**. The harness must therefore issue its own `Solve` for both and must not assume either file leaves the circuit solved.

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
- **`losses_kw_kvar` is the engine's `Losses()` converted from W/var to kW/kvar, not a dissipation figure.** For power-conversion elements and the source it equals the element's own power: in the ieee13 golden a load records 3454.66 kW, a capacitor bank −685.95 kvar and the source −3567.05 kW. Only passive elements contribute to dissipation, which is why line losses (106.48 kW) plus transformer losses (5.91 kW) equal `totals.losses_kw` (112.39 kW) while the sum over all elements is about zero. **`totals.losses_kw` is the only dissipation figure**; do not read a per-element `losses_kw_kvar` as energy lost in that element. *(Added by the package 4.1 architect review, finding E-1.)*
- **`elements` includes control objects.** `RegControl` entries appear with zero powers because `NumCircuitElements` counts them: the ieee13 golden's 38 entries are 12 lines, 5 transformers, 15 loads, 2 capacitors, **3 RegControls** and 1 Vsource. Regulator taps are also recorded under `controls`. *(Package 4.1 architect review, O-1.)*

### 5.1 Daily profile golden (package 4.3)

Package 4.3 delivered the IEEE 13 daily golden at revision 1, frozen under decision 19. Its `scenario` is `daily`, `solver.mode` is `Daily`, and `solver.step_size_s` is 3,600 seconds. All 24 steps converged. The profile totals 73,416.540 kWh and peaks at 4,004.671 kW in hour 18. [Daily golden](../../opendss_altdss_library/examples/fixtures/ieee13/golden_daily.json) · [Build audit](../audits/phase4_loadshape_daily_audit.md)

The golden records the shape settings used with the pinned IEEE 13 input files.

```json
"shape": {"name": "daily24", "npts": 24, "interval_h": 1.0, "use_actual": false,
          "pmult": [0.69, 0.64, 0.61, 0.6, 0.62, 0.68, 0.79, 0.9, 0.98, 1.02, 0.99, 0.96,
                    0.94, 0.95, 0.98, 1.04, 1.11, 1.16, 1.12, 1.05, 0.96, 0.87, 0.8, 0.74],
          "qmult": [], "assignment": "Load.daily"}
```

`steps` holds one record per solved hour. The first step is shown below with rounded values.

```json
"steps": [
  {"hour": 1, "converged": true, "iterations": 7, "control_iterations": 2,
   "totals": {"load_kw": 2399.365305, "load_kvar": 1455.114385, "losses_kw": 49.191776,
              "losses_kvar": 142.393127, "source_kw": -2448.543242, "source_kvar": -879.556905},
   "controls": {"RegControl.reg1": {"tap": 8}, "RegControl.reg2": {"tap": 6}, "RegControl.reg3": {"tap": 8},
                "Capacitor.cap1": {"states": [1]}, "Capacitor.cap2": {"states": [1]}},
   "lowest_bus": {"name": "611", "pu_vmag": 0.997018}}
]
```

- **`hour` is 1-based** and matches the engine's `Solution.Hour` at that step, so the mapping to `pmult` index is `hour - 1` and an off-by-one is visible in the file rather than hidden in the harness.
- **`peak_step`** repeats the full snapshot `buses` and `elements` blocks for the step with the highest `totals.load_kw`. The step is **derived from the data**, not hand-picked, so a circuit change cannot leave the reference step pointing at the wrong hour.
- **`energy_kwh`** records the day's load energy as the sum of each step's `load_kw` times the step length in hours, together with the same integral recomputed from the recorded `steps` array. The two must agree within tolerance, which turns the file into a check on itself rather than only on the engine.
- Each step records every regulator tap and capacitor state. `States` has one entry per configured capacitor step. Each IEEE 13 bank has one step. [Capacitor catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json)
- Tolerances are exactly [section 6](#6-tolerances); discrete quantities (hour, taps, states, iteration counts) compare exactly.
- Full bus voltages are recorded at the peak step only. Recording all buses at all 24 steps would multiply the file size without adding a discriminating check, since `lowest_bus` already tracks the binding constraint at every step.

## 6. Tolerances

| Quantity | Comparison | Value |
|---|---|---|
| Bus per-unit magnitude | absolute | `1e-6` |
| Bus angle (degrees) | absolute | `1e-6` |
| Element powers and losses (kW, kvar) | relative, with absolute floor | `1e-6` relative, `1e-6` kW absolute |
| Totals | relative, with absolute floor | `1e-6` relative, `1e-6` kW absolute |
| Integer and enum quantities (tap steps, capacitor states, iteration counts) | exact | — |

Same engine on the same platform should reproduce to about `1e-9`; `1e-6` leaves headroom for platform floating-point differences without hiding a real regression. Any wider tolerance requires a written reason in the fixture record — a tolerance is a claim, so it is documented like one.

Two `environment` keys are deliberately **excluded** from comparison: `python_version` and `platform`. They are recorded in the golden and printed in the report so drift is visible, but they do not fail a run, because the pins that reproducibility depends on are the engine and wrapper versions, which are compared exactly and also re-checked against `manifest.json` before compiling. A change of interpreter therefore passes with the difference visible in the report rather than silently. *(Package 4.1 architect review, O-2.)*

## 7. Harness contract

| Tool | Contract |
|---|---|
| [run_fixtures.py](../../opendss_altdss_library/tools/run_fixtures.py) | Verify input checksums, compile and solve, and compare the two snapshots and the IEEE 13 daily scenario against their goldens. Use `--fixture NAME` and `--scenario snapshot` or `--scenario daily` to select runs. Use `--report path` for a machine-readable diff. |
| `tools/run_fixtures.py --update-golden --reason "…"` | Refuses without `--reason`. Increments `golden_revision`, writes the file, and requires the owner approval record in `references/fixtures.json` to be updated in the same commit. Refuses when the working tree has uncommitted fixture-file changes, so a golden can never be regenerated against altered inputs in the same step. |
| [compare_interfaces.py](../../opendss_altdss_library/tools/compare_interfaces.py) | Compare the two snapshots through three wrappers of DSS C-API 0.14.5. The result summary records name-matched deltas. Independent numerical validation requires a separate reference. [Report](../audits/phase4_cross_interface_report.json) |
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

### 8.1 Deferred class catalogs (decision 17)

The classes carried as deferred since Phase 3B were measured before being scoped, so the record rests on counts and source availability rather than on impression. Row counts are the annotated keys of the pinned wrapper's `*Properties` class (AltDSS-Python `0.2.4`); the method reproduces the known `RegControl` figure of 35.

The decisive measurement is that neither pinned circuit uses any of them. The complete class inventory of the fixture trees is `load` (83), `linecode` (65), `line` (44), `transformer` (13), `regcontrol` (9) and `capacitor` (4). There is no `CapControl` in either circuit, so the two capacitor banks in package 4.3 are fixed rather than switched.

| Class | Kind | Rows | EPRI concept page | EPRI properties page | In fixtures | Scope (decision 17) |
|---|---|---|---|---|---|---|
| `LoadShape` | data object | 22 | `LoadShape.html` (carries the property narrative) | none — scanned `Properties1`–`35` for `NPts`, no hit; `Properties7.html` is the *Load* page and only cross-references shapes | 0 | **In package 4.3** |
| `GrowthShape` | data object | 7 | `GrowthShape.html` | not found in `Properties1`–`35` | 0 | Deferred |
| `CapControl` | control | 26 | `CapControl1.html` | `Properties20.html` | 0 | Deferred |
| `GenDispatcher` | control | 10 | none (`GenDispatcher`, `GenDispatcher1`, `GenDispatcher2`, `GeneratorDispatcher`, `Dispatcher` all 404) | none | 0 | Deferred |
| `AutoTrans` | transformer variant | 42 | `AutoTrans.html` | `Properties11.html` | 0 | Deferred |
| `PVSystem` | PC element | 54 | `PVSystem.html` | `Properties5.html`, `Properties6.html` | 0 | Deferred |
| `Storage` | PC element | 64 | `Storage.html` | `Properties5.html`, `Properties25.html` | 0 | Deferred |
| `InvControl` | control | 35 | `InvControl.html` | — | 0 | Deferred with the DER set |
| `ExpControl` | control | 17 | `ExpControl.html` | — | 0 | Deferred with the DER set |

`LoadShape` is in scope because package 4.3 cannot produce a daily profile without it; the catalog is delivered inside 4.3 so the readback matrix and the 24-step golden are validated together. Everything else is deferred on scope grounds — no fixture usage, no package depends on it, and the 203 rows that remain deferred from the seven originally named classes (225 in total, less the 22 now in scope) would add breadth no golden can exercise. CapControl and AutoTrans in particular are **not** deferred for lack of evidence, since EPRI documents both; they are deferred because nothing in Phase 4 needs them. Recorded for a future package: `AutoTrans` extends the Phase 3B `Transformer` catalog, and `RegControl`'s transformer reference already accepts an `AutoTrans` target.

Two measurement cautions were adopted from this survey. EPRI page names are inconsistent — `CapControl.html` is 404 while `CapControl1.html` returns the concept page, and the reverse holds for `RegControl` — so both forms are probed before any page is declared missing, and a single 404 is not evidence of absence. The Doxygen class reference at `dss-extensions.org/dss_capi/` was also checked and does list the property surface (`PTratio`, `CTratio`, `ONsetting`, `OFFsetting` on the CapControl page), but it carries no version string, so it is a cross-check index only and never a citation; pinned property claims cite the engine source at DSS C-API `0.14.5`.

`LoadShape` was probed on the pinned stack so package 4.3 inherits its traps rather than rediscovering them:

- The attribute is `NPts`; `Npts` raises `AttributeError`.
- Setting `PMult` before `NPts` fails with `(#20200425) LoadShape.daily24.PMult: Invalid number of elements. Expected 0 elements, got 24`. Size the array first, then assign.
- With `Solution.Number = 24`, each `Solve()` runs a whole day: `Solution.Hour` goes 1 → 24 in one call, so a naive 24-row loop samples the last step 24 times and the profile looks flat. Sample per step with `Number = 1` and 24 solves.
- `Solution.Hour` is 1-based: the first step reports `Hour = 1` and consumes `PMult[0]`.
- Scaling was confirmed against multipliers 0.5, 1.0, 1.5 and 2.0, giving 1765.68, 3567.13, 5410.94 and 7085.56 kW from a 3567.05 kW base.
- The property is `Solution.StepSize`, not `Stepsize`.

## 9. Package sequence

| Package | Content | Depends on |
|---|---|---|
| **4.1 Fixture harness and snapshot goldens** | [Pinned fixture tree](../../opendss_altdss_library/examples/fixtures/) · [Fixture catalog](../../opendss_altdss_library/references/fixtures.json) · [Review](../audits/phase4_fixture_harness_architect_audit.md) | Phase 3 complete |
| **4.2 RegControl catalog** | [Property catalog](../../opendss_altdss_library/references/regcontrols/regcontrol_properties.json) · [Workflow](../workflows/regcontrol.md) · [Review](../audits/phase4_regcontrol_architect_audit.md) | 4.1 goldens |
| **4.3 Daily time-series fixture** | [LoadShape catalog](../../opendss_altdss_library/references/loadshapes/loadshape_properties.json) · [IEEE 13 daily golden](../../opendss_altdss_library/examples/fixtures/ieee13/golden_daily.json) · [Review](../audits/phase4_loadshape_daily_architect_audit.md) | 4.1 and 4.2 accepted |
| **4.4 Cross-interface tool** | [Workflow](../workflows/cross_interface.md) · [Result summary](../audits/phase4_cross_interface_report.json) · [Review](../audits/phase4_cross_interface_architect_audit.md) | 4.1 and 4.3 accepted |
| **4.5 Phase 4 exit** | [Troubleshooting index](../workflows/troubleshooting.md) · [Exit checklist](exit_checklist.md) · [Build audit](../audits/phase4_exit_audit.md) | 4.1–4.4 accepted |

## 10. Owner decisions recorded

| # | Date | Decision |
|---|---|---|
| 13 | 2026-11-21 | Fixtures come from `dss-extensions/electricdss-tst` pinned at commit `3b20839`, with the BSD-3-Clause `License.txt` copied verbatim and attribution recorded per fixture |
| 14 | 2026-11-21 | `RegControl` is catalogued in Phase 4, not deferred, because both fixtures depend on it and the golden results carry tap positions |
| 15 | 2026-11-21 | Cross-interface comparison is in Phase 4 scope, adding `opendssdirect.py` 0.9.4 to the pinned stack, with its shared-backend limitation stated in the tool and the docs |
| 17 | 2026-11-21 | The deferred class catalogs are settled: `LoadShape` enters package 4.3 because the daily series cannot vary load without it, and `GrowthShape`, `CapControl`, `GenDispatcher`, `AutoTrans`, `PVSystem`, `Storage`, `InvControl` and `ExpControl` are deferred on scope grounds, not for lack of evidence. Measurements, EPRI page map and row counts in [section 8.1](#81-deferred-class-catalogs-decision-17) |

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

[Phase 4 exit checklist](exit_checklist.md) records the six plan gates, the evidence for each, and the validation scope.
