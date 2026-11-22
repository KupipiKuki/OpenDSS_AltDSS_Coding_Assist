# Phase 4.2 RegControl Catalog — Architect/Auditor Review

**Reviewed branch:** `wp/phase4`, tip `97ecbce` (QA/QC report commit), clean working tree at review start.
**Package revision under review:** `35a2b7cc4de10c1f8515f5996eca2cdec088bbee` (catalog, readback matrix, workflow, examples, build audit, QA handoff).
**Inputs/baseline revision:** `eb7aca4aac119b1c4478efd958a2aae10fd9d463`.
**Review date:** 2026-11-21 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; independently fetched sources at `AltDSS-Python@0.2.4` and `dss_capi@0.14.5`.

**STATUS:** PASS WITH FINDINGS (nothing blocking; one recommended correction F-1 and one architect-side correction A-1 applied)

This review was run as a check of the handoff's predictions rather than a re-derivation: the fourteen traps recorded in [the coder handoff](../handoffs/Phase_4_RegControl_Catalog_Coder_handoff.md) were probed before the package existed, so every overlapping claim was compared against a measurement already in hand.

## PROPERTY FINDINGS

- **Coverage is exact.** 35 rows = the 32 `TRegControlProp` members (`RegControl.pas` L69-L103 at `0.14.5`) plus `BaseFreq`, `Enabled`, `Like`. I confirmed the row names are unique, and that every row carries a non-empty `description`, `altdss_keyword` and `source_refs`. No missing, duplicate or unsupported property.
- **Defaults match the constructor row by row.** All 32 concrete defaults agree with the values I read from `RegControl.pas` L486-L553 and probed at runtime: `VReg` 120, `Band` 3, `PTRatio` 60, `CTPrim` 300, `Delay` 15, `TapDelay` 2, `MaxTapChange` 16, `RevDelay` 60, `RevThreshold` 100 (kW), `PTPhase` 1, `R`/`X`/`RevR`/`RevX`/`LDC_Z`/`Rev_Z` 0, `Reversible`/`RevNeutral`/`Cogen`/`InverseTime`/`EventLog`/`DebugTrace` false, `Enabled` true, `Bus` empty, `Winding` 1. The seven null defaults (`transformer`, `TapWinding`, `RemotePTRatio`, `TapNum`, `Reset`, `Like`, `BaseFreq`) are unset references, derived values or actions, and the record's `notes` says exactly that.
- **Units are stated where the engine flags them:** volts (`VReg`, `Band`, `RevVReg`, `RevBand`, `VLimit`), amperes (`CTPrim`), seconds (`Delay`, `TapDelay`, `RevDelay`), kW (`RevThreshold`), hertz (`BaseFreq`). `Band` and `RevBand` are correctly described as test-side volts and as a total width, which is the distinction that bites when someone reads `Band` as a half-width.
- **The trap set is present in the data, not only in prose.** Verified against my own probes: `vreg` states the exact `VReg` spelling; `tapnum` states that a later controlled solve can select a different tap and that `ControlMode=Off`/`SolveNoControl` held the write; `tapwinding` states that it follows `Winding` and must be written after it; `ptratio`/`remoteptratio` state the re-initialisation order; `maxtapchange` states the one-step budget failure; `reset`/`like` carry `python_method` + `dss_text_write` + `python_creation_status` instead of repeating the keyword trap as prose. My readings reproduce theirs exactly: manual 5 → solved 9 in 12 iterations, ±99 → ±16, `Winding=2`/`TapWinding=1` at 1.025 with winding 2 held at 1.05625.
- **F-1 (recommended, coder-applied).** The `ptphase` row and the workflow say to use an in-range index, but neither states what happens when you do not. Their own matrix records it: `sensing.pt_phase.out_of_range_positive` = `{written: 4, after_edit: 1}`. I reproduced it: writing `PTPhase = 4` on a three-phase winding reads back **1** silently, while `2` sticks and `-3`/`-2` return `RegControlPhaseSelection.min`/`max`. **Requested correction:** append one clause to the `ptphase` description in `references/regcontrols/regcontrol_properties.json` and one sentence to the `PTPhase` paragraph in `docs/workflows/regcontrol.md`, stating that an out-of-range positive index reads back as 1. Source: [`RegControl.pas` L639-L680 @0.14.5](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L639-L680) plus the recorded probe. This is a completeness gap in a caution, not a wrong claim, so it does not block acceptance.

## EVIDENCE FINDINGS

- **All 177 row references are pinned and in bounds.** Eight distinct files, tags correct per repository (`AltDSS-Python@0.2.4`, `dss_capi@0.14.5`), no file-only references, zero out-of-range or past-EOF ranges. I fetched all eight files at the pinned tags and bounds-checked every range independently of the package. Spot content checks land on the claim: `tapnum` → the property-table registration, `ptphase` → the wrapper TypedDict line, `enabled` → `SampleControlDevices` in `Solution.pas`.
- **Sources outside the row set also check out.** `altdss-solution-solve-no-control` cites `altdss/Solution.py#L83-L90`, where `SolveNoControl` sits at L89; `capi-solution-solve-no-control` cites `CAPI_Solution.pas#L632`, which is `procedure Solution_SolveNoControl` exactly; `capi-control-terminal-currents` cites `ControlElem.pas#L166-L178`, which is `GetCurrents` zeroing the array — the actual basis for the "zero powers" claim.
- **EPRI citations are limited to the pages that exist.** Only `RegControl.html` and `Properties23.html` are cited, both live (200). The 404 pages `RegControl1.html` and `Regulators.html` are not cited anywhere, and `target_versions.opendss_documentation` states "EPRI online documentation is mixed-version", so no field implies an unpinned current release.
- **Catalog growth is additive.** `sources.json` 100 → 110 and `dss_capi.json` 119 → 134 and `examples.json` 14 → 16, with zero removed identifiers in all three. The 15 new `dss_capi` records are all `capi-regcontrol-*`, each with `target_version 0.14.5` and an environment block; 14 record `pass` and `capi-regcontrol-reverse-and-compensation` records `not-run`, which matches the documented coverage limit rather than overclaiming.
- **O-2 (observation).** The build audit cites `https://dss-extensions.org/AltDSS-Python/changelog.html` and the releases page as prose context for the 0.2.4 choice. Neither is unpinned *evidence* for a property claim, and no catalog field uses it, so this is not a violation of the citation rule added in [the Phase 4 design §8.1](../phase_4/README.md). Package 4.5's documentation pass should decide whether prose-context URLs need pinning for consistency.

## REQUIREMENT FINDINGS

- **Minimum inputs are distinguished from the engine surface.** `required_properties` is `name` + `transformer`, with `name` correctly explained as the separate first argument to `ctx.RegControl.new`, and the record's first note states that the 35 rows describe advertised keywords while the identifier is a collection argument. That is the distinction the QA checklist asks for.
- **The conditional ordering requirement is sourced.** `property_requirements.conditional` requires `Winding` before `TapWinding` when monitoring one winding and moving another, citing the engine's `Winding` setter and the wrapper's setter path. I verified the behaviour behind it: writing `Winding=2` restored `TapWinding=2` after it had been reassigned to 1.
- **A-1 (architect-side correction, applied).** My handoff asserted that `#123` is unreachable through Python and text and should be marked source-only without qualification. That is too strong: passing a non-transformer element object violates the declared `str | Transformer | AutoTrans` input and reaches the guard. Reproduced: `Context.RegControl.new("inject", Transformer=ctx.Line[0])` raises `Controlled Regulator Element "l1" is not a transformer.` The package handles this better than the handoff did — the matrix and workflow scope `#123` as source-only "for the supported reference paths", and the build audit records the out-of-type injection explicitly. I corrected the handoff so the error does not propagate into the remaining control catalogs. No package change requested.
- **Scope is clean.** `git diff eb7aca4..HEAD` touches 16 files, all under `docs/`, `references/`, `examples/` and `tools/`. No Phase 3 or 4.1 catalog, no fixture file, no golden and no schema changed; the only library-wide edits are the additive source, engine and example records and the single `SCHEMA_PAIRS` entry.

## SCHEMA RESULT

**pass.** `tools/validate_catalogs.py` → 17/17 pairs, exit 0. The new pair reuses `schemas/catalogs/element_properties.schema.json` unchanged, as the handoff required. All the row fields this package uses — including `python_creation_status`, `python_method`, `dss_text_write`, `enum_type`, `reference_class` and `readback_type` — are declared in that schema, so the undeclared-row-field class of finding raised as O-1 in Phase 3 does not recur.

## RUNTIME RESULT

**pass**, run on the pinned stack (Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, backend `0.14.5`, `jsonschema 4.26.0`).

| Check | Result |
|---|---|
| `tools/validate_catalogs.py` | 17/17 pairs, PASS |
| `tools/run_examples.py` | 16 examples PASS, including both RegControl entries |
| `tools/run_fixtures.py` | both revision 1 goldens PASS (ieee13 16/38/2, lowest 611 @ 0.960843; ieee34 37/117/25/6 ctrl, lowest 890 @ 0.923099) — the regulator-bearing goldens are unmoved |
| `tools/readback_regcontrol.py` | exit 0; stdout byte-identical to the committed matrix after line-ending normalisation, reproduced by me, not taken from the report |

Every measurement in the matrix that overlaps my pre-handoff probes agrees: tap 9 ← manual 5 on a controlled solve, hold at 5 under `ControlMode=Off` and `SolveNoControl`, ±16 clamping, `TapWinding` divergence, `#485` from a one-step limit, `#124` for omitted/unknown/wrong-class names, `#482` on a bare create, `#122` for `Winding=5`, zero `TotalPowers()`, `Enabled=False` holding tap 9. The `#123` reproduction above is the only claim in the package I could not match to a prior probe, because my handoff had predicted it unreachable.

## Observations recorded without action

- **O-1.** `reset` and `like` are modelled as rows with `python_method`/`dss_text_write`/`python_creation_status` rather than as prose traps. This is the right shape for the third package to hit the keyword-versus-method trap, and it sets the pattern the remaining control catalogs should copy.
- **O-3.** The `.dss` example contains no assertion of its own — its expected tap 4 and 122.91429 V are checked by the runner and the readback tool, and `examples.json` says so in `expected_result`. Acceptable for DSS text, where a self-check is not expressible, but it should stay explicit in future DSS examples rather than becoming an assumption.
- **O-4.** Every row carries `evidence_label: Official-versioned` even where the description reports a probe result ("left the transformer tap unchanged in the probe"). This matches how the Phase 3 catalogs are labelled (verified across all seven: no row uses a runtime label) and the probe record lives in the matrix, so it is a consistent convention rather than a 4.2 defect.

## REQUIRED CORRECTIONS

None blocking acceptance.

| ID | Owner | Change |
|---|---|---|
| F-1 | Coder | Add one clause to the `ptphase` row and the workflow paragraph: an out-of-range positive `PTPhase` reads back as 1 (matrix `sensing.pt_phase.out_of_range_positive`, reproduced) |
| A-1 | Architect | **Applied in this review.** Handoff statement that `#123` is unreachable replaced with the out-of-type injection route and the supported-path scoping the package actually uses |
