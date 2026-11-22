# Phase 4 Package 4.2 — RegControl Catalog (coder handoff)

**Issued** 2026-11-21 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** Phase 4.1 accepted (fixture goldens carry the regulator taps this catalog describes) · owner decision 14 (RegControl catalogued in Phase 4, not deferred).

## Goal

Catalogue `RegControl` with the same six-artifact template the Phase 3 element packages used, so that the regulator behaviour already recorded in both fixture goldens has a property-level reference behind it. Everything in this handoff was verified on the pinned stack on 2026-11-21; where a claim below says "probed", it was measured, not inferred.

## Pinned surface

| Item | Value |
|---|---|
| Engine class | `src/Controls/RegControl.pas` at DSS C-API `0.14.5` |
| Wrapper class | `altdss/RegControl.py` at AltDSS-Python `0.2.4`, `RegControl(DSSObj, CircuitElementMixin)`, `_cls_idx = 21` |
| Engine property enum | `TRegControlProp` — `INVALID` + **32** members (`Transformer` … `Cogen`) |
| Wrapper key set | `RegControlProperties` — **35** keys = the 32 own + `BaseFreq`, `Enabled`, `Like` |
| Collection | `ctx.RegControl`, element class string `RegControl` |
| EPRI pages | [RegControl element](https://opendss.epri.com/RegControl.html) (200) and [Properties23](https://opendss.epri.com/Properties23.html) (200, 8 RegControl mentions). `RegControl1.html` and `Regulators.html` are 404 — do not cite them |

The wrapper mixes in `CircuitElementMixin`, so accessors such as `TotalPowers()` exist and return zeros. The class is a control, not plant: both fixture goldens record it under `elements` with zero powers and separately under `controls` with its tap.

## Verified defaults (constructor, `RegControl.pas` L492-L549)

| Property | Default | Unit flag | Notes |
|---|---|---|---|
| `Transformer` | unset | — | `Required`; a `DSSObjectReferenceProperty` to a proxy accepting `Transformer` or `AutoTrans` |
| `Winding` | 1 | — | maps to `ElementTerminal`; must be ≤ the transformer's terminal count |
| `VReg` | 120.0 | `Units_V` | **attribute is `VReg`, not `Vreg`** |
| `Band` | 3.0 | — | volts, total band width |
| `PTRatio` | 60.0 | — | writing it re-initialises `RemotePTRatio` |
| `RemotePTRatio` | = `PTRatio` | — | `DynamicDefault` |
| `CTPrim` | 300.0 | `Units_A` | |
| `R`, `X` | 0.0 | — | line-drop compensator |
| `Delay` | 15.0 | `Units_s` | |
| `TapDelay` | 2.0 | `Units_s` | |
| `MaxTapChange` | 16 | — | tap steps allowed per control iteration |
| `PTPhase` | 1 | — | **a `VBuffer` index, not a phase label** |
| `TapWinding` | = `Winding` | — | `DynamicDefault` |
| `Reversible` | FALSE | — | |
| `RevVReg` | 120.0 | — | **attribute is `RevVReg`, not `RevVreg`** |
| `RevBand` | 3.0 | — | |
| `RevR`, `RevX` | 0.0 | — | |
| `RevDelay` | 60.0 | `Units_s` | |
| `RevThreshold` | 100.0 | `Units_kW` | |
| `RevNeutral` | FALSE | — | |
| `VLimit` | 0.0 | `Units_V` | |
| `LDC_Z`, `Rev_Z` | 0.0 | — | |
| `Cogen`, `InverseTime`, `EventLog`, `DebugTrace` | FALSE | — | |
| `Bus` | `''` | — | optional remote regulated bus; setting it forces one phase and two conductors |
| `TapNum` | tapped winding's tap | — | read and write by function |

`Reset` is a `BooleanActionProperty` — an action, not a state. `Enabled` and `BaseFreq` are inherited.

## Traps, all probed on the pinned stack

1. **`VReg` and `RevVReg` casing.** `reg.Vreg` and `Vreg=120` both raise `AttributeError: 'RegControl' object has no attribute 'Vreg'`. The same applies to `RevVreg`. Read the key set from the wrapper, not from the DSS manual's capitalisation.
2. **A manual tap write is undone by the next controlled solve.** On the fixture: read `TapNum` 9, write 5, read 5, `Solve()` → back to **9** with 12 total iterations. Use `Set ControlMode=Off` or `Solution.SolveNoControl()`; both kept the written 5. Any example that demonstrates a tap must state which of the three paths it uses.
3. **`TapNum` is clamped by the transformer, not by `RegControl`.** For the fixture's 32-tap windings (`MinTap` 0.9, `MaxTap` 1.1) writing 99 reads back **16** and −99 reads back **−16**. Catalogue `TapNum` as an integer step count bounded by the tapped winding.
4. **`TapNum` moves the `TapWinding`, which may not be the monitored `Winding`.** With `Winding` 2 and `TapWinding` 1, `TapNum = 4` moved winding 1's tap to 1.025 while winding 2 stayed at 1.05625. Both are dynamic defaults from the same source, so they agree until one is set.
5. **Too small a `MaxTapChange` fails the solve.** From tap 0 with `MaxTapChange = 1`, `Solve()` raised `(#485) Warning Max Control Iterations Exceeded`; with the default 16 the same start converged to tap 9 in 12 iterations. Do not "fix" a control problem by lowering this without recording the resulting error.
6. **Missing, unknown, and wrong-class targets all give `#124`.** `RegControl.new("x", VReg=120)` with no transformer, `Transformer="nosucht"`, and `Transformer="l1"` pointed at a Line each raised `(#124)`. The source also defines `#123` "Controlled Regulator Element is not a transformer", but I could not reach it through the Python keyword path or through `New RegControl ... transformer=l1` in text; record `#123` as source-only and do not claim a reproduction.
7. **A bare `new()` is accepted and fails later.** `ctx.RegControl.new("bare")` with no keywords constructs, then the first `Solve()` raises `(#482) Error Encountered in Solve: Solution aborted`, which wraps the underlying `#124`. Catalogue creation as needing `Transformer` even though the wrapper does not enforce it at the call.
8. **`Winding` beyond the transformer's terminals raises `#122`** — "Winding no. 5 does not exist" for a two-winding transformer.
9. **Writing `PTRatio` overwrites `RemotePTRatio`.** Explicit `RemotePTRatio = 10` followed by `PTRatio = 50` read back 50 for both. Set `PTRatio` first and `RemotePTRatio` last when the two must differ.
10. **`PTPhase` is a `VBuffer` index.** Source uses `VBuffer[FPTPhase]` and switches on it; the wrapper enum `RegControlPhaseSelection` exposes only `min = -3` and `max = -2`, while the default is `1` and reads back as a plain `int`. Do not present it as a phase number, and do not assume the enum covers the default.
11. **`Bus` changes the control completely.** Default `''` regulates the controlled winding's own bus. Setting `Bus = "634"` on the fixture held tap 16 after the solve. When `Bus` is set the object uses one phase and two conductors.
12. **`Enabled = False` stops the control.** With `Enabled` false, setting `VReg = 100` and solving left the tap at 9.
13. **`Like` and `Reset` are methods; the keywords raise.** `RegControl.new(..., Like="reg1")` and `... Reset=True` both raise `AttributeError: 'RegControl' object attribute ... is read-only`. `reg.Like("reg1")` returns `None` and copies the source's settings (probed: `VReg` 110 → 122, `Band` 3 → 2); `reg.Reset()` returns `None` and did not move the tap in the probe. DSS text `Like=reg1` works. **This is the third package where this trap shape appeared — do not repeat "read-only on the object" in the catalog.**
14. **`RegControl` appears in `ctx.Element` with zero powers.** The fixture goldens count it in `NumCircuitElements` (38 and 117). The catalog and workflow must say that a RegControl is a control, and that its `TotalPowers()` is meaningless rather than zero-by-coincidence.

## Deliverables

| # | Artifact | Notes |
|---|---|---|
| 1 | `references/regcontrols/regcontrol_properties.json` | One record, `element_class: RegControl`, 35 rows = 32 engine members + `BaseFreq`, `Enabled`, `Like`. `required_properties` = `name`, `transformer` |
| 2 | `schemas/catalogs/element_properties.schema.json` | **No change expected.** The row schema now declares every field the Phase 3 and 4.1 packages needed; if you need a new row field, declare it in the same commit and say why. Do add the pairing — `tools/validate_catalogs.py` `SCHEMA_PAIRS` currently has 16 entries, so this package must add `"references/regcontrols/regcontrol_properties.json": "schemas/catalogs/element_properties.schema.json"` for the run to report 17 |
| 3 | `docs/workflows/regcontrol.md` | Cover the wiring order, the three tap paths (controlled solve, `ControlMode=Off`, `SolveNoControl`), tap clamping, `PTRatio`/`RemotePTRatio` ordering, `PTPhase`, `Bus`, and the `#122`/`#124`/`#482`/`#485` guard set |
| 4 | Two examples | One Python and one DSS. Use a self-contained two-winding transformer plus a load, not the fixture, so the example does not depend on fixture provenance. Assert a tap readback **and** a regulated-voltage readback, and state which control path produced each |
| 5 | `tools/readback_regcontrol.py` + committed matrix | Sections: defaults (every row), tap paths, tap clamping, `TapWinding` divergence, `MaxTapChange` failure, `PTRatio`/`RemotePTRatio` ordering, `PTPhase`, `Bus`, `Enabled`, actions, guards |
| 6 | `docs/audits/phase4_regcontrol_audit.md` | Build audit with the environment block and the exact commands |
| 7 | `references/sources.json`, `dss_capi.json`, `examples.json` | Additive only. Cite `0.14.5` for the engine and `0.2.4` for the wrapper; EPRI `RegControl.html` and `Properties23.html` are the only valid EPRI pages |

## Acceptance

1. `tools/validate_catalogs.py` passes with the new schema pair on the extended total (17 pairs expected).
2. `tools/run_examples.py` passes with the two new examples recorded `Observed-working` and their environment block.
3. `tools/readback_regcontrol.py` runs clean and its committed matrix reproduces exactly.
4. Every catalog row carries pinned, in-bounds `source_refs`; no mutable refs, no range past end of file.
5. The traps that fail (`#122`, `#124`, `#482`, `#485`) are recorded with the exact messages observed, and `#123` is marked source-only.
6. The tap-path distinction is explicit wherever a tap is written, in the catalog description, the workflow, and both examples.
7. No Phase 3 or Phase 4.1 catalog, golden, or fixture file changes; `git diff` stays inside `docs/`, `references/`, `examples/`, `schemas/`, and `tools/`.
8. The build audit states the pinned environment and the validation date, and the plan/manifest reconciliation is deferred to package 4.5.

## Out of scope

CapControl, GenDispatcher, PVSystem/InvControl, LoadShape, GrowthShape, Storage, and AutoTrans remain uncatalogued; the daily time series is 4.3; the cross-interface tool is 4.4; the exit pass is 4.5. Do not catalogue `Transformer` again — it already exists from Phase 3B package 3.
