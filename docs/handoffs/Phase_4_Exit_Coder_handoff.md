# Phase 4 Package 4.5 — Phase 4 exit (coder handoff)

**Issued** 2026-11-22 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** 4.1–4.4, all accepted (decisions 16, 18, 19, 20). **Scope authority** plan section 6.5 (the stop gate) and section 6.7 (package 4.5).

## Goal

Close the charter stop gate. Packages 4.1–4.4 proved the fixtures reproduce and that the three Python surfaces agree. This package supplies the last two things the gate asks for that no earlier package owns: a **populated `troubleshooting.json`** built from failure modes that were actually seen, and a **documentation pass** that leaves every artifact describing the state the project is actually in.

Nothing here is new evidence about the engine. This is the package where the library stops describing what it intends to do and starts describing what it does.

## Where the stop gate already stands

| §6.5 item | State before 4.5 | Owner |
|---|---|---|
| 1. Fixtures compile, converge, match goldens from a clean env | Met — three golden runs pass, byte-identical by hash | 4.1, 4.3 (frozen) |
| 2. Cross-interface deltas within tolerance or dispositioned | Met — three pairs per fixture, zero deltas | 4.4 |
| 3. Golden metadata complete (source, checksums, license, versions, options, date, revision) | Met | 4.1, 4.3 |
| 4. **`troubleshooting.json` holds the observed failure modes with resolutions** | **Empty — 0 records** | **4.5** |
| 5. Independent QA/QC sign-off; `validation.runtime` states scope, environment, residual gaps | QA/QC signs each package; the manifest text is current as of 4.4 | 4.5 sign-off, architect writes the text |
| 6. Golden regeneration only via `--update-golden` with an owner-approved reason and a new revision | Met — the guard is implemented and unit-exercised | 4.1 |

So the work is item 4, the documentation pass, and an exit checklist that points at evidence for the rest. Do not re-prove 1, 2, 3 or 6 beyond re-running the harnesses to confirm they still pass.

## Deliverable 1 — `references/troubleshooting.json`

### The contract, read from the schema

`schemas/catalogs/troubleshooting.schema.json` is a top-level **array** whose items `$ref` `schemas/records/issue.schema.json`, which in turn `$ref`s `common.schema.json#/$defs/evidenceRecordFields`. In practice:

- **Required:** `id`, `version_range`, `evidence_level`, `source` (`title`, `url_or_path`, `accessed_or_captured` as a `date`), `kind` (must be the literal `"issue"`), `title`, `symptom`, `status`.
- **Optional:** `cause`, `safe_fix`, `diagnostic_evidence` (array of strings), `affected_versions` (array or null), `notes` (array), and `tested` (`target_version`, `environment`, `result` in `pass` / `fail` / `not-run`). **Corrected 2026-11-22 during the Phase 4.5 review:** `tested` is *not* reachable on issue records as issued. `common.schema.json` defines `$defs/tested`, but `evidenceRecordFields` never references it, so a record carrying `tested` is rejected by `unevaluatedProperties: false`. Add the reference to `schemas/records/issue.schema.json` (one line, one catalog's scope) or drop the block; adding it to `evidenceRecordFields` would widen every record type for a troubleshooting-only need.
- `status` accepts only **`confirmed`**, **`unresolved`**, **`superseded`**. There is no `resolved`; the resolution belongs in `safe_fix`, and a record is `confirmed` when the behaviour is reproduced and the fix is known.
- `evidence_level` accepts `Official-current`, `Official-versioned`, `Observed-working`, `Observed-export`, `Example-only`, `Inferred`, `Unverified`. A record you reproduced on the pinned stack is `Observed-working`.
- `unevaluatedProperties: false` sits on the issue record, and `source` and `tested` are closed objects too. **An extra field fails validation**, so do not carry scratch keys into the committed file.

A valid record, exactly as this package should write it:

```json
{
  "id": "ts-tapnumber-not-indexed",
  "kind": "issue",
  "title": "RegControls.TapNumber returns the active control's tap, not the indexed one",
  "symptom": "Walking the RegControl active class in opendssdirect and calling RegControls.TapNumber() returned 9, 9, 9 on ieee13, while the true taps are 9, 6 and 9.",
  "cause": "TapNumber is a property of the active RegControl, and the opendssdirect proxy accepts and silently discards the cursor index.",
  "safe_fix": "Read each tap by name with the text query: odd.Text.Command(f'? RegControl.{name}.TapNum'); int(odd.Text.Result()). In altdss use the object property reg.TapNum.",
  "diagnostic_evidence": [
    "text query ? RegControl.reg1|reg2|reg3.TapNum -> '9', '6', '9'",
    "RegControls.TapNumber() inside an ActiveClass walk -> 9, 9, 9"
  ],
  "affected_versions": ["opendssdirect.py 0.9.4", "dss-python 0.15.7"],
  "status": "confirmed",
  "version_range": "opendssdirect.py 0.9.4 / dss-python 0.15.7 / DSS C-API 0.14.5",
  "evidence_level": "Observed-working",
  "source": {
    "title": "Phase 4.4 architect review, tap readback",
    "url_or_path": "docs/audits/phase4_cross_interface_architect_audit.md",
    "section_or_record": "Process isolation and accessor mapping",
    "accessed_or_captured": "2026-11-22"
  },
  "tested": {
    "target_version": "0.14.5",
    "environment": "Windows 11 AMD64, Python 3.14.6, altdss 0.2.4, dss-python 0.15.7, opendssdirect.py 0.9.4",
    "result": "pass"
  },
  "notes": ["Reproduced independently by the architect during the 4.4 review and again while preparing this handoff."]
}
```

Populate to roughly **12–16 records**. Write only what you re-observe yourself; the seeds below tell you where to look, not what to assert. If a seed does not reproduce on your install, record it as `unresolved` with what you saw instead, or drop it — a short honest catalog beats a long copied one.

### Seeds, each measured on the pinned stack while this handoff was prepared

Re-run every one before recording it.

| # | Symptom as observed | Cause | Safe fix | Where it was seen |
|---|---|---|---|---|
| 1 | `RegControls.TapNumber()` inside an `ActiveClass` walk returned `9, 9, 9` on `ieee13`; `? RegControl.regN.TapNum` returns `'9'`, `'6'`, `'9'` | `TapNumber` is the active control's property and the proxy discards the index | text query by name, or `reg.TapNum` in altdss | 4.4 review |
| 2 | `dss.Text.Command("solve")` → `TypeError: 'str' object is not callable`; `dss.Text.Commands` is the method | `Text.Command` is a `str` property in dss-python | assign the property, or call `Commands` | 4.4 handoff trap 1, re-observed |
| 3 | `dss.DSS.Solution` → `AttributeError: 'IDSS' object has no attribute 'Solution'` | the solution hangs off the active circuit, not the DSS object | `dss.DSS.ActiveCircuit.Solution` | re-observed while preparing this handoff |
| 4 | `Solution.Totaliterations` (lower-case `i`) on dss-python returns `2`; `TotalIterations` does not exist there; opendssdirect has `TotalIterations()` | naming split between the two dss-derived surfaces | pick per surface; both are documented in `python_interface_comparison.json` | re-observed |
| 5 | `dss.DSS.ActiveCircuit.ActiveClass.First` is an `int` (calling it → `TypeError: 'int' object is not callable`); `odd.ActiveClass.First()` is a method | property/method flip | do not wrap both in one adapter | 4.4 handoff trap 4, re-observed |
| 6 | `CktElement.Losses()` → `[60728.50, 195986.08]` while `CktElement.TotalPowers()` → `[3566.70, 1735.85, -3505.97, -1539.86]` on `Line.650632` | `Losses` is W/var, `TotalPowers` is kW/kvar | divide losses by 1000 before comparing; `compare_interfaces.verify_loss_scale` backstops it | 4.1 E-1, re-observed |
| 7 | `edit RegControl.reg2 TapNum=5` then `? RegControl.reg2.TapNum` → `5`; after `Solve()` → `6` | a controlled solve overwrites a manual tap | record the tap after the solve, or fix the regulator with `Controlled=No` | 4.2 trap, re-observed |
| 8 | `edit RegControl.reg2 PTPhase=7` then `? RegControl.reg2.PTPhase` → `1` | out-of-range positive reads back as the first valid index | validate `PTPhase` as a 0-2 `VBuffer` index before writing | 4.2 finding F-1, re-observed |
| 9 | `hasattr(Capacitors, "Spectrum")` → `False`, `hasattr(Loads, "Spectrum")` → `True` | the Capacitor element has no Spectrum | do not set a harmonic spectrum on a capacitor | Phase 3B Capacitor catalog, re-observed |
| 10 | `altdss` context A compiled `ieee13`, then context B `NumCircuitElements` → `(#8888) There is no active circuit!`; a second compile through `odd` while dss-python held one raises `(#266) Warning: Duplicate new element definition` | altdss isolates per context; dss-python and opendssdirect share one engine | one process per interface/context, or accept the isolation | 4.4 trap 9, both halves re-observed |
| 11 | `ctx.LoadShape.new("s1")` on an existing shape returned `NPts = 0`, and iterating the collection then shows `LoadShape.s1` twice (`NPts` 3 and 0); `ctx.LoadShape["s1"].NPts` still reads `3` | `.new(name)` creates, it does not fetch; a duplicate name is allowed | fetch with `ctx.LoadShape[name]`; create only once | re-observed while preparing this handoff |
| 12 | `ctx.LoadShape` is an `ILoadShape` with no `.New`; `.New("x")` → `AttributeError` | the collection proxies expose lower-case `new` | use `.new(...)` or the text interface | re-observed |
| 13 | `new LoadShape.c1 csvfile=[nonexistent.csv]` → `(#613) Error opening file: "nonexistent.csv"`; `shape.CSVFile` on an empty shape reads `''` without raising, and a statistics getter leaves `#61107` pending | the CSV read is lazy and the error surfaces later | read `CSVFile` only after a shape with `NPts > 0`, and clear the pending error before the next assertion | 4.3 A-1, both halves re-observed |
| 14 | assigning a two-element `PMult` to a shape whose `NPts` is 0 → `(#20200425) LoadShape.s1.PMult: Invalid number of elements. Expected 0 elements, got 2.` | `PMult` must match `NPts` exactly, in both directions | set `NPts` first, then assign the full-length array | 4.3 trap, re-observed |
| 15 | after a bare `NPts = 4` the read-back `PMult` was an **empty** array, `array([], dtype=float64)`, not four values | the array is resized without initialisation, and the length reported follows the element's own sense of how many points are set | never read `PMult` after a bare `NPts` grow; write the whole array and re-read | 4.3 trap; my re-observation differs from the 4.3 note that recorded uninitialised values, so record what you see, not this row |

`source.url_or_path` may point at a repository path (as above) or at a pinned upstream URL. When you record the engine's own behaviour, cite the DSS C-API `0.14.5` source or your own `diagnostic_evidence`; never cite an EPRI page for behaviour, since the EPRI documentation is mixed-version and says nothing about the wrapper surfaces.

## Deliverable 2 — `docs/workflows/troubleshooting.md`

An index, not a second copy: group the records by symptom (control state, unit confusion, accessor shape, per-interface quirks, creation and data errors), one line each, linking to the record `id`. It must open by stating that these are wrapper and engine behaviours observed on the pinned stack, that a case not recorded here is not asserted to be impossible, and that the `python_interface_comparison.json` catalog is the accessor mapping while this page is the failure index.

## Deliverable 3 — documentation pass

The library README is the artifact that most visibly drifted. Fix at least:

| File | Drift |
|---|---|
| `opendss_altdss_library/README.md` | says the DSS C-API catalog holds **119** records (it holds 144) and the example catalog **14** (it holds 19); the Contents list omits `regcontrols/`, `loadshapes/`, `fixtures.json`, `python_interface_comparison.json` and the fixtures tree; the Validation block omits `run_fixtures.py`, `compare_interfaces.py`, `readback_regcontrol.py` and `readback_loadshape.py`; the closing line says three catalogs remain empty when only `opendss_objects` and `troubleshooting` do |
| `README.md` (root) | Phase 4 sentence still reads as if package 4.4 were issued rather than delivered; add the 4.5 exit state once this package lands |
| `docs/phase_4/README.md` | section 5.1 and the package table should point at the delivered artifacts rather than describing them as planned |

Resolve the four observations from the 4.4 review, or decline each with a recorded reason:

- **O-1** the committed comparison report is a *result summary*, not a snapshot set. Say so in `docs/workflows/cross_interface.md` and in the report-reading instructions.
- **O-2** `examples/interfaces/compare_ieee13.py` is a driver, not a tutorial. One sentence in the workflow page so nobody reads it as the explanation.
- **O-3** `examples.schema.json` has no cross-interface language value, so the record claims `python_altdss` for a three-interface script. Add an enum value (`python_cross_interface`) and update the record, or annotate the record and say in the build audit why the enum is left alone.
- **O-4** `verify_loss_scale` is a magnitude heuristic, not a unit assertion. One sentence where the tool is described.

## Deliverable 4 — `docs/phase_4/exit_checklist.md`

One row per plan section 6.5 item, each with the command that proves it and the artifact that records the result, plus a short section listing what Phase 4 **does not** cover: no year-long QSTS, no harmonics, no unbalanced-fault study, daily profile on one fixture only, deferred classes per decision 17, `opendss_objects` still empty for Phase 5. A stop gate that overstates its coverage is worse than one that never closed.

## Deliverable 5 — `docs/audits/phase4_exit_audit.md`

Build audit: environment, exact commands, tool output, the record count in `troubleshooting.json`, and for each record the one-line observation that produced it. State plainly that no engine behaviour was inferred from an EPRI page and that schema validity is not runtime validation.

## Do not

- Do not edit `manifest.json` or `docs/implementation_plan.md`. Both are architect-owned; report your numbers in the build audit and the architect will fold them in.
- Do not touch the fixtures, the goldens, the accepted catalogs, `run_fixtures.py`, or `compare_interfaces.py` beyond documentation.
- Do not add element catalogs or any deferred class (decision 17).
- Do not invent a `resolved` status, a `resolution` field, or any other field the schema does not declare.
- Do not cite an EPRI page for wrapper or engine behaviour.

## Acceptance

1. `references/troubleshooting.json` is non-empty, schema-valid, and every `confirmed` record carries a `tested` block with `result: "pass"` and the pinned environment. No record claims an observation you did not make.
2. `validate_catalogs.py` passes all pairs (18 today, 18 after this package), `run_examples.py` passes all 19, `run_fixtures.py` passes all three, and `compare_interfaces.py` still produces a report byte-identical to `docs/audits/phase4_cross_interface_report.json`.
3. Goldens, fixtures and accepted catalogs are unchanged, proven by hash rather than by a passing test.
4. `git diff` for the package stays inside `docs/`, `references/` and, if you take O-3, the single additive `examples.schema.json` enum value; record that decision either way.
5. Every stop-gate item maps to a command and an artifact in `docs/phase_4/exit_checklist.md`, and the coverage limits are stated.
6. The documentation pass leaves no file claiming a catalog is empty, a record count that is wrong, or a package as pending that has landed.
