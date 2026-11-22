# Coder Handoff: Phase 3B Package 4 — Load

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3` (or a task branch from it). Packages 1–3 are reviewed and accepted; do not reopen them. Commit package 4 on `wp/phase3`, push, and hand it to independent QA/QC before the owner considers it complete.

## Goal

Deliver Phase 3B package 4 — the **Load** element — with the same six-artifact pattern used for Lines, Circuit/Vsource, and Transformer. `Load` is the first package where the user can specify the same physical quantity in five different ways, so the catalog has to describe the load-specification families and their precedence precisely; that is the core of this package.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Scope decision

1. **`Load` is in scope; `LoadShape` and `GrowthShape` are not.** They are separate DSS classes with their own collections and property sets, and they are shared by many elements. Package 4 covers the `Load` rows plus the *assignment* behavior of `Daily`, `Yearly`, `Duty`, `Growth`, and `CVRCurve`. Do not catalog LoadShape or GrowthShape properties; if an example needs a shape, define a minimal one inline and note in the audit that its catalog is future scope.
2. **One element class in the catalog.** `references/loads/load_properties.json` with `element_class: Load` only.
3. **The five load-specification families are the package's centerpiece.** Treat them as the engine's declaration of alternative complete inputs, not as free-form knobs.

## What the pinned surface actually looks like

Verified on the pinned stack; re-confirm each point with a citation and a readback.

- **`LoadProperties` has 42 keys**, and the engine `TLoadProp` has 38 members (`Load.pas` L111-L150). The four extras are inherited or action keys: `Spectrum`, `BaseFreq`, `Enabled`, `Like`. There is no separate per-phase or per-terminal accessor: a load is one terminal with `NConds` conductors.
- **`kV` drives the voltage base, not the power.** The `conn` and `phases` side effects recompute `VBase` (`delta` uses line-to-line, wye uses line-to-neutral for two or three phases) and reset the conductor count (`Load.pas` L519-L575).
- **Percent-scaled fields exist:** `pctMean`, `pctStdDev`, and `pctSeriesRL` carry `PropertyScale 0.01` (L408-L410), so the readbacks are 50.0, 10.0, and 50.0 while the engine stores 0.5, 0.1, and 0.5.
- **`kVA` is derived, not an independent input, in most families.** `RecalcElementData` (L1152-L1190) computes it from `kW`/`kvar`, and the kWh family leaves it at 0.

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- Package 3 for the current standard: [catalog](../../opendss_altdss_library/references/transformers/transformer_properties.json) · [workflow](../workflows/transformer.md) · [build audit](../audits/phase3b_transformer_audit.md) · [QA report](../audits/phase3b_transformer_qaqc.md) · [architect review](../audits/phase3b_transformer_architect_audit.md)
- Package 2 for the element-plus-command pattern: [catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [workflow](../workflows/circuit_vsource.md)
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Property catalog | `references/loads/load_properties.json` | One `element_class`: `Load`. Reuse `schemas/catalogs/element_properties.schema.json`; no new schema expected. Every row needs `source_refs`. |
| 2 | Source index additions | `references/sources.json` | EPRI Load pages (see the URL table), the 0.2.4 wrapper modules, the 0.14.5 engine files, the inherited `CktElement`/`PCElement` files, and a scope note for LoadShape/GrowthShape. Additions only. |
| 3 | Engine records | `references/dss_capi.json` | Load-specification families and precedence, connection/conductor behavior, percentage scales, shape-assignment side effects, ZIPV, default derivation, and required flags. Cite `0.14.5` ranges. |
| 4 | Workflow | `docs/workflows/load.md` | Family selection and precedence, unit rules, connection effects, shape assignment, ZIPV, and the traps below. |
| 5 | Examples | `examples/load/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; cover a two-family comparison and a solve that reads back actual served power or currents. `source_ids` recorded; `Observed-working` only after a harness run. |
| 6 | Readback tool and matrix | `tools/readback_load.py`, `docs/audits/phase3b_load_readback.json` | Defaults for every catalogued row plus the behavior probes below, with the environment block and date. |
| 7 | Audit | `docs/audits/phase3b_load_audit.md` | Method, coverage counts, checks, limitations, hazards, open items, and the LoadShape/GrowthShape scope note. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_Load_QAQC_handoff.md` | Pinned to the package commit; checklist and report format as in the package 3 handoff. |

Register the catalog in `tools/validate_catalogs.py` (`SCHEMA_PAIRS`); expect 13/13 pairs.

## Sources

| Surface | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| Load | `https://opendss.epri.com/Load1.html` (200; element page) | `altdss/Load.py` | `src/PCElements/Load.pas` |
| Load property vocabulary | `https://opendss.epri.com/Properties7.html` (200) | `altdss/Load.py` | `src/PCElements/Load.pas` |
| Inherited element data | — | TypedDict | `src/Common/CktElement.pas`, `src/PCElements/PCElement.pas`, `src/PCElements/PCClass.pas` |
| Shapes (scope note only) | `LoadShape.html`, `GrowthShape.html` (both 200) | `altdss/LoadShape.py`, `altdss/GrowthShape.py` | `src/General/LoadShape.pas`, `src/General/GrowthShape.pas` |

**Correction (2026-11-21):** this handoff first named `Properties17.html` as the Load property vocabulary page. That is wrong — `Properties17.html` returns 200 but is the **Fault** page (11 mentions of `Fault`, none of `Load` or `ZIPV`). The correct page is **`Properties7.html`**, whose raw HTML contains `ZIPV` and `kWhDays` and 13 mentions of `Load`. Both pages were re-checked live on 2026-11-21 after the independent reviewer flagged the mismatch.

**Do not use `https://opendss.epri.com/Load.html`: it returns 404 at check time.** The element page is `Load1.html` and the property page is `Properties7.html`. Record whichever pages you cite with an access date and a scope note; the JS-rendered tables do not expose the field list to a plain GET, so field-level claims rest on the pinned wrapper and engine.

Line pins for this package: `TLoadProp` enum `Load.pas` L111-L150; `DefineProperties` L358-L494; spec sets L368-L385; required flags L405, L448-L457; percent scales L408-L410; `conn`/`phases`/`kV` side effects L519-L575; `kW`/`PF`/`allocationfactor`/`Cfactor` L563-L620; shape side effects L620-L660; `kWh`/`kvar`/`xfkVA`/`kWhDays`/`kVA`/`ZIPV` L660-L731; constructor L801-L893; `RecalcElementData` L1152-L1190. Wrapper: `Load` class L18, `LoadProperties` L848-L889, `new` L1689.

## Established facts to reuse and re-verify

Reproduce each in your environment and record it; do not copy these numbers without a run. Unless a trap says otherwise, these were reproduced through `Load.new(name, **kwargs)` and through `New Load...` text commands, which agree with each other. **Attribute assignment is not equivalent — see trap 15.**

**Defaults, `Load.new("l1")` with no arguments:** `Phases` 3, `Bus1` generated as `l1_1`, `kV` 12.47, `kW` 10.0, `PF` 0.88, `kvar` **5.3974** (derived from kW and PF, not the engine's `kvarBase` of 5.0), `kVA` 11.3636, `Model` 1, `Conn` 0 (wye), `RNeut` −1.0 (open), `XNeut` 0.0, `Status` 0, `Class` 1, `VMinpu` 0.95, `VMaxpu` 1.05, `VMinNorm` 0.0, `VMinEmerg` 0.0, `XfkVA` 0.0, `AllocationFactor` 0.5, `pctMean` 50.0, `pctStdDev` 10.0, `CVRWatts` 1.0, `CVRVars` 2.0, `kWh` 0.0, `kWhDays` 30.0, `CFactor` 4.0, `CVRCurve` None, `NumCust` 1, `ZIPV` [0×7], `pctSeriesRL` 50.0, `RelWeight` 1.0, `VLowpu` 0.5, `puXHarm` 0.0, `XRHarm` 6.0, `Spectrum` `<Spectrum.defaultload>`, `BaseFreq` 60.0, `Enabled` True, four conductors, one terminal. The constructor values behind them are `kWBase` 10, `kvarBase` 5, `PFNominal` 0.88, `kVLoadBase` 12.47, `VminPu` 0.95, `VmaxPu` 1.05, `VLowpu` 0.50, `CVRwattFactor` 1.0, `CVRvarFactor` 2.0, `kWhDays` 30, `FCfactor` 4.0, `puMean` 0.5, `puStdDev` 0.1, `puSeriesRL` 0.50, `XRHarmRatio` 6.0, `LoadClass` 1, `NumCustomers` 1, status Variable, model ConstPQ (L801-L893).

**Enums:** `LoadModel` ConstantPQ 1, ConstantZ 2, Motor 3, CVR 4, ConstantI 5, ConstantP_fixedQ 6, ConstantP_fixedX 7, ZIPV 8. `LoadStatus` Variable 0, Fixed 1, Exempt 2. `Connection` wye 0, delta 1.

**Specification families (engine declaration, `Load.pas` L368-L385):** `kW, PF`; `kW, kvar`; `kVA, PF`; `xfkVA, AllocationFactor, PF`; `kWh, kWhDays, CFactor, PF`. The engine tracks a `LoadSpecType` state and clears the competing property-tracking entries when a family is selected (L563-L731). Note that the display strings in `SpecSetNames` (L368-L374) and the member arrays in `TSpecSets` (L375-L381) use different orders for the kWh family: the name is `kWh, kWhDays, CFactor, PF`, while the set is built as `Create(ord(kWh), ord(PF), ord(kWhdays), ord(Cfactor))`. Record the member order the engine actually builds, and do not present the display string as the storage order.

**Behavior that must be documented and probed:**

1. **The last family write wins, and the readbacks follow it.** `kW=100, PF=0.95` gives kvar 32.8684 and kVA 105.2632; `kW=100, kvar=30` gives PF 0.9578 and kVA 104.4031; `kVA=200, PF=0.9` gives kW 180 and kvar 87.178; `kWh=30000, kWhDays=30, CFactor=4, PF=0.9` gives kW 166.6667 (= 30000/720 × 4) and kvar 80.7204.
2. **`PF` is not authoritative in every family.** On one object built as `Load.new("e", kW=50, PF=0.9)` → kvar 24.2161, kVA 55.5556; then `e.kvar = 20.0` → kvar 20, kVA 53.8516, PF read back 0.9285; then `e.PF = 0.8` changed **nothing** (kvar stayed 20, PF stayed 0.9285, kVA stayed 53.8516); then `e.kVA = 100.0` produced kW 92.8477 and kvar 37.1391 using the *existing* PF 0.9285. The same sequence through `Edit Load... kvar=20` / `PF=0.8` text commands behaves identically. Describe `PF` as the value used when the active family needs it, and warn that a PF write can be a no-op.
3. **Argument order matters for the allocation families.** `Load.new("e", XfkVA=100, AllocationFactor=0.5, PF=0.9)` produced **kW 44.0**, not 45.0, because the allocation ran with the previous PF (0.88) before `PF` was applied. Set `PF` before `XfkVA`/`AllocationFactor` (or issue a second edit). Python kwargs are applied in order; this is not the text-command ordering rule, where `PF` carries `Ordering_Last` (L452).
4. **`kVA` reads 0 in the kWh family** while `kW` and `kvar` are populated. Record the observed value and explain that the derived kVA base is not set on that path (L1183-L1190).
5. **Connection changes the conductor count.** Probes: wye 3φ → 4 conductors, delta 3φ → 3, one phase → 2 in either connection, one terminal in all cases. `kV` and `conn` recompute `VBase` (delta line-to-line, wye line-to-neutral for 2–3 phases).
6. **A `UseActual` load shape rewrites the load's kW and kvar.** Assigning a `Daily` shape whose maximum is 1.5 changed a 10 kW load to kW 1.5, kvar 0.7265, kVA 1.6667.
7. **`Daily` auto-fills `Yearly`.** With only `Daily` assigned, `Yearly` read back the same shape object; assigning only `Yearly` left `Daily` at None.
8. **Shape properties read back as object references** (`<LoadShape.shape1>`, `<GrowthShape.grow1>`), not strings. Size the `data_type` and description accordingly.
9. **`ZIPV` is a fixed-length 7-coefficient array** with `NoDefault`; writing it sets the internal "ZIPV set" flag that pairs with `Model=8`. A fresh load reads seven zeros.
10. **Percent-scaled readbacks:** `pctMean` 50.0, `pctStdDev` 10.0, `pctSeriesRL` 50.0 while the engine stores 0.5, 0.1, 0.5.
11. **`Status` is an enum-backed status, not a boolean**, and `Class` is an integer load class; `NumCust` is a separate customer count. Do not conflate them.
12. **`VMinNorm`/`VMinEmerg` default to 0**, which means the circuit's values apply.
13. **The load uses `Spectrum.defaultload`**, which is a different default object from Vsource's `defaultvsource`.
14. **`kV` and `Bus1` are `Required` in the engine; the power inputs are `RequiredInSpecSet`.** Use the Line/Vsource convention: `required_properties` records identity plus required model inputs, and the conditional entries record the five families.
15. **Attribute writes do not recompute derived fields while an edit context is open.** The effect is an edit-state effect, not an attribute-versus-kwargs effect; three cases were measured:

    - `l = Load.new("a")` (the constructor leaves the edit open), then `l.kW = 50.0; l.PF = 0.9` → kW 50, **kvar 5.3974, kVA 11.3636**, the constructor values. Reverse order behaves the same.
    - `l = Load.new("a"); l.end_edit()`, then `l.kW = 50.0` → kvar 26.9871 at the current PF 0.88; a following `l.PF = 0.9` → kvar 24.2161, kVA 55.5556. Writes after finalization recompute normally.
    - `l = Load.new("a", begin_edit=False)`, then `l.kW = 50.0; l.PF = 0.9` → kvar 5.3974 persists with **no later recovery** on attribute writes.

    A load constructed with completed kwargs (`Load.new("b", kW=12, PF=0.9)`), or one created by a DSS text command, refreshes on individual writes (`b.kW = 50.0` → kvar 24.2161, kVA 55.5556). Tell users to specify a family in one `new(...)` call, one text command, or to `end_edit()` before reading derived values, and never to rely on `begin_edit=False` plus attribute writes. Do not claim a recompute on the open-edit attribute path.

## Required approach

- Every row carries `source_refs` citing the pinned wrapper TypedDict or the engine property block; inherited rows cite `CktElement.pas`/`PCElement.pas`.
- Keep `data_type` consistent with the observed readback. All three enum properties read back as altdss enum members, not raw integers: `Model` → `LoadModel.ConstantPQ`, `Conn` → `Connection.wye`, `Status` → `LoadStatus.Variable` (use `.value` for the engine integer). Cite the wrapper's enum import path for each.
- Do not state a default you cannot defend. Where the constructor literal and the readback differ (`kvar`, `kVA`, `pctSeriesRL`), state both and say which one a user sees.
- Represent the five families in `property_requirements.conditionals` exactly as the engine declares them, including the `PF` member of each, and state that the Python constructor applies arguments in order.
- Do not modify prior catalogs, packages 1–3, or existing audits and QA reports. Additions to `dss_capi.json` and `sources.json` only.
- Record the LoadShape/GrowthShape deferral in the audit and the source index scope notes.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt` and record the environment block.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_load.py
```

The matrix must cover, at minimum: default readbacks for every catalogued row, including the enum member types of `Model`, `Conn`, and `Status`; each of the five families and the derived readbacks; the family-switching probe that shows a `PF` write becoming a no-op; the allocation ordering probe; the `kVA`-reads-zero case; the attribute-versus-kwargs divergence (trap 15) in both paths; connection/phases conductor counts; shape assignment including the `Daily`→`Yearly` fill and the `UseActual` kW/kvar rewrite; the ZIPV probe with `Model=8`; and a solve that reads back served power or currents. Label anything not executed as `not-run`.

## Definition of done

1. Schema pair registered and passing (13/13 or more).
2. Catalog validates; every row has source refs; one element class; enums match the wrapper's readback types.
3. Engine records cite `0.14.5` ranges; `tested` reflects what actually ran.
4. Workflow documents the five families, precedence, ordering, connection effects, shapes, ZIPV, and the traps.
5. Examples pass through the harness and are recorded `Observed-working` with the environment.
6. Readback matrix committed with the environment block and date.
7. Audit records method, counts, checks, limitations, and the shape-class scope note.
8. QA handoff prepared and pinned to the package commit.
9. Manifest, plan, READMEs, and skill updated to the real validation level.

## Out of scope

`LoadShape` and `GrowthShape` property catalogs, `Capacitor`, `Generator`, energy meters, load-allocation commands beyond the documented family math, harmonics and reliability studies, Phase 4 fixtures, `opendss_objects` roll-up, `python_interface_comparison`, and `troubleshooting` seeding.

## Commit and review

- Commit the package on `wp/phase3` with a message naming the package; keep unrelated edits out.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings; do not start package 5 (`Capacitor`) until the owner accepts this one.
