# Coder Handoff: Phase 3B Package 6 — Generator

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3`. Packages 1–4 are accepted. Package 5 (Capacitor) is released to the coder with handoff `docs/handoffs/Phase_3B_Capacitor_Coder_handoff.md`. **The owner directed this handoff to be prepared in parallel; do not start coding package 6 until package 5 is accepted unless the owner says otherwise.** Commit package 6 separately.

Generator is the last of the six element packages in plan §5.3, and it is the first one whose properties do not fully determine the solved result: several of them act only through dispatch controls that this package does not cover.

## Goal

Deliver Phase 3B package 6 — the **Generator** element — with the same six-artifact pattern used for the other element packages. The defining difficulties are:

1. `kVA` and `MVA` are **machine ratings**, not power specifications, so the load-style "families" idea does not carry over;
2. the wrapper's readbacks are the **scheduled** setpoints, while the solved injection is only visible through terminal powers;
3. `DispMode`, `DispValue`, `Status`, `ForceOn`, and `PVFactor` act through the **deferred** `GenDispatcher` control, so they must be described from source and labelled honestly.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Scope decision

1. **`Generator` is in scope; `GenDispatcher` is not.** `GenDispatcher` is a controller class with its own collection and property set (`src/Controls/GenDispatcher.pas`, `altdss/GenDispatcher.py`). Record a scope note; do not catalog its properties.
2. **One element class in the catalog.** `references/generators/generator_properties.json` with `element_class: Generator` only.
3. **Dynamic and user models are catalogue entries, not runtime targets.** `UserModel`, `UserData`, `ShaftModel`, `ShaftData`, `DynamicEq`, `DynOut` are catalogued with source citations; executing a compiled user-model DLL or a dynamics simulation is out of scope.
4. **Fuel properties are catalogued.** `UseFuel`, `FuelkWh`, `pctFuel`, `pctReserve`, and the `Refuel` action are in scope for description and readback; a fuel-consumption study is not.
5. **`PVSystem` and `Storage` are separate classes**, already present in the pinned engine (`src/PCElements/PVsystem.pas`, `src/PCElements/Storage.pas`), and are out of scope.

## What the pinned surface actually looks like

Verified on the pinned stack; re-confirm each point with a citation and a readback.

- **The engine file is `src/PCElements/generator.pas` — lower-case `g`.** `Generator.pas` returns 404, and `src/PDElements/generator.pas` does not exist. This is the single easiest citation to get wrong in this package.
- **`GeneratorProperties` has 47 keys** (`Generator.py` L896-L943) while `TGeneratorProp` has **44 members** (`generator.pas` L128-L175). The engine member the wrapper omits is **`MVA`**, which is text-only. The four additions are `Spectrum`, `BaseFreq`, `Enabled`, and `Like`. 44 − 1 + 4 = 47.
- **A generator has one terminal and 2–4 conductors**, inherited from the PCElement path: wye three-phase gives four conductors, delta three-phase three, one-phase two. `NumTerminals()` is always 1.
- **`MVA` is a redundant alias of `kVA`**, scaled by 1000 and flagged `Redundant` with `PropertyRedundantWith[MVA] = kVA` (`generator.pas` L639-L643). It has no Python attribute at all.
- **There are only two specification families**: `kW, PF` and `kW, kvar` (`generator.pas` L510-L517). Unlike `Load`, `PF` carries no `Ordering_Last` flag (L636-L637).

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- Package 5 for the most recent element pattern: [Capacitor handoff](Phase_3B_Capacitor_Coder_handoff.md)
- Package 4 for family and readback reasoning: [Load handoff](Phase_3B_Load_Coder_handoff.md) · [Load architect review](../audits/phase3b_load_architect_audit.md)
- Package 2 for the element-plus-command pattern: [catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [workflow](../workflows/circuit_vsource.md)
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Property catalog | `references/generators/generator_properties.json` | One `element_class`: `Generator`. Reuse `schemas/catalogs/element_properties.schema.json`; no new schema expected. Every row needs `source_refs`. |
| 2 | Source index additions | `references/sources.json` | EPRI Generator pages, the 0.2.4 wrapper modules, the 0.14.5 engine file, the inherited `PCElement`/`CktElement` files, `enums.py`, and a scope note for `GenDispatcher`. Additions only. |
| 3 | Engine records | `references/dss_capi.json` | The 44-member property enum, the two families, the rating-versus-specification distinction, the enums, the constructor defaults, the model dispatch routines, the nominal-versus-solved reactive behavior, the register set, and the action properties. Cite `0.14.5` ranges. |
| 4 | Workflow | `docs/workflows/generator.md` | Rating versus specification, sign convention, Model selection and what each model needs, `Vpu` as a target with kvar limits, dispatch coupling, shapes, fuel, and the traps below. |
| 5 | Examples | `examples/generator/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; include a solve that reports the generator's per-terminal complex power and a PV (Model 3) case that states the achieved voltage against the requested `Vpu`. `source_ids` recorded; `Observed-working` only after a harness run. |
| 6 | Readback tool and matrix | `tools/readback_generator.py`, `docs/audits/phase3b_generator_readback.json` | Defaults for every catalogued row plus the behavior probes below, with the environment block and date. |
| 7 | Audit | `docs/audits/phase3b_generator_audit.md` | Method, coverage counts, checks, limitations, hazards, open items, and the `GenDispatcher` scope note. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_Generator_QAQC_handoff.md` | Pinned to the package commit; checklist and report format as in the package 3 handoff. |

Register the catalog in `tools/validate_catalogs.py` (`SCHEMA_PAIRS`); expect 15/15 pairs.

## Sources

| Surface | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| Generator | `https://opendss.epri.com/Generator.html` (200; the element page) | `altdss/Generator.py` | `src/PCElements/generator.pas` |
| Generator property vocabulary | `https://opendss.epri.com/Properties9.html` (200) | `altdss/Generator.py` | `src/PCElements/generator.pas` |
| Enumerations | — | `altdss/enums.py` L286-L305 | `generator.pas` L449-L465 |
| Inherited element data and registers | — | `PCElementMixin`, `ElementHasRegistersMixin`, TypedDict | `src/PCElements/PCElement.pas`, `src/Common/CktElement.pas` |
| Dispatch coupling (scope note only) | — | `altdss/GenDispatcher.py` | `src/Controls/GenDispatcher.pas` |
| User and dynamic models (scope note only) | — | `altdss/GenUserModel.py` | `src/PCElements/GenUserModel.pas`, `src/General/DynamicExp.pas` |

**Page traps:** `Generator1.html` and `Generator2.html` both return **404** — the naming is the opposite of Load and Capacitor, where the numbered page is the element page. `Properties5.html` is the **Storage** page (54 `Storage` mentions) and must not be cited for Generator. `Properties9.html` is the Generator vocabulary page (44 `Generator` mentions, plus `ShaftModel` and "user model"). Verified live on 2026-11-21 by fetching the pages and counting tokens; the tables are JS-rendered, so a URL is citable but a field list is not extractable from a plain GET.

Line pins for this package: legacy enum `generator.pas` L80-L127; modern enum L128-L175; `TGeneratorVars` record L177ff; register names L467-L475; enum creation L449-L465; `DefineProperties` L500-L651; `SpecSetNames` L510-L513; `SpecSets` L514-L517; `Conn` registration L520-L522; `DispMode` L524-L526; `Status` L528-L530; `Bus1` L554-L556; `Model` L572-L574; `Maxkvar` L601-L602; `Minkvar` L604-L605; `PVFactor` L608; `DispValue` L609; `VMinpu` L610; `VMaxpu` L611; `DutyStart` L613-L614; `FuelkWh`/`pctFuel`/`pctReserve` L616-L618; `kVA` L620-L621; `Xd`/`Xdp`/`Xdpp`/`H`/`D`/`XRdp` L623-L628; `kV` L630-L631; `kvar` L633-L634; `kW`/`PF` L636-L637; `MVA` L639-L643; `Refuel` L645-L647; `PropertySideEffects` L679-L842; `MakeLike` L845ff; constructor L937-L1046; `SetNominalGeneration` L1108; `RecalcElementData` L1268-L1308; model routines `DoConstantPQGen` L1544, `DoConstantZGen` L1606, `DoPVTypeGen` L1635, `DoFixedQGen` L1694, `DoFixedQZGen` L1752, `DoUserModel` L1816, `DoCurrentLimitedPQ` L1838, `DoDynamicMode` L1923, `DoHarmonicMode` L2042; `MakePosSequence` L2786. Wrapper: `Generator` class L18, `_cls_idx` 27 (L21), `Refuel` method L771, `GeneratorProperties` L896-L943, `new` L1799. Enums: `GeneratorModel` L286-L294, `GeneratorDispatchMode` L296-L300, `GeneratorStatus` L302-L305.

## Established facts to reuse and re-verify

Reproduce each in your environment and record it; do not copy these numbers without a run.

**Defaults, `Generator.new("g1")` after a 12.47 kV three-phase circuit:** `Phases` 3, `Bus1` generated `g1_1`, `kV` 12.47, `kW` 1000.0, `PF` 0.88, **`kvar` 60.0**, `kVA` **1200.0**, `Model` `GeneratorModel.ConstantPQ`, `VMinpu` **0.90**, `VMaxpu` **1.10**, `Vpu` 1.0, `Maxkvar` 120.0, `Minkvar` −120.0, `PVFactor` 0.1, `DispMode` `GeneratorDispatchMode.Default`, `DispValue` 0.0, `Conn` `Connection.wye`, `Status` `GeneratorStatus.Variable`, `Class` 1, `ForceOn` False, `Balanced` False, `DebugTrace` False, `Xd` 1.0, `Xdp` 0.28, `Xdpp` 0.20, `H` 1.0, `D` 1.0, `XRdp` 20.0, `DutyStart` 0.0, `Yearly`/`Daily`/`Duty` None, `UserModel`/`UserData`/`ShaftModel`/`ShaftData` empty strings, `DynamicEq` None, `DynOut` empty list, `UseFuel` False, `FuelkWh` 0.0, `pctFuel` 100.0, `pctReserve` 20.0, `Spectrum` `<Spectrum.defaultgen>`, `BaseFreq` 60.0, `Enabled` True, one terminal, four conductors. Constructor constants (`generator.pas` L937-L1046): `kWBase` 1000, `kvarBase` 60, `kvarMax` 120, `kvarMin` −120, `PFNominal` 0.88, `Vpu` 1.0, `VBase` 7200, `Vminpu` 0.90, `Vmaxpu` 1.10, `GenVars.kVArating` = 1.2 × kW, `puXd` 1.0, `puXdp` 0.28, `puXdpp` 0.20, `Hmass` 1.0, `Dpu` 1.0, `XRdp` 20.0, `PVFactor` 0.1, `pctFuel` 100, `pctReserve` 20, `SpectrumObj` defaultgen.

**Enums:** `GeneratorModel` ConstantPQ 1, ConstantZ 2, ConstantPV 3, ConstantP_fixedQ 4, ConstantP_fixedX 5, Usermodel 6, Approximateinvertermodel 7. `GeneratorDispatchMode` Default 0, LoadLevel 1, Price 2. `GeneratorStatus` Variable 0, Fixed 1. `Connection` wye 0, delta 1.

**Behavior that must be documented and probed:**

1. **`kVA` is a rating, not apparent power.** `kW=2000, PF=0.9` gives `kvar` 968.6442 but **`kVA` 2400**, which is 1.2 × kW, not 2222.2. `kW=2000, kvar=400` leaves `kVA` at 2400 and derives PF 0.9806. `kVA=3000` alone changes no power at all. Do not model `kVA` as a third power family.
2. **`kVA` is a dynamic default.** While it has not been written, a `kW` write rescales it: default 1200, then `kW = 2000` → `kVA` 2400 and `kvar` 1079.4856 at PF 0.88. After an explicit `kVA = 5000`, a later `kW = 1000` leaves `kVA` at 5000. The `DynamicDefault` flag (L620-L621) is the mechanism.
3. **`MVA` exists only in DSS text.** `Generator.new("m", MVA=3.0)` and `g.MVA = 3.0` both raise `AttributeError: 'Generator' object has no attribute 'MVA'`, while `New Generator.m3 Bus1=... kV=12.47 MVA=3` works and sets `kVA` 3000. Catalog it as text-only with the redundant-alias citation.
4. **The default operating point is internally inconsistent.** Fresh readbacks are `kW` 1000, `kvar` 60, `PF` 0.88, `kVA` 1200; `kW`/`kvar` imply PF 0.9988, and `kVA` is a rating. Say so explicitly rather than presenting a consistent machine.
5. **Only two families exist** and `PF` has no `Ordering_Last` flag: `kW, PF` and `kW, kvar`. Reach the second by writing `kvar` after `kW`. `kvar` is `NoDefault` and `RequiredInSpecSet` (L633-L634).
6. **`TotalPowers()` is negative for a generator.** A 1000 kW, PF 0.95 machine at a load bus returns `[(-1000-328.684j)]` kVA: injection is the negative of the load convention. Every example and the workflow must state this, and must not cast the complex result with `float()`.
7. **Property readbacks are scheduled values; only terminal powers show the solved ones.** With `Model=3`, `Vpu=1.03`, and `Maxkvar`/`Minkvar` at ±3000, the terminal power was `(−800 − j3000)` — clamped at `Minkvar` — while `kvar` read 431.8 and `PF` read 0.88, both derived from `kW` and `PFNominal`. Treat `kvar`/`PF`/`kVA` as setpoints and `TotalPowers()` as the result.
8. **`Vpu` is a target that kvar limits clamp.** On a 3 MW-loaded feeder section, default limits (±120 kvar) produced 0.9969 pu for both `Vpu` 1.0 and 1.03; with ±3000 kvar the 1.03 case reached 1.0012 pu with Q pinned at −3000. Report the achieved voltage and the limiting element, never the requested `Vpu` as an outcome.
9. **Model coverage differs.** `Model` 1, 2, 4, and 5 solve on a plain feeder. `Model` 3 needs a real bus and adequate kvar limits to show voltage support. `Model` 7 (approximate inverter) solves but its control behavior needs the inverter settings that PVSystem/InvControl provide. **`Model` 6 raises `#570 Generator User Model <name> Not Loaded`** unless a compiled DLL is present — a construction-time error, so mark it `not-run` rather than pretending.
10. **The wrapper's enum member names are not the display names.** `GeneratorModel.Usermodel` and `GeneratorModel.Approximateinvertermodel` use lower-case `m` and `i`, while the engine's display strings are `User model` and `Approximate inverter model` (enums.py L286-L294, generator.pas L457-L465). A coder who writes `GeneratorModel.UserModel` gets `AttributeError`.
11. **`DispMode` validates at the wrapper.** `DispMode=3` raises `ValueError: 3 is not a valid GeneratorDispatchMode`; use the enum or 0/1/2.
12. **`Refuel` is an action method, not a property** (wrapper L771; engine `BooleanActionProperty` L645-L647). Calling it on a fresh generator left `FuelkWh` unchanged at 100.
13. **`Like` is read-only on the object.** `Generator.new("cp", Like="base")` raises `AttributeError: 'Generator' object attribute 'Like' is read-only`, while `New Generator.cp Like=base` works: it copies `kW`, `kV`, and `Conn` but keeps its own `Bus1` (`cp_1`), and it reported **four conductors although the copied `Conn` is delta** — the terminal count is not recomputed by the copy.
14. **Conductors follow the connection; terminals never do.** Wye three-phase 4, delta three-phase 3, one-phase 2, always one terminal.
15. **`kV` is `Required` with `NonNegative`** (L630-L631): `kV = 0` is accepted, `kV = -12.47` raises `#2020032 cannot be negative`, and `Phases = 0` raises `#2020031 cannot be zero`. `Bus1` is `Required` (L554-L556).
16. **Negative `kW` is allowed and means consumption.** `kW = -500, PF = 0.9` solved and returned `(+500 + j242.16)` at the terminals with `kVA` −600; the rating keeps the sign.
17. **`DynamicEq` must name an existing object.** `DynamicEq="nonexistent"` raises `#401 DynamicExp object "nonexistent" not found`. `DynOut` is a list.
18. **Shapes do not fill each other.** Assigning `Daily` left `Yearly` and `Duty` at None — the Generator has **no** Daily→Yearly fill, unlike `Load` (Load.pas L636-L637). `UseActual` shapes call `SetkWkvar` (side effects L781-L790).
19. **Percent and hour units:** `pctFuel` and `pctReserve` read back as percentages (50 and 25 when written), `FuelkWh` in kWh, `DutyStart` carries `Units_hour` (L613-L614).
20. **Registers are a Generator feature.** The engine declares `kWh`, `kvarh`, `Max kW`, `Max kVA`, `Hours`, and `$` registers (L467-L475) and the wrapper mixes in `ElementHasRegistersMixin`. Document the readback path if you can exercise it; if not, cite the source and mark it `not-run`.
21. **Dispatch properties cannot be demonstrated in a snapshot solve.** `DispMode`, `DispValue`, `Status`, `ForceOn`, and `PVFactor` act through `GenDispatcher` and the dispatch loop; a single `Solve` showed no observable effect from `Status=Fixed` or `ForceOn=True`. Describe them from source, and mark any runtime cell `not-run` unless you build a real dispatch or isolation scenario.

## Required approach

- Every row carries `source_refs` citing the pinned wrapper TypedDict or the engine property block; inherited rows cite `PCElement.pas`/`CktElement.pas`; the enum rows cite `enums.py` and the `TDSSEnum.Create` block.
- Keep `data_type` consistent with the observed readback and record `enum_type` and `reference_class` where they apply, matching the package-4 convention.
- Catalog `MVA` with `supported_in_target: false` for the Python target and explain the text-only path; the schema's fault is documented in the package-4 architect audit (O-1) — declare any extension field you need, and do not invent new row fields that the schema neither declares nor explains in the audit.
- Do not state a default you cannot defend. Where the constructor literal and the readback differ (`kVA` 1200 as a rating, `kvar` 60 versus PF 0.88), state both and say which one a user sees.
- Distinguish the two families from the rating properties in `property_requirements.conditionals`, and state that `DispMode`/`Status`/`ForceOn` are control inputs whose effects require `GenDispatcher`.
- Record the `GenDispatcher` and user-model deferrals as scope notes with citations.
- Do not modify prior catalogs, packages 1–5, or existing audits and QA reports. Additions to `dss_capi.json` and `sources.json` only.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt` and record the environment block.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_generator.py
```

The matrix must cover, at minimum: default readbacks for every catalogued row including the three enums and the empty user-model strings; both families and the `kVA`-as-rating behavior including the dynamic default; the `MVA` text path; connection and conductor counts; the negative-`kW` convention; a solved case reporting per-terminal complex power with the sign stated; a `Model=3` case that reports the achieved voltage against `Vpu` with and without wide kvar limits; the `Model=6` construction error; shape assignment showing no Daily→Yearly fill; the `Like` text path and its stale conductor count; and the fuel/percent readbacks. Label anything not executed as `not-run`, including every dispatch-coupled property.

## Definition of done

1. Schema pair registered and passing (15/15 or more).
2. Catalog validates; every row has source refs; one element class; `MVA` marked unsupported in the Python target with the reason.
3. Engine records cite `0.14.5` ranges; `tested` reflects what actually ran.
4. Workflow documents ratings versus specifications, the sign convention, model selection, `Vpu` clamping, dispatch coupling, shapes, and fuel.
5. Examples pass through the harness and are recorded `Observed-working` with the environment.
6. Readback matrix committed with the environment block and date.
7. Audit records method, counts, checks, limitations, and the `GenDispatcher` scope note.
8. QA handoff prepared and pinned to the package commit.
9. Manifest, plan, READMEs, and skill updated to the real validation level, with package 6 closing the §5.3 element sequence.

## Out of scope

`GenDispatcher` and other controller catalogs, `PVSystem`, `Storage`, `InvControl`, compiled user-model or shaft-model DLLs, dynamics and harmonic simulations beyond the catalogued properties, fuel-consumption studies, `Reactor`, `Fault`, Phase 4 fixtures, `opendss_objects` roll-up, `python_interface_comparison`, and `troubleshooting` seeding.

## Commit and review

- Commit package 6 on `wp/phase3` with a message naming the package; keep unrelated edits out and do not mix it with package 5.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings. With this package the §5.3 element sequence is complete, so the next planning question is the Phase 4 fixture set rather than another element.
