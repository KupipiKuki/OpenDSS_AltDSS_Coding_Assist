# Coder Handoff: Phase 3B Package 3 — Transformer and XfmrCode

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3` (or a task branch from it). Packages 1 and 2 are reviewed; do not reopen them. Commit package 3 on `wp/phase3`, push, and hand it to independent QA/QC before the owner considers it complete.

## Goal

Deliver Phase 3B package 3 — the **Transformer** element and its shared **XfmrCode** definition — with the same six-artifact pattern used for Line/LineCode and packages 1 and 2. `Transformer` is the first package with a per-winding record model and a terminal count that follows a property, so the catalog has to separate per-winding, array, and text-only access cleanly.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Scope decision

1. **`Transformer` and `XfmrCode` are in scope together.** They are the same relationship as Line and LineCode: `XfmrCode` holds the impedance and thermal definition, and `Transformer.XfmrCode` assigns it. Covering one without the other leaves the primary reuse path undocumented.
2. **`AutoTrans` is out of scope.** It is a separate DSS class and a separate `altdss` collection with its own property set. Record it as deferred in the audit; adding it needs an owner scope decision.
3. **Two- and three-winding models only.** `Windings` is documented and supported for 2 and 3. See the hazards below before touching any other value.

## What the pinned surface actually looks like

Verified on the pinned stack; re-confirm each point with a citation and a readback.

- **Per-winding data is a struct array, not flat properties.** The engine declares `TWinding` as a record and `WindingArray = array[1..3]`, registers `PropertyStructArrayOffset`, `PropertyStructArrayStep`, `PropertyStructArrayIndexOffset`, and `PropertyStructArrayCountOffset` (`Transformer.pas` L371-L460), and exposes the per-winding scalars (`Wdg`, `Bus`, `Conn`, `kV`, `kVA`, `Tap`, `pctR`, `RNeut`, `XNeut`) through a `wdg` selector.
- **The Python wrapper exposes arrays and no per-winding scalars.** `TransformerProperties` has 50 keys and contains `Buses`, `Conns`, `kVs`, `kVAs`, `Taps`, `pctR`, `RNeut`, `XNeut`, `XSCArray`; it has no `bus`, `conn`, `kv`, `kva`, `tap`, `wdg`, or `%r`. Confirmed on 0.2.4: those attributes do not exist on the object.
- **The text interface keeps the per-winding path.** `Edit Transformer.t1 wdg=2 bus=secondary` and `Edit Transformer.t1 wdg=1 tap=1.2` work, and `? Transformer.t1.tap`, `? ....bus`, and `? ....wdg` return the active winding's values.
- **Three engine properties become Python methods.** `WdgCurrents` is a read-only string property in the engine (`Transformer.pas` L399-L401) but the wrapper exposes `WindingCurrents()`, `WindingVoltages(winding)`, and `LossesByType()` from `TransformerExtras.py` L6-L28. They are not properties and must not be cataloged as such.
- **Percent-versus-per-unit scaling differs by property.** `pctR` and `pctRs` carry `PropertyScale 0.01` (L503-L518); `XHL`/`XHT`/`XLT` are stored as per-unit fractions (0.07, 0.35, 0.30) and read back as percent (7, 35, 30).

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- Package 2 for the current standard: [catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [workflow](../workflows/circuit_vsource.md) · [build audit](../audits/phase3b_circuit_vsource_audit.md) · [QA report](../audits/phase3b_circuit_vsource_qaqc.md) · [architect review](../audits/phase3b_circuit_vsource_architect_audit.md)
- Package 1 for the multi-class catalog pattern: [catalog](../../opendss_altdss_library/references/lines/line_geometry_wires_properties.json) · [workflow](../workflows/line_geometry_wires.md)
- [Line/LineCode package](../audits/line_linecode_schema_audit.md) — the original shared-definition pattern (`XfmrCode` plays the LineCode role here)
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Property catalog | `references/transformers/transformer_properties.json` | Two `element_class` values: `Transformer` and `XfmrCode`. Reuse `schemas/catalogs/element_properties.schema.json`; no new schema expected. Every row needs `source_refs`. |
| 2 | Source index additions | `references/sources.json` | EPRI `Transformer.html`, `XfmrCode.html`, and `AutoTrans.html` (scope note only), the 0.2.4 wrapper modules, the 0.14.5 engine files, and the inherited `CktElement`/`PDElement` files. Additions only. |
| 3 | Engine records | `references/dss_capi.json` | Winding struct-array mapping, `windings` reset semantics, `XSCArray` derivation order, percent scaling, tap write path, `XfmrCode` copy semantics, terminal count from `Phases`, and the `WdgCurrents` mapping. Cite `0.14.5` ranges. |
| 4 | Workflow | `docs/workflows/transformer.md` | Ordering, winding arrays vs text scalars, `XfmrCode` reuse, tap and impedance behavior, and the hazards below. |
| 5 | Examples | `examples/transformer/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; cover a two-winding solve and a three-winding or `XfmrCode`-based case. `source_ids` recorded; `Observed-working` only after a harness run. |
| 6 | Readback tool and matrix | `tools/readback_transformer.py`, `docs/audits/phase3b_transformer_readback.json` | Defaults for every catalogued row plus the behavior probes below, with the environment block and date. |
| 7 | Audit | `docs/audits/phase3b_transformer_audit.md` | Method, coverage counts, checks, limitations, hazards, open items. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_Transformer_QAQC_handoff.md` | Pinned to the package commit; checklist and report format as in the package 2 handoff. |

Register the catalog in `tools/validate_catalogs.py` (`SCHEMA_PAIRS`); expect 12/12 pairs.

## Sources

| Surface | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| Transformer | `https://opendss.epri.com/Transformer.html` (200) | `altdss/Transformer.py`, `altdss/TransformerExtras.py` | `src/PDElements/Transformer.pas` |
| XfmrCode | `https://opendss.epri.com/XfmrCode.html` (200) | `altdss/XfmrCode.py` | `src/General/XfmrCode.pas` |
| Inherited element data | — | TypedDicts | `src/Common/CktElement.pas`, `src/PDElements/PDElement.pas`, `src/PDElements/PDClass.pas` |

Line pins for this package: `TTransfProp` enum `Transformer.pas` L88-L149 (49 properties), `DefineProperties` L371-L599, spec sets L379-L388, struct-array mapping L392-L396, `WdgCurrents` L399-L401, percent scales L503-L518, `PropertySideEffects` L618-L757, constructor L822-L893, `SetNumWindings` L896-L903, `RecalcElementData` L919+, `TWinding.Init` L1361-L1386, `Set_PresentTap` L1391-L1421. `TXfmrCodeProp` enum `XfmrCode.pas` L68-L114 (39 properties), spec sets L214-L220, constructor L532-L566. Wrapper: `Transformer` class L17, `TransformerProperties` L889-L940, `new` L1832; `XfmrCode` class L12, `XfmrCodeProperties` L605-L641, `new` L1262.

## Established facts to reuse and re-verify

Reproduce each in your own environment and record it; do not copy these numbers without a run.

**Defaults, `Transformer.new("t1")` with no arguments:** `Phases` 3, `Windings` 2, `pctR` [0.2, 0.2], `RNeut` [-1.0, -1.0] (open neutral), `XNeut` [0.0, 0.0], `Buses` generated as `t1_1`, `t1_2`, `Conns` wye/wye, `kVs` [12.47, 12.47], `kVAs` [1000, 1000], `Taps` [1.0, 1.0], `XHL` 7.0, `XHT` 35.0, `XLT` 30.0, `X12`/`X13`/`X23` mirroring them, `XSCArray` [7.0], `Thermal` 2.0, `n` 0.8, `m` 0.8, `FLRise` 65.0, `HSRise` 15.0, `pctLoadLoss` 0.4, `pctNoLoadLoss` 0.0, `NormHkVA` 1100.0, `EmergHkVA` 1500.0, `Sub` False, `SubName` empty, `MaxTap` [1.1, 1.1], `MinTap` [0.9, 0.9], `NumTaps` [32, 32], `pctIMag` 0.0, `ppm_Antifloat` 1.0, `pctRs` [0.2, 0.2], `Bank` empty, `XfmrCode` None, `XRConst` False, `LeadLag` 0, `Core` 0, `RDCOhms` [0.088117, 0.088117], `Seasons` 1, `Ratings` [1100.0], `NormAmps` 50.93, `EmergAmps` 69.45, `FaultRate` 0.007, `pctPerm` 0.0, `Repair` 0.0, `BaseFreq` 60.0, `Enabled` True. The engine constructor (`Transformer.pas` L822-L893) and `TWinding.Init` (L1361-L1386: kVLL 12.47, kVA 1000, puTap 1.0, Rpu 0.002, Rneut −1, TapIncrement 0.00625, NumTaps 32, MaxTap 1.10, MinTap 0.90) are the sources for the paired defaults.

**`XfmrCode` defaults** follow the same winding record, but `Ratings[0]` starts at **600**, not 1100 (`XfmrCode.pas` L564-L566). `XfmrCodeProperties` has 35 keys: no `Buses`, `Sub`, `SubName`, `Bank`, `XfmrCode`, `XRConst`, `LeadLag`, `Core`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, or `Enabled`.

**Enums:** `Connection` wye = 0, delta = 1 (default wye). `CoreType` shell = 0, one_phase = 1, three_leg = 3, four_leg = 4, five_leg = 5, core_1_phase = 9. `PhaseSequence` Lag = 0, Lead = 1.

**Specification sets.** `Transformer` declares three sets (`Transformer.pas` L379-L388): `XfmrCode` (always applied first); `X12, X13, X23, kV`; `XscArray, kV`. `XfmrCode` declares two (`XfmrCode.pas` L214-L220): `X12, X13, X23`; `XscArray`. Put these in `property_requirements.conditionals`; keep the object identifier and model inputs separate, as in the Line and Vsource catalogs.

**Behavior that must be documented and probed:**

1. **Changing `Windings` resets every winding record.** `PropertySideEffects` re-initializes each winding through `TWinding.Init`, regenerates terminals (`Nterms := NumWindings`), and reallocates `XSC`, `TermRef`, and the Y matrices (L630-L665). Setting `Windings` after `Buses`/`kVs` discards them — verified: `Windings = 3` replaced `['a','b']` with `['a','b','t2_3']` and reset kV/kVA/conn/tap to defaults. The catalog description must state the ordering rule.
2. **`Windings = 1` is ignored, not applied.** The flag is `GreaterThanOne` (L449), so a write of 1 leaves `Windings` at 2 and no error is raised.
3. **`Windings` above 3 is unvalidated and unsafe.** A write of 4 is accepted by the setter and reports four windings, but the model is outside the engine's design. Writing `Windings = 1` (which is ignored) and then `Windings = 4` in the same session crashed the process with a **segmentation fault (exit 139)**, reproduced twice on Windows 11 / Python 3.14.6 / backend 0.14.5, while the same 4-write alone merely reported four windings before any further use. Do not put this in the automated harness; record it in the workflow and audit as an observed hazard with the exact sequence, and keep the catalog scoped to 2 and 3.
4. **Array writes are length-checked; scalar text writes are not.** `Buses=[four names]` on a two-winding object fails with `DSSException (#20200424) … Invalid number of elements. Expected 2 elements, got 4.` Bus names are stored lowercased.
5. **Taps are not range-clamped on the property path.** `Taps = [1.5, 1.0]` and `Edit Transformer.t1 wdg=1 tap=1.5` both store 1.5 even though `MaxTap`/`MinTap` are 1.1/0.9. `Set_PresentTap` clamps (L1391-L1421) but the property and text writes do not route through it; `MaxTap`/`MinTap`/`NumTaps` belong to tap-changing controls. Say this plainly instead of implying the engine validates taps.
6. **`pctLoadLoss` rewrites the winding resistances.** Writing 1.0 moved `pctR` from [0.2, 0.2] to [0.5, 0.5], because the side effect splits the loss across windings 1 and 2 (`Transformer.pas` L695-L700). Writing `pctR` recomputes `pctLoadLoss` from `Rpu` sums (L688-L689).
7. **`XSCArray` is derived, not stored input.** A two-winding object reads [7.0]; three windings read [7.0, 30.0, 30.0] from `XHL`/`XHT`/`XLT`. Writing `XHL`, `XHT`, `XLT`, `X12`, `X13`, or `X23` clears the `XscArray` and `XfmrCode` property-tracking entries and sets `XHLChanged` (L700-L712).
8. **`XfmrCode` copies at assignment.** Creating a code with `kVs` [12.47, 4.16] and a transformer with `XfmrCode=code` reproduced the code's `kVs`, `kVAs`, `pctR`, and `XHL`; editing the code afterwards did not change the transformer.
9. **`WdgCurrents`, `WindingVoltages`, and `LossesByType` are methods.** Before a solve, `WindingCurrents()` returns zeros rather than raising (12 complex values for a two-winding, three-phase object). After a solve with a 100 kW load at 4.16 kV, `LossesByType()` returned total and load losses of 89.15 + j669.42 VA and no-load losses of 0 + j0 VA, and `WindingVoltages(1)` returned the winding-1 complex voltages. Record the ordering and 1-based winding index.
10. **`Phases` drives the conductor count.** `PropertySideEffects` sets `NConds := FNphases + 1`, so the neutral terminal exists for every winding; a `Phases` change redefines conductors and reallocates matrices (L622-L625).
11. **`RDCOhms` is derived from `Rpu`.** Default 0.088117 Ω per winding comes from `0.85 × Rpu × Zbase`; an explicit `RDCOhms` write sets `RdcSpecified` and stops the derivation. Probe both states.
12. **`NormHkVA` and `EmergHkVA` follow winding 1.** Defaults are 1.1× and 1.5× the winding-1 kVA and update on `kVA`/`kVAs` writes (L648-L694).

## Required approach

- Every row carries `source_refs` citing the pinned wrapper TypedDict or the engine property block. Rows for inherited fields cite `CktElement.pas`/`PDElement.pas`.
- Represent the winding model honestly: array rows for Python access, and the per-winding scalars (`wdg`, `bus`, `conn`, `kv`, `kva`, `tap`, `%r`, `rneut`, `xneut`) as DSS-text rows with no `altdss_keyword`, each stating that the pinned wrapper has no scalar member. Do not invent Python keywords for them.
- Keep `data_type` consistent with the observed readback, as in packages 1 and 2. `Conns` reads back as `Connection` members, `XSCArray`/`Buses`/`kVAs` as arrays, `XHL` and friends as percent reals.
- Do not state a default you cannot defend. Where the constructor literal and the readback differ (percent scaling, derived ohms, generated bus names), state both and say which one a user sees.
- Mark what the pinned target cannot reach with `supported_in_target: false` only when nothing works; when the text interface reaches a property, keep it supported and give the access path.
- Do not modify prior catalogs, packages 1 and 2, or existing audits and QA reports. Additions to `dss_capi.json` and `sources.json` only.
- Record `AutoTrans` as out of scope in the audit, with the owner-decision note.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt` and record the environment block.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_transformer.py
```

The matrix must cover, at minimum: default readbacks for every `Transformer` and `XfmrCode` row; a two-winding solve with a load and the three result methods; a three-winding construction with the `XSCArray` derivation; the `Windings` reset probe; the `Windings = 1` no-op; array-length validation; the tap non-clamping probe; `pctLoadLoss` ↔ `pctR`; `XfmrCode` copy semantics; and the text-interface scalar path with `wdg` queries. Keep the four-winding hazard out of the harness and record it separately.

## Definition of done

1. Schema pair registered and passing (12/12 or more).
2. Catalog validates; every row has source refs; both element classes present; text-only rows have no Python keyword.
3. Engine records cite `0.14.5` ranges; `tested` reflects what actually ran.
4. Workflow documents ordering, percent scaling, taps, the code-copy path, the methods, and the hazards.
5. Examples pass through the harness and are recorded `Observed-working` with the environment.
6. Readback matrix committed with the environment block and date.
7. Audit records method, counts, checks, limitations, hazards, and the `AutoTrans` scope note.
8. QA handoff prepared and pinned to the package commit.
9. Manifest, plan, READMEs, and skill updated to the real validation level.

## Out of scope

`AutoTrans`, regulators and controls that drive taps, `Load`, `Capacitor`, `Generator`, harmonic and thermal-transient studies, the Phase 4 fixture harness, `opendss_objects` roll-up, `python_interface_comparison`, and `troubleshooting` seeding.

## Commit and review

- Commit the package on `wp/phase3` with a message naming the package; keep unrelated edits out.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings; do not start package 4 (`Load`) until the owner accepts this one.
