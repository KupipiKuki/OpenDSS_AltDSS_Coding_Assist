# Phase 4 Package 4.3 — LoadShape catalog and daily profile (coder handoff)

**Issued** 2026-11-21 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** 4.1 accepted (snapshot goldens frozen, decision 16) and 4.2 accepted (decision 18).
**Scope authority** decision 17: `LoadShape` is the one deferred class that enters Phase 4, because the daily series cannot vary load without it. Nothing else from the deferred list is in this package.

## Goal

Two deliverables in one package, because they validate each other: the `LoadShape` property catalog with its readback evidence, and the 24-step daily profile on `ieee13` whose golden depends on the shape behaving as catalogued. The golden format is fixed in [the Phase 4 design, section 5.1](../phase_4/README.md); do not redesign it, and do not touch the snapshot goldens.

## Rider from package 4.2

Deliver this with the same commit series: **F-1** from [the 4.2 audit](../audits/phase4_regcontrol_architect_audit.md). Add one clause to the `ptphase` row of `references/regcontrols/regcontrol_properties.json` and one sentence to the `PTPhase` paragraph of `docs/workflows/regcontrol.md`, stating that an out-of-range positive `PTPhase` reads back as `1`. Evidence already exists in `docs/audits/phase4_regcontrol_readback.json` under `sensing.pt_phase.out_of_range_positive` (`written: 4, after_edit: 1`), and I reproduced it: `4` → `1`, `2` → `2`, `-3` → `RegControlPhaseSelection.min`, `-2` → `max`. Do not change any other RegControl row, value or citation.

## Pinned surface

| Item | Value |
|---|---|
| Wrapper class | `altdss/LoadShape.py` at AltDSS-Python `0.2.4`, `LoadShapeProperties` = **22** keys |
| Engine class | `src/General/LoadShape.pas` at DSS C-API `0.14.5` (2385 lines). Not `src/LoadShape.pas` — that path does not exist |
| Collection | `ctx.LoadShape`; the circuit also always carries `LoadShape.default` |
| EPRI | [`LoadShape.html`](https://opendss.epri.com/LoadShape.html) (200) carries the concept **and** the property narrative: `Npts`, `Pmult`/`Mult`, array syntax, the `PMult=[file=…]` form, and the fixed-versus-variable-interval rule. **There is no EPRI properties page for LoadShape** — I scanned `Properties1`–`35` for `NPts` and found no hit, and `Properties7.html` is the *Load* page, which only cross-references shapes. Do not cite a `Properties*` page for this class |

The 22 keys, all of which need a row: `NPts`, `Interval`, `Hour`, `Mean`, `StdDev`, `CSVFile`, `SngFile`, `DblFile`, `Action`, `QMult`, `UseActual`, `PMax`, `QMax`, `SInterval`, `MInterval`, `PBase`, `QBase`, `PMult`, `PQCSVFile`, `MemoryMapping`, `Interpolation`, `Like`. Note there is no `BaseFreq` and no `Enabled` on this class — it is a data object, not a circuit element, which is also why it must not appear in `elements`.

## Verified defaults (fresh object, pinned stack)

| Property | Default | Notes |
|---|---|---|
| `NPts` | 0 | number of points to expect |
| `Interval` | 1.0 | hours; `0.0` selects the variable-interval path |
| `SInterval` | 3600.0 | seconds — **the same field as `Interval`** |
| `MInterval` | 60.0 | minutes — **the same field as `Interval`** |
| `Hour` | empty | time values in hours, variable-interval path only |
| `Mean`, `StdDev` | 0.0 | do not copy the Load page's 50/10 defaults; those belong to `Load` |
| `PMult`, `QMult` | empty | multiplier arrays, length must equal `NPts` |
| `UseActual` | `False` | when true the arrays are actual kW/kvar |
| `PMax`, `QMax` | 1.0, 0.0 | normalization ceilings for `Action(Normalize)` |
| `PBase`, `QBase` | 0.0, 0.0 | used with `UseActual` |
| `CSVFile`, `SngFile`, `DblFile`, `PQCSVFile` | unset | `CSVFile` read on an empty shape raises (see traps) |
| `MemoryMapping` | `False` | file-backed loading |
| `Interpolation` | `Avg` (0) | enum `LoadShapeInterpolation` = `Avg` 0, `Edge` 1 |
| `Action` | method | enum `LoadShapeAction` = `Normalize` 0, `DblSave` 1, `SngSave` 2 |
| `Like` | method | copies `NPts` and the arrays |

`LoadShapeClass` exists as a separate enum (`none` -1, `Daily` 0, `Yearly` 1, `Duty` 2) and is **not** the same thing as `Load.Daily`. State that distinction in the workflow; conflating them is the obvious reader error.

## Traps, all probed on the pinned stack

1. **`NPts` casing.** `shape.Npts` raises `AttributeError`; the attribute is `NPts`. The DSS text keyword is `npts`.
2. **`PMult` must be written after `NPts`, at exactly the right length, in both directions.** Before `NPts` is set: `(#20200425) LoadShape.daily24.PMult: Invalid number of elements. Expected 0 elements, got 24.` Too short after: `(#20200425) LoadShape.s1.PMult: Invalid number of elements. Expected 4 elements, got 2.` There is no truncation and no padding.
3. **Growing `NPts` does not zero the new slots.** Setting `NPts` 4 → 6 with `PMult` = `[1, 2, 3, 4]` left the two new entries as uninitialised memory — observed `1.2186087344420384e-12` and `6.085753414500863e+247`. Always set `NPts` first and then write the full array; never grow a shape and read it back.
4. **`Interval`, `SInterval` and `MInterval` are one field in three units.** Writing `SInterval = 1800` set `Interval` to 0.5 and `MInterval` to 30; writing `MInterval = 15` moved both again. They are not independent settings, and a catalog that presents them as three separate values without saying so is misleading.
5. **`CSVFile` on a shape with no data, and the sticky statistics error behind it.** A fresh shape reads `CSVFile` as `""`. Reading `Mean` or `StdDev` then returns a value but leaves an engine error pending, and the **next checked read** raises `(#61107) LoadShape has no data to be normalized. Check for previous er…`; once that error is consumed, `CSVFile` reads `""` again. So a matrix that reads every key in order will surface `#61107` on whichever row follows the statistics rows. Isolate each statistics getter in its own context and consume the error deliberately, or the trailing rows of your loop look broken. Corrected 2026-11-21 during the package audit: this trap originally said a plain `CSVFile` read raises, which is wrong — the raise is the pending error from a statistics getter, not the file read itself.
6. **`Mult` is an accepted DSS text alias for `PMult`.** `New LoadShape.s2 npts=3 mult=(0.1 0.2 0.3)` round-trips. The Python keyword is `PMult`.
7. **`Action(Normalize)` rescales in place.** `[1, 2, 4]` became `[0.25, 0.5, 1.0]` against `PMax` 1.0. Record it as an action with the enum, not as a property.
8. **`Like` copies the data, not just the settings.** `s3.Like("s2")` reproduced `NPts` 3 and `[0.1, 0.2, 0.3]`. It is a method: as in 4.2, a `Like=` creation keyword is not the way.
9. **`Solution.Number = N` makes each `Solve()` run N steps.** With `Number = 24`, one `Solve()` took `Solution.Hour` from 0 to 24, so a 24-row collection loop sampled the same index 24 times and the profile looked flat. For a 24-step golden use `Number = 1` and call `Solve()` 24 times, or record `Hour` explicitly and assert it advanced.
10. **`Solution.Hour` is 1-based.** The first solved step reports `Hour = 1` and consumes `PMult[0]`, so the index is `hour - 1`. Getting this wrong shifts the entire profile by one step and still looks plausible.
11. **The property is `Solution.StepSize`, not `Stepsize`.** Same casing class of error as `NPts`.
12. **Shape assignment takes a name or an object.** `load.Daily = "daily24"` reads back as `LoadShape.daily24`, and the DSS text route `Load.<name>.daily=daily24` behaves the same. Record which one the example uses.
13. **The circuit always has `LoadShape.default`.** Iterating `ctx.LoadShape` returns it, so any "shape count" assertion must account for it. In the smoke probe a fresh circuit plus one shape reported 2 entries.
14. **A shape is not a circuit element.** It must not appear in `elements` or in `NumCircuitElements`. The ieee13 golden's 38 entries are unchanged by this package.
15. **The fixture's capacitors are fixed.** Neither pinned circuit contains a `CapControl`, so "both capacitor banks operating" in the design means energised at their defined states, not switched. Do not invent a control to make the series more interesting, and do not add `CapControl` (deferred by decision 17).
16. **`Interval = 0` switches to the variable-interval path** and comes with `Hour`; a fixed-interval shape with `Hour` populated is a contradiction the catalog should warn about. The zero-length case is what the EPRI page describes, and I probed that both arrays write cleanly at `NPts = 3`.
17. **`UseActual = True` changes the meaning of the multipliers** from per-unit to kW/kvar, with `PBase`/`QBase` as the reference. The daily golden uses `UseActual = False`, so say so in the shape block rather than leaving it implied.

## Deliverables

| # | Artifact | Notes |
|---|---|---|
| 1 | `references/loadshapes/loadshape_properties.json` | One record, `element_class: LoadShape`, 22 rows. `required_properties` = `name` only; the effective requirement is `NPts` plus a multiplier array, which belongs in `property_requirements.conditional` with the ordering trap |
| 2 | `references/regcontrols/regcontrol_properties.json` + `docs/workflows/regcontrol.md` | **F-1 rider only** — the `PTPhase` clause. Change nothing else |
| 3 | `docs/workflows/loadshape.md` | Cover construction order, the exact-length contract, the three-unit `Interval` family, `Number`/`StepSize`/`Hour` stepping, shape assignment, `LoadShape.default`, and the `LoadShapeClass` versus `Load.daily` distinction |
| 4 | Two examples | One Python, one DSS, each building its own small circuit with a daily shape and stepping it. Assert a per-step load kW **and** the hour it occurred at, so an off-by-one fails the example |
| 5 | `tools/readback_loadshape.py` + `docs/audits/phase4_loadshape_readback.json` | Sections: defaults for all 22 keys, the length contract in both directions, the `NPts` growth hazard, the `Interval` family, `Action(Normalize)`, `Like`, the text alias, the empty-shape `CSVFile` error, and stepping |
| 6 | `examples/fixtures/ieee13/golden_daily.json` + harness extension | Format fixed by design section 5.1. `scenario: "daily"`, `golden_revision: 1`, shape block inside the golden, 24 step records, derived `peak_step`, `energy_kwh` with its own reconstruction check. The snapshot `golden.json` must remain byte-identical |
| 7 | `references/fixtures.json` + schema | Add the daily scenario record for `ieee13`; `run_fixtures.py` must check both scenarios and generate either golden |
| 8 | `docs/audits/phase4_loadshape_daily_audit.md` | Build audit with the environment block, exact commands, and the 24-step summary |
| 9 | `references/sources.json`, `dss_capi.json`, `examples.json`, `tools/validate_catalogs.py` | Additive only; register the LoadShape pair so validation reports 18 |

## Acceptance

1. `validate_catalogs.py` → 18/18 pairs. `run_examples.py` → 18 examples PASS with environment blocks. `run_fixtures.py` → all three checks PASS: ieee13 snapshot, ieee34 snapshot, ieee13 daily.
2. The snapshot goldens are **byte-identical** to `HEAD` before and after. Prove it with a hash comparison, not a test pass.
3. The daily golden's `energy_kwh` agrees with its own reconstructed integral, and `peak_step` is the step with the highest `load_kw`.
4. Every catalog row carries pinned `source_refs`; no `Properties*` page is cited for LoadShape; no unpinned URL is cited as evidence.
5. All 22 keys appear once, with units where the engine has them (`Interval` hours, `SInterval` seconds, `MInterval` minutes, `PMax`/`QMax`/`PBase`/`QBase` kW/kvar).
6. The readback matrix runs clean and the committed copy reproduces byte-identically on a re-run, allowing only the recorded capture date to differ.
7. F-1 from 4.2 is applied, and the 4.2 catalog, matrix and workflow are otherwise unchanged (verify with a path-filtered diff).
8. No Phase 3 catalog, no 4.1 fixture input, no 4.2 artifact beyond the F-1 lines, and no schema file changed except the new pair registration and any `fixtures.schema.json` declaration the daily scenario genuinely needs.

## Out of scope

`GrowthShape`, `CapControl`, `GenDispatcher`, `AutoTrans`, `PVSystem`, `Storage`, `InvControl` and `ExpControl` are deferred by decision 17 — do not catalogue them, and do not add a `CapControl` to make the capacitor banks switch. QSTS is not required; the profile is one daily pass at a 1-hour step. The cross-interface tool is 4.4 and the exit pass is 4.5; plan and manifest reconciliation stays there.
