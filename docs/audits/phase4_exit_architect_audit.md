# Phase 4.5 exit package — Architect/Auditor Review

**Reviewed branch:** `wp/phase4`, tip `22fd398` (QA/QC report), clean working tree at review start.
**Package revision under review:** `75c6e1ca9adf8e06f704a31d7d42593cb5ba57c5` (troubleshooting catalog, documentation pass, exit checklist, build audit).
**Inputs/baseline revision:** `cc8aa92ecaf14bbc4f54a2ee78b177adbf130bb8` (decision 20, package issued).
**Review date:** 2026-11-22 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine `DSS C-API 0.14.5` revision `87d85c2…`), `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`.

**STATUS:** PASS WITH FINDINGS — two documentation corrections required, no code, catalog or data change requested. Every troubleshooting record and every harness result reproduces. **Both corrections were applied at `0187ded` and verified in the addendum below; the stop gate is closed pending owner acceptance.**

## Run verification (my own runs, not the build audit's)

| Check | Result |
|---|---|
| `tools/validate_catalogs.py` | 18/18 pairs PASS, `references/troubleshooting.json` **16 record(s)** |
| `tools/run_examples.py` | 19/19 PASS, including `ieee13-snapshot-cross-interface` under its new `python_cross_interface` classification |
| `tools/run_fixtures.py` | 3/3 PASS — ieee13 snapshot 16 buses/38 elements/2·1, lowest 611 at 0.960843; ieee13 daily 24 h, 73,416.540 kWh, peak 4,004.671 kW at hour 18, lowest 611 at 0.952044 at that hour; ieee34 37/117/25·6, lowest 890 at 0.923099 |
| `tools/compare_interfaces.py --report <tmp>` | PASS both fixtures, six pairs, zero out-of-tolerance differences and zero nonzero numeric deltas; report **byte-identical** to the accepted blob, SHA-256 `578d56f9a4d024205e9f652b49e17371da2b58b74b49191c639905595ab8c97a` — the same digest the build audit records |
| `git diff --check cc8aa92..HEAD` | clean |
| Goldens | all three identical across the baseline blob, HEAD blob and working tree: `f72d59d8…ef5f4`, `b06282a6…2709f`, `0f8d5400…8223` |
| Fixture tree | 15 tracked files, none modified by the package |

## The troubleshooting catalog is real evidence, not a summary of my handoff

I re-observed **all 16 records** myself rather than reading them, deliberately using routes different from the ones the build audit describes where a route choice could flatter the result:

| Record | My observation |
|---|---|
| `ts-tapnumber-not-indexed` | `ActiveClass` walk via `RegControls.TapNumber()` → `[9, 9, 9]`; `? regN.TapNum` → `9/6/9`. With the class cursor on reg1 (route: `RegControls.Name("reg2")` selects, reads do not), `TapNumber(7)` returned `None` and moved **reg2** 6 → 7 while reg1 and reg3 stayed 9 |
| `ts-dss-text-command-property` | `dss.Text.Command("solve")` → `TypeError: 'str' object is not callable`; `dss.Text.Commands` exists and is the method |
| `ts-dss-solution-via-active-circuit` | `dss.DSS.Solution` → `AttributeError: 'IDSS' object has no attribute 'Solution'`; `ActiveCircuit.Solution` is an `ISolution` |
| `ts-totaliterations-accessor-casing` | `Solution.TotalIterations` (capital) → `AttributeError` on dss-python; `Totaliterations` → 2; `odd.Solution.TotalIterations()` → 2 |
| `ts-active-class-first-property` | `dss…ActiveClass.First` is `int` 1, calling it → `TypeError`; `odd.ActiveClass.First()` → 1 |
| `ts-losses-watts-vs-kilowatts` | `Losses()` → `[60728.5028021296, 195986.0785571934]` W/var; `TotalPowers()` → `[3566.699001…, 1735.849316…, -3505.970498…, -1539.863238…]` kW/kvar. The terminal sum is `[60.728503, 195.986078]`, which equals the converted losses, so the reconciliation claim holds exactly |
| `ts-controlled-solve-retaps` | tap 5 after the write; 6 after controlled `Solve()`; **5** after `SolveNoControl()` with `Solution.ControlMode()` = 0 (Static) before and after |
| `ts-ptphase-out-of-range` | `PTPhase=7` reads back `1` through the text query |
| `ts-capacitor-no-spectrum` | `hasattr(Capacitors, "Spectrum")` False, `hasattr(Loads, "Spectrum")` True |
| `ts-python-context-isolation` | second altdss context → `(#8888) There is no active circuit! Create a circuit and retry.`; in one process both classic facades report circuit `ieee13nodeckt`, a load created through `odd` appears in dss-python's `AllElementNames`, and `New Circuit.second` raises `(#266) Warning: Duplicate new element definition: "Vsource.source". Element being redefined.` A plain recompile of the same file is fine — the error is about redefining the source, not about compiling twice |
| `ts-loadshape-new-duplicates` | `.new("s1")` on an existing 3-point shape → `NPts` 0; iteration then lists `LoadShape.s1` twice with 3 and 0 points; `ctx.LoadShape["s1"]` still returns the 3-point original |
| `ts-loadshape-lowercase-new` | `ctx.LoadShape.New("x")` → `AttributeError: 'ILoadShape' object has no attribute 'New'`; `callable(ctx.LoadShape.new)` True |
| `ts-loadshape-missing-csv` | `new LoadShape.c1 csvfile=[nonexistent.csv]` → `(#613) Error opening file: "nonexistent.csv"` at the command |
| `ts-loadshape-empty-statistics` | fresh shape: `CSVFile` → `''`; `Mean` → `0.0`; next `CSVFile` → `(#61107) LoadShape has no data to be normalized. Check for previous errors.`; the read after that → `''` again |
| `ts-loadshape-pmult-length` | at `NPts=0` a two-value write raises `(#20200425) … Expected 0 elements, got 2.`; on a 4-point shape, 2 and 5 values both raise with `Expected 4 elements`; the rejected edits leave `[1,2,3,4]` intact |
| `ts-loadshape-npts-without-array` | bare `NPts=4` → `PMult` is an empty `float64` array; after the first full write it reads `[1,2,3,4]` |

The last record is the honest one: my handoff's seed 15 carried the 4.3 note about *uninitialised values*, and the coder recorded what was actually visible instead — an empty array — and said so. That is the behaviour I want from a record of observed failure modes, and it is the reason this catalog can be trusted where a copied one could not.

## Schema contract

| Check | Result |
|---|---|
| 16 records validate against `schemas/catalogs/troubleshooting.schema.json` | PASS |
| undeclared `resolution` field | rejected — `Unevaluated properties are not allowed ('resolution' was unexpected)` |
| `tested.result: "maybe"` | rejected — not one of `pass`/`fail`/`not-run` |
| `status: "resolved"` | rejected — not one of `confirmed`/`unresolved`/`superseded` |
| record without `tested` | valid (the block is optional) |
| the same record at `cc8aa92` | rejected — `Unevaluated properties are not allowed ('tested' was unexpected)` |

That last row is the important one and it is a finding against **my** handoff, not the coder's work: see A-1. `issue.schema.json` is consumed only by the troubleshooting catalog, so the one-line `$ref` addition has a blast radius of exactly one file, and it relaxes rather than tightens — nothing that validated before fails now.

## Documentation pass

The library README was the artifact with real drift and it is now correct: 144 engine records, 19 examples, `regcontrols/`, `loadshapes/`, `fixtures.json`, `python_interface_comparison.json` and the fixtures tree listed, all five runners in the validation block, and a closing line that names only `opendss_objects` as still empty. I verified each count against the catalogs rather than against the diff summary.

The Phase 4 design's rewritten daily-profile example is not decoration — I checked **every digit** against `golden_daily.json` and all of it is exact: the 24-point `pmult`, `solver.mode: Daily`, `step_size_s` 3600, 24 converged steps, energy 73,416.540 kWh from both the integral and the step sum, peak hour 18, and step 1 with iterations 7, control iterations 2, taps 8/6/8, both banks at `[1]` and lowest bus 611 at 0.997018 (recorded 0.9970177). A documentation example that quotes real numbers is a claim, and this one holds.

The two additive schema changes are exactly what O-3 and the `tested` gap needed: one enum value in `examples.schema.json` with one matching catalog value, and one `$ref`. Only `troubleshooting.json` and that single `language` value changed under `references/`; `tools/`, `examples/` and every accepted catalog are untouched.

## REQUIRED CORRECTIONS

**R-1 — the exit checklist loses two gates the design's own §12 carried.** `docs/phase_4/README.md` §12 previously listed eight items; it is now a pointer to `docs/phase_4/exit_checklist.md`, which carries the plan's six. Two design-level gates therefore have no row anywhere:

- *fixture checksums match `fixtures.json` before compilation* — implemented and exercised (`run_fixtures.py:96-125`, `verified_bytes` raising on any byte or digest mismatch), but the checklist's row 1 does not say that its command proves it;
- *the element classes the fixtures touch are catalogued or explicitly recorded as deferred* — Line, LineCode, Transformer, Load, Capacitor, Vsource and RegControl are all catalogued, and the row would be one line of links.

Add both to `docs/phase_4/exit_checklist.md` (either as rows 7 and 8 or as a "design gates" subsection), with the command and artifact for each. A stop gate that quietly drops two of its own items is the failure mode the charter's gate exists to prevent.

**R-2 — `docs/phase_4/exit_checklist.md` row 5 is stale.** It reads "Package 4.5 QA/QC and the final manifest update are pending", but QA/QC passed at `22fd398` (`docs/audits/phase4_exit_qaqc.md`). Record the QA/QC outcome and keep the manifest/plan reconciliation as the architect's remaining step, so the row reflects the state a reader will find.

## Observations (no action requested)

- **O-1** `docs/workflows/troubleshooting.md` links records by line anchor (`troubleshooting.json#L185`). I checked all 16 and every one points at the right record today, but a line anchor is silently wrong after the first inserted record. Consider linking by `id` in prose, or adding a short markdown table in `docs/` that carries the ids.
- **O-2** `fixtures.json` records `daily.shape.assignment: "Load.daily"` while the harness assigns the shape to all 15 loads (`run_fixtures.py:301-304`). The label reads like one load name and is frozen inside the revision 1 golden, so it should stay until a revision is warranted — worth knowing before someone reads it as a wiring claim.
- **O-3** `skill.md` dropped the clause "an unpinned catalog fails the run on purpose", which was the reason the pairing guard exists. The rule survives, the motive does not.
- **O-4** writing `Capacitor.States` in altdss appeared to be ignored in my probe (`States = [1,1,0,1]` read back unchanged). Nothing in this package writes states — the harness reads them — so this is a note for a future package, not a defect here.

## Architect self-corrections found during this review

- **A-1** My 4.5 handoff listed `tested` as an optional field of issue records. It is not: `common.schema.json` defines `$defs/tested`, but `evidenceRecordFields` never references it, so a record carrying `tested` was rejected at `cc8aa92`. The coder's one-line `$ref` is the correct remedy and the narrower one — adding it to `evidenceRecordFields` would have widened every record type to solve a troubleshooting-only need. Corrected in the handoff with a note.
- **A-2** My 4.4 handoff trap 8 said an argument to `opendssdirect`'s `RegControls.TapNumber` is "swallowed silently". At `opendssdirect/RegControls.py#L267-L279` it is a getter with no arguments and a **setter** with one, and the setter writes the active control's tap — my probe wrote reg3's tap to 7 by accident. The 4.4 workflow page already states this correctly, so no accepted artifact is wrong; the handoff is. Corrected with a note.
- **A-3** My design text said the capacitor `states` array follows the element's node count. It follows `NumSteps`: a three-phase bank with `NumSteps=1` records one state, and with `numsteps=4` it records four. The coder's rewrite in the design is correct and I confirmed it directly.

## Stop gate against plan §6.5

| Gate | Verdict |
|---|---|
| 1. Fixtures match goldens from a clean environment | met, reproduced |
| 2. Cross-interface deltas within tolerance or dispositioned | met, six pairs at zero delta |
| 3. Golden metadata complete | met; the metadata example in the design is exact against the file |
| 4. `troubleshooting.json` holds observed failure modes with resolutions | met — 16 confirmed records, all re-observed by me, schema-strict |
| 5. Independent QA/QC sign-off, `validation.runtime` states scope, environment and gaps | QA/QC PASS at `22fd398`; the manifest text is mine to reconcile (done this review, completion at acceptance) |
| 6. Golden regeneration only through the approved path | met; guards re-read in code and previously unit-exercised |

With R-1 and R-2 applied, the gate is closed on evidence rather than on assertion.

## Corrections verified (remediation commit `0187ded`)

The remediation touches one file, `docs/phase_4/exit_checklist.md` (+28/−3). I verified the corrections by executing them rather than by reading them.

**R-1, checksum gate.** The row and the header now say the harness verifies inputs *before* compiling. To prove the gate bites rather than merely exists, I copied the library to a scratch tree, appended two comment lines to `IEEETestCases/13Bus/IEEE13Nodeckt.dss`, and ran the harness:

```text
Checksum mismatch for …IEEE13Nodeckt.dss: expected 8354 bytes and 033ccd40…a504,
observed 8366 bytes and d82e945f…6cd
FAIL ieee13 snapshot
FAIL ieee13 daily
PASS ieee34 snapshot
```

The tool exits 1, and only the tampered fixture fails — per-fixture, not global. That is what the gate is supposed to look like.

**R-1, coverage gate.** The new `### Fixture class coverage check` is executable, so I ran it as written with `powershell.exe`:

```text
Capacitor  Line  LineCode  Load  LoadShape  RegControl  Transformer  Vsource
exit 0
```

It resolves because the goldens store `elements` as an object keyed by full name, so `.PSObject.Properties.Name` yields the names and the split recovers the class. I also confirmed the two directions independently: the snapshot goldens contribute Capacitor, Line, Load, RegControl, Transformer and Vsource, the daily harness adds LoadShape, the fixture scripts carry LineCode, and every one of the eight appears as an `element_class` in a property catalog — so the check would have thrown had any been missing.

**R-2, row 5.** Now records QA/QC PASS at `22fd398` with a link to the report, and leaves the manifest/plan reconciliation as the architect's step at acceptance, which is accurate.

**Anchors.** I resolved every new link: `#checksum-proof-three-way-per-file` is `## Checksum proof (three-way, per file)` in the 4.1 QA/QC report, `#stop-gate-against-plan-65` is `## Stop gate against plan §6.5` in this audit, and `#81-deferred-class-catalogs-decision-17` is `### 8.1 Deferred class catalogs (decision 17)` in the Phase 4 design. All three resolve as written.

`validate_catalogs.py` still passes 18/18 after the remediation. Nothing outside the checklist changed, so the accepted catalogs, goldens and tools remain as reviewed.
