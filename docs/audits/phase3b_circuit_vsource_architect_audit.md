# Phase 3B Package 2 Architect/Auditor Review

- **Date** 2026-11-21
- **Reviewer role** Architect/auditor (DeepSeek), independent of the coder (GPT-6.2 Sol) and of the QA/QC reviewer (Mistral 4)
- **Reviewed branch** `wp/phase3`
- **Package revision** `555f4f6` (Circuit and Vsource package); QA handoff pin `e37224c`; QA report `420b2e9`
- **Baseline** `861a6e6`
- **Reviewed working tree** clean; no auditor changes were required
- **Targets** AltDSS-Python 0.2.4 (tag commit `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee`), DSS-Python 0.15.7, DSS C-API backend 0.14.5 (tag commit `87d85c2622c8281b92255335bc7c09b11191b21d`)
- **Review environment** fresh venv from `tools/requirements-validation.txt`; Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, `jsonschema` 4.26.0
- **Sources inspected** wrapper `Vsource.py`, `CircuitElement.py`, `AltDSS.py` from the pinned 0.2.4 install; engine `VSource.pas`, `Circuit.pas`, `DSSGlobals.pas`, `CktElement.pas`, `CktElementClass.pas`, `PCElement.pas`, `PCClass.pas`, `Spectrum.pas`, `Solution.pas`, `ExecHelper.pas`, `ExecOptions.pas` at tag `0.14.5`; EPRI `Vsource` and `Circuit` pages

[Property catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [Workflow](../workflows/circuit_vsource.md) · [Build audit](phase3b_circuit_vsource_audit.md) · [QA/QC report](phase3b_circuit_vsource_qaqc.md) · [Readback matrix](phase3b_circuit_vsource_readback.json) · [Coder handoff](../handoffs/Phase_3B_Circuit_Vsource_Coder_handoff.md)

## STATUS: PASS

No blocking findings and no required corrections. Two non-blocking observations are recorded below; neither changes the catalog's accuracy. The package meets the element-package definition of done in plan §5.4 items 1–7 and is ready for owner disposition before Phase 3B package 3.

Source review and runtime execution are reported separately; neither substitutes for the other.

## Independent verification performed

| Check | Method | Result |
| --- | --- | --- |
| Schema pairs | `tools/validate_catalogs.py` | PASS 11/11, exit 0 |
| Example execution | `tools/run_examples.py` | PASS 6/6, exit 0, environment block matches pins, no drift warning |
| Readback matrix | `tools/readback_circuit_vsource.py` compared to the committed JSON | identical except `environment`/date fields; 37 cells = 34 `read back` + 2 `DSS text readback` + 1 `action` |
| Catalog structure | parse of both element records | `Circuit` 1 row, `Vsource` 36 rows; every row has non-empty `source_refs`; no duplicate row names |
| Citation resolution | all row, conditional, and element `sources` references mapped to pinned files | 181 references (126 unique), 0 unresolved, 0 out of range, 0 mutable `master`/`main` refs; tags 0.14.5 (73) and 0.2.4 (51) |
| Wrapper correspondence | `VsourceProperties` TypedDict parsed from the pinned 0.2.4 install | 33 keys ↔ 33 catalog `altdss_keyword` values, exact case, no extras on either side; rows without a keyword are exactly `name`, `z1`, `z0` |
| Engine correspondence | `TVsourceProp` and constructor read at `0.14.5` | 31 members after `INVALID` (`Bus1`…`puZIdeal`); 31 catalog rows cover them; `spectrum`, `basefreq`, `enabled` correctly attributed to `PCClass`/`PCElement`/`CktElement` |
| Defaults | catalog `default_value` compared with every `read back` cell | all 15 null defaults are exactly the derived, dynamic, or generated fields; every non-null default matches the matrix and the constructor |
| Baseline preservation | `git diff 861a6e6..555f4f6` | zero removed lines in `dss_capi.json` (45→59), `sources.json` (34→51), `examples.json` (4→6); 8 added files, 8 modified docs/tools, no stray downloads |
| Link check | 109 relative links across the changed docs | 0 missing targets |
| Counts asserted in the build audit | recount | 51 sources, 59 engine records, 6 examples, 37 matrix cells, 10 `pass` / 4 `not-run` additions — all confirmed |

## PROPERTY FINDINGS

None blocking.

- **Coverage is exact and arithmetically consistent.** 36 `Vsource` rows = 1 identifier + 33 creation keywords (including the `Like` action) + 2 DSS-text-only complex rows (`z1`, `z0`). Of the 31 engine rows, 29 carry Python keywords, 2 are DSS-text-only, and the remaining 4 keywords (`Spectrum`, `BaseFreq`, `Enabled`, `Like`) are inherited or action rows with their own citations.
- **Thin `Circuit` entry was implemented as scoped.** One `name` row plus routing requirements and notes; no Vsource rows are duplicated, so there is a single source of truth for the source parameters. The identifier row cites `ExecHelper.pas` L227-L262, which is `DoNewCmd`'s `CompareText(ObjClass, 'circuit')` branch into `MakeNewCircuit` — the correct routing point.
- **No unsupported or mislabeled rows.** `z1`/`z0` carry `supported_in_target: true` and no `altdss_keyword`, and their descriptions state that the pinned Python wrapper has neither attribute. That is accurate: the engine and DSS text reach the properties, only the Python member is missing. See O-2.
- **Derived and generated defaults are left null rather than guessed.** `r1`/`x1`/`r0`/`x0`, `isc3`/`isc1`, `frequency`, `basefreq`, `bus1`, `bus2`, `z2`, `puZ1`/`puZ0`/`puZ2`, and the shape fields carry null defaults, and the matrix records what a fresh source actually reports. This is the correct treatment of the constructor-literal trap raised in the coder handoff.

## EVIDENCE FINDINGS

- **Every trap from the handoff is documented with source and runtime support, not asserted:** constructor ohms versus derived readback, `ZBase = BasekV²/BaseMVA` scaling, `pu` as voltage, the five specification families with their precedence behavior, circuit-dependent `Frequency`, integer enum readbacks, the `Spectrum` object default, and the `Z1`/`Z0` wrapper gap.
- **Code claims verified at the pinned tag:** `TVsourceProp` L57-L90; constructor L607-L669 (`Phases=3`, `Nterms=2`, `MVAsc3=2000`, `MVAsc1=2100`, `R1=1.65`, `X1=6.6`, `R0=1.9`, `X0=5.7`, `Isc3=10000`, `Isc1=10540`, `X1R1=4`, `X0R0=3`, `pu=1`, `BasekV=115`, `BaseMVA=100`, `Angle=0`, `ScanType=1`, `Sequence=1`, `puZIdeal=1e-6+0.001j`); `SpecSetNames`/`SpecSets` L228-L241 matching the five catalog `requirement_groups`; family switching L446-L505 (`ZSpecType` 1/2/3 and the `PrpSequence` resets); `ZBase` updates L510-L523; the MVA branch deriving `Isc3 = MVAsc3·1000/(√3·BasekV)` and `X0 = R0·X0R0` L710-L741; the per-unit branch using `puZ1·ZBase` L761-L772; the `puZ1` setter seeding unset `puZ0`/`puZ2` L419-L435; `MakeNewCircuit` passing the command remainder to `vsource.source` with a `SourceBus` default, `DSSGlobals.pas` L426-L449; grounded `Bus2` from `Bus1` when unset, `VSource.pas` L373-L393 and `L497-L498`; `BaseFrequency := ActiveCircuit.Fundamental` in `CktElement.pas` L203; `DefaultVSource := Find('defaultvsource')` in `Spectrum.pas` L131; the quasi-ideal branch L903-L932.
- **Enum text verified against the target surface:** `ScanType.Positive = 1`, `SequenceType.Positive = 1`, `VSourceModel.Thevenin = 0`, `Ideal = 1`. The rows' "Positive (1)" and "Thevenin (0) is the default" statements are correct.
- **My own coder handoff miscounted the enum.** It said "30 properties after `INVALID`"; the pinned source has 31 (`Bus1`=1 … `puZIdeal`=31). The coder catalogued and audited 31 correctly, and the QA review independently confirmed 31. The error was in the handoff, not in the package.
- **Range precision is good; three spans are slightly wide but land on the claimed constructs.** `capi-circuit-container` (L61-L118) runs a few lines past the class declaration into its field list; `capi-vsource-specification-sets` (L228-L246) includes the `bus1` required-flag line after the spec sets; `capi-vsource-complex-ohmic-access` (L77-L83) cites the enum tail as context for the complex rows. No correction is required — none of these misattributes a claim — and tightening them would not change meaning.
- **Evidence scope stays honest.** The EPRI pages are cited for the model concept only (`Vsource` intro paragraph; `Circuit` classic interface), the JS-rendered property tables are not mined, and every field-level claim rests on a pinned tag. `tested` is 10 `pass` / 4 `not-run`; all `pass` records reproduce in my run, and the `not-run` records are static source facts with a null environment.
- **Examples are real solves with honest scope.** Both new records are `Observed-working` with a committed file, harness run, environment, and date; the Python example asserts the routed source values, `Bus2 = src.0.0.0`, and bus nodes [1, 2, 3]. The audit states that the runnable examples are single-source solves and that standalone probes in the matrix are unsolved by design.

## REQUIREMENT FINDINGS

- **Specification sets are exact.** The five `requirement_groups` match `SpecSetNames`/`SpecSets` member for member, including `BaseMVA` in the per-unit group and the `X1R1`/`X0R0` ratio members in both short-circuit groups.
- **Precedence is described as observed behavior rather than as a rule.** "MVA/current/direct-impedance writes select the calculation family; an X/R edit affects the active family but does not switch it; an explicit `puZ1` can keep controlling ohmic recalculation" matches `ZSpecType` handling and the `PrpSequence` resets, and the matrix shows the retained value surviving a later MVA edit. The workflow's advice to use separate source definitions for cross-family comparisons follows from the code.
- **`required_properties` follows the published convention** — `Vsource` lists `name`, `bus1`, `basekv`, matching the Phase 2 `Line` precedent (`name`, `bus1`, `bus2`) and its note that the list records identity plus model inputs, not the Python signature. The conditional entry states explicitly that Python `new` needs only a name to allocate an object.
- **Mappings and casing confirmed at runtime:** `altdss_mapping` is `altdss.Vsource` for the source and the context command form for `Circuit`; `New Circuit.<name>` routing and `ctx.Vsource["source"]` readback are exercised by both examples and the harness; wrapper keyword casing (`MVASC3`, `MVASC1`, `puZ1`, `puZIdeal`, `BaseFreq`, `X1R1`, `X0R0`) matches the pinned TypedDict exactly.
- **No property is claimed that the pinned stack cannot reach,** and no reachable property is silently dropped.

## SCHEMA RESULT

**pass.** `tools/validate_catalogs.py` exits 0 with 11/11 pairs on the reviewed tree. The new catalog reuses `element_properties.schema.json` (registered in `SCHEMA_PAIRS`), keeps per-row `source_refs`, and permits the thin one-row `Circuit` entry, which validates.

## RUNTIME RESULT

**pass.** Executed by this review in a fresh venv on the pinned stack (Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, `jsonschema` 4.26.0).

- `run_examples.py`: 6/6 PASS; the two new examples report circuit `source_demo`, source `source`, 3 phases, `BasekV` 12.47, `pu` 0.98, `Angle` 5, `Bus1` src, `Bus2` src.0.0.0, `MVASC3` 250, solution 60 Hz, and bus nodes [1, 2, 3].
- `readback_circuit_vsource.py`: exit 0; output equals the committed matrix after removing `environment`/date. The harness asserts against the catalog, uses DSS text queries for `z1`/`z0`, and fails on drift.
- **Independent probes by this review**, outside the harness, reproduced the load-bearing claims: `Set DefaultBaseFrequency=50` then `New Circuit` gives 50/50/50 for solution, source `Frequency`, and `BaseFreq`; `Solution.Frequency = 55` leaves the source at 50; a later `BaseFreq = 48` changes only the element base. `puZ1 = 0.02+0.08j` at 115 kV yields 2.645/10.58 Ω, and a subsequent `R1 = 0.5`, `X1 = 1.5` is overwritten back to the per-unit values. `Z1`/`Z0` are absent as Python attributes but query correctly in DSS text, and `Z2` reads back as complex. `New Circuit.nobus` places the source on `sourcebus` with `Bus2 = sourcebus.0.0.0`.

## Required corrections

None.

## Observations (non-blocking)

| ID | Observation | Assessment |
| --- | --- | --- |
| O-1 | The `SourceBus` default for `New Circuit.<name>` without `Bus1` is stated in the engine record (`capi-new-circuit-source-routing`) but not in the `Circuit` entry or the workflow text. | Optional cross-reference for a later edit; the engine record carries the fact and `bus1` is listed as a required model input. No correction required for this package. |
| O-2 | `z1`/`z0` carry `supported_in_target: true` with no `altdss_keyword`. | Accepted. The engine and DSS text reach both properties and the descriptions state the missing Python member, so marking them unsupported would be less accurate than the current form. |

## Accepted limitations

1. `puZ1` can override later scalar ohmic edits inside the impedance branch and keeps its stored value after returning to the MVA family; the workflow recommends fresh source definitions for cross-family comparisons.
2. The pinned Python wrapper exposes `Z2` but not `Z1`/`Z0`; DSS text covers them and the matrix records the query path.
3. Runnable examples are single-source solves; standalone default and scaling probes are unsolved by design; harmonic, shape-driven, multi-source, and Phase 4 fixture validation are out of scope.

## Disposition

The package delivers the catalog, workflow, two executed examples, readback matrix, fourteen engine records, seventeen source records, build audit, and independent QA/QC report that plan §5.4 requires for the Circuit creation path and the Vsource element. Coverage, defaults, units, family precedence, and the wrapper gap were re-derived from the pinned sources and re-executed on a clean environment rather than accepted from the coder's or the QA reviewer's report.

Recommended owner action: accept package 2 and open Phase 3B package 3 (`Transformer`) on the same template. No coder remediation is outstanding for package 2.
