# Phase 4.3 LoadShape catalog and daily profile — Architect/Auditor Review

**Reviewed branch:** `wp/phase4`, tip `be6e780` (QA/QC report commit), clean working tree at review start.
**Package revision under review:** `2e4d92b40b799280ed23429314b2ddddae75de7a` (LoadShape catalog, daily golden, harness extension, workflow, examples, readback matrix).
**Inputs/baseline revision:** `5efeaf1a97f4a63b5f4ec828cc63` — the commit that accepted 4.2 and issued this handoff.
**Review date:** 2026-11-21 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; engine sources fetched at `dss_capi@0.14.5`, wrapper compared against the installed `0.2.4` wheel.

**STATUS:** PASS WITH FINDINGS (nothing blocking; both findings are corrections to my own documents, not to the package)

The package inherited a handoff written from probes taken before it existed. Two of those handoff statements turned out to be less precise than what the package measured, and the package is right in both cases; I corrected my documents rather than the catalog.

## PROPERTY FINDINGS

- **Coverage is exact.** 1 record, `element_class: LoadShape`, **22 rows**, matching the `LoadShapeProperties` key set one for one. `required_properties` is `name`, with the effective `NPts` + array requirement placed in `property_requirements.conditional`, including the ordering note, exactly as the handoff asked.
- **Every default matches my own fresh-object probe:** `NPts` 0, `Interval` 1, `SInterval` 3600, `MInterval` 60, `Hour`/`PMult`/`QMult` empty, `Mean`/`StdDev` 0, `UseActual` false, `PMax` 1 / `QMax` 0, `PBase`/`QBase` 0, file properties empty, `MemoryMapping` false, `Interpolation` 0, `Action`/`Like` as methods.
- **Units are carried in row metadata, not only in prose:** `interval` `hour`, `sinterval` `s`, `minterval` `min`; `pmult`/`qmult` declare `array_element_type: float64` and `array_length: "NPts when supplied"`. This is a better shape than the Phase 3 element catalogs, which buried units in descriptions.
- **The methods are modelled as methods.** `action` and `like` carry `python_method`, `python_creation_status` and `dss_text_write`, and `action`/`interpolation` carry `enum_type` (`LoadShapeAction`, `LoadShapeInterpolation`). The keyword-versus-method trap from 4.2 is applied consistently rather than rediscovered.
- **The hard traps are in the data.** `interval`, `sinterval` and `minterval` each state that they write the same field; `npts` states that an edit changes the count without resizing allocated arrays and points at the replacement workflow; `pmult` states the exact-length requirement and the `Mult` alias; `csvfile` states both the empty-string read and the pending-statistics interaction.

## EVIDENCE FINDINGS

- **All 133 row references are pinned and in bounds.** Six distinct files across `AltDSS-Python@0.2.4` and `dss_capi@0.14.5`, correct tag per repository. I bounds-checked all 133 myself: 115 against locally available copies and the remaining 18 after fetching `src/General/DSSObjectHelper.pas` and `src/PCElements/Load.pas` at `0.14.5`. Zero violations, zero unparsed, zero mutable refs.
- **Citation hygiene holds.** The catalog contains no `Properties` page reference and no `dss-extensions.org` URL; the only EPRI URL is `LoadShape.html`, which is the page that actually carries the LoadShape property narrative. That is the correction I made to the design page map in the issuing commit, applied.
- **Catalog growth is additive.** `sources.json` 110 → 119, `dss_capi.json` 134 → 144, `examples.json` 16 → 18 with no record removed.
- **A-1 (architect-side correction, applied).** My handoff trap 5 said that reading `CSVFile` on a shape with no data raises `(#61107)`. The package's matrix is more accurate, and I confirmed it: a **fresh** shape reads `CSVFile` as `""`, `Mean` returns `0.0`, and the `#61107` surfaces on the **next checked read after a statistics getter**, because that getter leaves the engine error pending. Reproduced: fresh read → `''`; `Mean` then `CSVFile` → `(#61107) LoadShape has no data to be normalized`; after the error is consumed → `''`. My original probe had walked `Mean`/`StdDev` before `CSVFile`, which is why I saw a raise and called it a property of the read. The handoff now describes the pending-error mechanism.

## REQUIREMENT FINDINGS

- **The golden follows design section 5.1 exactly.** `scenario: "daily"`, `golden_revision: 1`, `solver.mode: Daily`, `step_size_s: 3600.0`, the `shape` block identical to `fixtures.json`'s `daily.shape`, 24 step records with hours exactly `1..24`, per-step `controls` and `lowest_bus`, and a `peak_step` carrying only the full `buses`/`elements` capture plus its hour.
- **The file checks itself, and I checked it independently.** `from_steps` 73416.54014883189 equals my own `math.fsum` of the recorded per-step `load_kw` exactly, and `integrated` 73416.54014883187 agrees to 1.5e-11. The peak derived from the data is hour 18 at 4004.670549958446 kW, identical to `peak_step.hour`. The lowest bus recomputed from `peak_step.buses` is `611` at 0.9520444393688189 pu, identical to the recorded `lowest_bus` at hour 18.
- **`peak_step` is a circuit capture, not a shape capture.** 38 elements — 12 lines, 5 transformers, 15 loads, 2 capacitors, 3 regulators, 1 source — with names exactly equal to the snapshot golden's element set, and **no `LoadShape` entry**. A shape is correctly treated as data rather than a circuit element.
- **The capacitors are energised, not switched.** Both banks report `states: [1]` at every step, identical to the snapshot golden's `[1]`, and the fixture contains no `CapControl`. This is what decision 17 predicted and what the handoff required.
- **The regulator taps do move.** `reg1` and `reg3` span taps 7–11, `reg2` spans 6–7 across the day, so the daily series is exercising control action rather than repeating the snapshot.
- **A-2 (architect-side correction, applied).** Design section 5.1's illustrative step snippet shows `"Capacitor.C1": {"states": [1, 1, 1]}`. The fixture's capacitors record one state each, because they are single-phase elements in this circuit; taking my snippet literally would suggest three states are expected. I changed the snippet to the fixture's actual shape so the format example cannot mislead.
- **The F-1 rider is exactly scoped.** The RegControl changes are one clause in the `ptphase` description and one sentence in `docs/workflows/regcontrol.md`. Nothing else in the 4.2 catalog, matrix or QA report moved — verified by path-filtered diff.

## SCHEMA RESULT

**pass.** `tools/validate_catalogs.py` → 18/18 pairs, exit 0, with the LoadShape pair registered against the existing `element_properties.schema.json` (no element schema change).

`fixtures.schema.json` did change, and I checked it rather than accepting the count: the diff is a `$ref` refactor plus a new scenario. `golden_updates` moved into `$defs/goldenUpdates` and `dailyScenario` was added; a structural comparison of every `required`/`enum`/`type`/`minimum`/`pattern`/`additionalProperties`/`uniqueItems`/`minItems`/`format` constraint between the baseline and the current schema reports **zero changed constraints**, with all 14 relocated paths reappearing identically under `$defs`. No constraint was weakened to admit the new scenario, and `dailyScenario` is closed (`additionalProperties: false`) with `golden_path`, `golden_revision`, `golden_updates`, `solver` and `shape` all required.

## RUNTIME RESULT

**pass**, run by me on the pinned stack (Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, backend `0.14.5`).

| Check | Result |
|---|---|
| `tools/validate_catalogs.py` | 18/18 pairs, PASS |
| `tools/run_examples.py` | 18 examples PASS, including both LoadShape entries |
| `tools/run_fixtures.py` | 3/3 PASS — ieee13 snapshot, ieee13 daily (24 hours, 73416.540 kWh, peak 4004.671 kW at hour 18, lowest 611 at 0.952044 pu), ieee34 snapshot |
| `tools/readback_loadshape.py` | exit 0; stdout byte-identical to the committed matrix |

**Snapshot freeze verified by hash, not by a passing test:** `ieee13/golden.json` hashes to `f72d59d8…ef5f4` and `ieee34/golden.json` to `b06282a6…2709f` in the baseline blob, the current blob and the working tree. Both match the values recorded when 4.1 was accepted.

Claims I spot-checked beyond the handoff, all confirmed: `NumCircuitElements` is unchanged by adding a shape (2 → 2) and the circuit always carries `LoadShape.default`; `Action(Normalize)` with `PBase = 200` divides to `[0.5, 1.0, 2.0]` and clears `UseActual`; and a DSS text `Hour=(…)` write sets `Interval` to 0 while the typed Python `Hour` write leaves the configured interval — the asymmetry the workflow documents.

## Observations recorded without action

- **O-1 (commendable deviation).** My handoff offered the uninitialised values I read after growing `NPts` (`1.2e-12`, `6.08e+247`) as evidence. The package instead labels the unsafe resize path source-only and demonstrates the supported replacement-and-rebind workflow. That is the correct call: those slots are uninitialised memory, so committing them as expected readback would make the matrix flaky on the next run. The catalog description still warns about the hazard, which is what a reader needs.
- **O-2.** The matrix key `csv_read_after_statistics` is keyed by the statistics getter that leaves the error pending, not by the getter that raises. Combined with A-1 that is defensible and the tool's comments explain it, but a `pending_from` field or one sentence in the build audit would remove the ambiguity for the next reader.
- **O-3.** `npts_growth` and the `UseActual=True` path rest on readback and source evidence rather than a golden, which the QA report states as a limitation. No action: the golden is defined as `UseActual=False` by design section 5.1.

## REQUIRED CORRECTIONS

None to the package.

| ID | Owner | Change |
|---|---|---|
| A-1 | Architect | **Applied in this review.** Handoff trap 5 rewritten: `CSVFile` reads `""` on a fresh shape; `#61107` surfaces on the next checked read after a statistics getter, because that getter leaves the error pending |
| A-2 | Architect | **Applied in this review.** Design section 5.1 snippet changed to the fixture's actual single-state capacitor shape |
