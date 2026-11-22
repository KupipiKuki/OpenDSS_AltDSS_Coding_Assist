# Coder Handoff: Phase 3B Package 5 — Capacitor

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3`. Packages 1–3 are accepted; package 4 (Load) is with the coder and its handoff is `docs/handoffs/Phase_3B_Load_Coder_handoff.md`. **The owner directed this package to be prepared in parallel; do not start coding package 5 until package 4 is accepted unless the owner says otherwise.** Commit package 5 separately from package 4.

## Goal

Deliver Phase 3B package 5 — the **Capacitor** element — with the same six-artifact pattern used for Lines, Circuit/Vsource, Transformer, and Load. Capacitor is the first package whose properties are **arrays over `NumSteps`** and whose **legacy v6 property set no longer exists** in the pinned engine. Both facts drive the catalog design and are the core of this package.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Scope decision

1. **`Capacitor` is in scope; `CapControl` is not.** `CapControl` is a separate controller class with its own class index, collections, and property set (`src/Controls/CapControl.pas`, `altdss/CapControl.py`, at least 68 public attributes). Package 5 covers the `Capacitor` rows plus the **`States`-based control hook** that `CapControl` drives. Record a scope note; do not catalog `CapControl` properties.
2. **One element class in the catalog.** `references/capacitors/capacitor_properties.json` with `element_class: Capacitor` only.
3. **Three capacitance specification families are the centerpiece** (`kvar, kV` · `cmatrix` · `cuf, kV`), and the array-over-`NumSteps` shape of `kvar`, `Cuf`, `R`, `XL`, `Harm`, and `States` is the package's defining difficulty.

## What the pinned surface actually looks like

Verified on the pinned stack; re-confirm each point with a citation and a readback.

- **`CapacitorProperties` has 21 keys** (`Capacitor.py` L378-L399) but the engine class declares only **13 own properties** (`Capacitor.pas` L68-L86). The other eight are inherited: `NormAmps`, `EmergAmps`, `FaultRate`, `pctPerm`, `Repair` from `PDElement`, and `BaseFreq`, `Enabled`, `Like` from the object/class base. **There is no `Spectrum` key** (unlike Load and Vsource).
- **Six properties are arrays, not scalars:** `kvar`, `Cuf`, `R`, `XL`, `Harm` are `Float64Array` and `States` is `Int32Array`, all indexed over `NumSteps` (`Capacitor.pas` L227-L259). `CMatrix` is a symmetric-matrix property scaled by `1e-6` (`Units_uF`, L220-L225).
- **The engine file lives in `src/PDElements/Capacitor.pas`, not `src/PCElements/`.** Line, Load, and Transformer are in `PCElements`; a citation to `src/PCElements/Capacitor.pas` is a 404.
- **The v6-era property set is gone.** `Model`, `Vmin`, `Vmax`, `StepSize`, `Vharmonics`, `State` (singular), `PctLead`, `PctLag`, `PtPhase`, `Userated`, and `Spectrum` all fail on the pinned stack (`#110 Unknown parameter` from text; `AttributeError` on the object). `States` (plural, integer array) replaces `State`.

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- Package 4 for the current standard and the closest precedent: [Load handoff](Phase_3B_Load_Coder_handoff.md)
- Package 3 for citations and audit shape: [catalog](../../opendss_altdss_library/references/transformers/transformer_properties.json) · [workflow](../workflows/transformer.md) · [build audit](../audits/phase3b_transformer_audit.md) · [QA report](../audits/phase3b_transformer_qaqc.md) · [architect review](../audits/phase3b_transformer_architect_audit.md)
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Property catalog | `references/capacitors/capacitor_properties.json` | One `element_class`: `Capacitor`. Reuse `schemas/catalogs/element_properties.schema.json`; no new schema expected. Every row needs `source_refs`. |
| 2 | Source index additions | `references/sources.json` | EPRI Capacitor pages (see the URL table), the 0.2.4 wrapper module, the 0.14.5 engine file, the inherited `PDElement`/`PDClass` files, and a scope note for `CapControl`. Additions only. |
| 3 | Engine records | `references/dss_capi.json` | The 13-member property enum, the three specification families and `SpecType`, array-over-`NumSteps` semantics and length validation, the `CMatrix`/`Cuf` microfarad scales, terminal and conductor side effects, `States` and the control hook, constructor defaults, and the amp-rating derivation. Cite `0.14.5` ranges. |
| 4 | Workflow | `docs/workflows/capacitor.md` | Family selection, array/`NumSteps` ordering, wye/delta/shunt/series wiring, `States` and `CapControl` coupling, ratings, and the traps below. |
| 5 | Examples | `examples/capacitor/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; include a solve that reads back the capacitor's reactive output per terminal, and a multi-step bank driven by `States`. `source_ids` recorded; `Observed-working` only after a harness run. |
| 6 | Readback tool and matrix | `tools/readback_capacitor.py`, `docs/audits/phase3b_capacitor_readback.json` | Defaults for every catalogued row plus the behavior probes below, with the environment block and date. |
| 7 | Audit | `docs/audits/phase3b_capacitor_audit.md` | Method, coverage counts, checks, limitations, hazards, open items, and the `CapControl` scope note. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_Capacitor_QAQC_handoff.md` | Pinned to the package commit; checklist and report format as in the package 3 handoff. |

Register the catalog in `tools/validate_catalogs.py` (`SCHEMA_PAIRS`); expect 14/14 pairs.

## Sources

| Surface | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| Capacitor | `https://opendss.epri.com/Capacitor1.html` (200; element page) | `altdss/Capacitor.py` | `src/PDElements/Capacitor.pas` |
| Capacitor (second page) | `https://opendss.epri.com/Capacitor.html` (200 at check time; also titled "Capacitor" — cite only after reading it, and say what it is) | `altdss/Capacitor.py` | `src/PDElements/Capacitor.pas` |
| Inherited element and class data | — | `PDElementMixin`, TypedDict | `src/PDElements/PDElement.pas`, `src/PDElements/PDClass.pas`, `src/Common/CktElement.pas` |
| Control coupling (scope note only) | — | `altdss/CapControl.py` | `src/Controls/CapControl.pas` |

**Do not cite `Capacitor2.html` (404) and do not guess a `Properties<N>.html` number.** `Properties23.html` and `Properties24.html` both return 200 with no capacitor text in a plain GET because the tables are JS-rendered, so the property-vocabulary page cannot be identified that way. Field-level claims rest on the pinned wrapper and engine; record access dates on whatever pages you do cite.

Line pins for this package: legacy enum `Capacitor.pas` L53-L66; modern enum L68-L86; `DefineProperties` L200-L283; `SpecSetNames` L208-L212; `SpecSets` L213-L217; `CMatrix` L219-L224; `kvar` L226-L230; `R` L232-L234; `XL` L236-L238; `Cuf` L240-L244; `Harm` L246-L248; `States` L250-L253; `Conn` L255-L258; `Bus1` L260-L263; `Bus2` L265-L266; `kV` L268-L270; `Phases` L272-L275; `NumSteps` L277-L279; `PropertySideEffects` L296-L501; `Bus1` side effect L303-L321; `Conn` L322-L341; `Bus2` L342-L350; `Phases` L351-L371; `kvar`/`CMatrix`/`Cuf` spec-type writes L372-L386; `NumSteps` L387-L455; `XL` L459-L468; `Harm` L470-L471; `States` L472-L473; Y-prim invalidation L476-L498; constructor L546-L600; `RecalcElementData` L614-L694. Wrapper: `Capacitor` class L15, `_cls_idx` 22 (L18), `CapacitorProperties` L378-L399, `new` L798, `States` docstring L270-L274.

## Established facts to reuse and re-verify

Reproduce each in your environment and record it; do not copy these numbers without a run. Reproduced through `Capacitor.new(name, **kwargs)` and through `New Capacitor...` text commands unless a trap says otherwise.

**Defaults, `Capacitor.new("c1")` after a 12.47 kV three-phase circuit:** `Bus1` `c1_1`, **`Bus2` `c1_1.0.0.0`** (grounded wye default), `Phases` 3, `kvar` **[1200.0]**, `kV` 12.47, `Conn` `Connection.wye` (0), `CMatrix` **empty array**, `Cuf` **[20.46997067]** (µF, derived), `R` [0.0], `XL` [0.0], `Harm` [0.0], `NumSteps` 1, `States` **[1]**, `NormAmps` **75.00460594**, `EmergAmps` **100.00614125**, `FaultRate` 0.0005, `pctPerm` **100.0**, `Repair` 3.0, `BaseFreq` 60.0, `Enabled` True; `NumTerminals()` 2, `NumConductors()` 3. Constructor constants (L546-L600): `FNPhases` 3, `Nterms` 2, `kvarRating` 1200, `kVrating` 12.47, `NumSteps` 1, `SpecType` 1, `FaultRate` 0.0005, `PctPerm` 100, `HrsToRepair` 3.0.

**Derived ratings:** per-phase rated current is 55.556 A at 1200 kvar / 12.47 kV three-phase, and `NormAmps` = 1.35 × that, `EmergAmps` = 1.8 × that (L684-L694). The wrapper docstring says NormAmps "defaults to 180%" — the engine uses **135%**; report the engine value and flag the docstring.

**Families and state:** `SpecSetNames` = `kvar, kV` · `cmatrix` · `cuf, kV`; the side effects set `SpecType` 1 / 3 / 2 respectively (L372-L385), so **the last capacitance write selects the family**.

**Behavior that must be documented and probed:**

1. **The last family write wins.** `kvar=600, kV=12.47` gives `Cuf` 10.235; writing `Cuf=10` leaves `kvar` at **[1200]** and drives `NormAmps`/`EmergAmps` to **0.000**; writing `kvar` again restores `Cuf` from the kvar family. Describe `SpecType` as engine state, not a property, and warn that the non-selected family's readbacks go stale.
2. **The `Cuf` family does not maintain the kvar-side readbacks.** `RecalcElementData` accumulates `Ftotalkvar` as `w·FC·PhasekV²/1000` (L663-L665), which for `Cuf=10` at 7.1995 kV per phase returns ~1.95e-4 instead of ~195 kvar per phase, so `NormAmps`/`EmergAmps` read ~0 while the Y matrix is built from `FC` directly. State the measured readbacks, describe the mechanism as a unit inconsistency in the accumulator, and validate the electrical result with a **solve** rather than the rating readbacks. Do not claim a specific "correct" kvar without showing the solve.
3. **`CMatrix` accepts any length and reads back 9 values for three phases.** Both a 6-value and a 9-value input were accepted and read back as nine values; `kvar` and `Cuf` keep the kvar-family values. Use the documented lower-triangle notation `c11 | -c21 c22 | -c31 -c32 c33`, microfarads, and record that the property is scaled by `1e-6`.
4. **`NumSteps` re-divides the total kvar.** A default 1200 kvar bank with `NumSteps=4` becomes `[300, 300, 300, 300]` with `Cuf` `[5.1175 × 4]`, `R`/`XL`/`Harm` copied, **all `States` set to 1**, and `LastStepInService` updated (L387-L455). The stored total is preserved, not multiplied.
5. **Array length must equal `NumSteps`, and order matters.** `kvar = [100,200]` on a four-step bank raises `#20200425 Capacitor.m.kvar: Invalid number of elements. Expected 4 elements, got 2`. Worse, `new("a", kV=12.47, Cuf=10, NumSteps=2)` succeeds but leaves `kvar` **[1200.0, 0.0]** (mixed), while `new("b", kV=12.47, NumSteps=2, Cuf=10)` raises `Expected 2 elements, got 1`. Always set `NumSteps` first, then pass a full-length array.
6. **Connection drives the terminal count.** Wye three-phase: `NumTerminals()` 2, `NumConductors()` 3. Delta three-phase: **`NumTerminals()` 1**, 3 conductors. Delta with one phase: 1 terminal, **2** conductors. Wye one phase: 2 terminals, 1 conductor. `Phases = 0` raises `#2020031 Value (0) cannot be zero`.
7. **Delta drops `Bus2`.** On a delta object `Bus2` reads back empty; switching that object back to wye invented a **new bus `d1_2`** instead of restoring the original. Set connection and buses together, and never toggle `Conn` on a series capacitor.
8. **`Bus2` defaulting is a `Bus1` side effect** (L303-L321): on a wye object `Bus2` becomes `Bus1` plus one `.0` per phase, giving grounded-wye shunt behavior. An explicit different `Bus2` makes it a series element (`IsShunt` false), which then returns balanced in/out powers — probed as `[-2.68-3.44j, 2.68+3.37j]` kVA across a 3 MW load, and 0 when the element sits across a near-zero voltage difference (two parallel lines).
9. **All v6-era properties are gone** (`#110 Unknown parameter` / `AttributeError`): `Model`, `Vmin`, `Vmax`, `StepSize`, `Vharmonics`, `State`, `PctLead`, `PctLag`, `PtPhase`, `Userated`, `Spectrum`. Any example copied from the EPRI page or older references that uses them must be rewritten; `States` replaces `State`.
10. **`States` writes are not honored through the Python attribute.** `c.States = np.array([0,1,1,0], dtype=np.int32)` left the array unchanged (`[1,0,0,0]`), while `Edit Capacitor.c1 States=(1,0,0,0)` took effect. Verify this on the pinned stack, document the working path, and treat silent no-ops as a hazard rather than a feature.
11. **`States` are electrically real.** A four-step 1200 kvar bank with all steps on returned `-j1208.2` kvar after the solve; `States=(1,0,0,0)` returned `-j302.05` (one quarter). This is the control hook that `CapControl` modifies.
12. **`TotalPowers()` returns a complex array, one entry per terminal** — 2 for wye, 1 for delta. Casting it with `float()` silently discards the reactive part (numpy `ComplexWarning`), so examples must print real and imaginary parts explicitly.
13. **Explicit `NormAmps` is sticky.** With `NormAmps=50` on a 1200 kvar bank, changing `kvar` to 2400 left `NormAmps` at 50.0 while `EmergAmps` recomputed 100.006 → 200.012; without an explicit value both recomputed (75.005 → 150.009 and 100.006 → 200.012). The `normAmpsSpecified`/`emergAmpsSpecified` flags are the reason, and `EmergAmps` deliberately ignores `NormAmps` (see the code comment at L690-L693).
14. **`Like` is in `CapacitorProperties` but read-only on the object.** `new(..., Like="q")` raises `AttributeError: 'Capacitor' object attribute 'Like' is read-only`; `New Capacitor.cp Like=q` works, copies `kV`/`kvar`/`Conn`, keeps the target's own `Bus1`, and does **not** recompute the terminal count (the copy read `Conn=delta` with `NumTerminals()` still 2). Catalog it as a creation keyword only.
15. **Percent and hour units:** `pctPerm` reads back in percent (50 written, 50.0 read) and `Repair` in hours (3.0 default). Cite the inherited `PDClass`/`PDElement` lines for both rather than the Capacitor file.
16. **`NumSteps` carries `SuppressJSON`** (L281-L283), so it may be missing from JSON property dumps even though it is a real property. Note it wherever the catalog describes JSON behavior.
17. **`CMatrix`, `Cuf`, `kvar`, `R`, `XL`, `Harm`, and `States` are arrays in the wrapper.** Their `data_type` must not be `float`/`int`; record the array element type and the `NumSteps` length, and state whether the readback is `Float64Array`/`Int32Array` or a plain list.

## Required approach

- Every row carries `source_refs` citing the pinned wrapper TypedDict or the engine property block; inherited rows cite `PDElement.pas`/`PDClass.pas`/`CktElement.pas`.
- Keep `data_type` consistent with the observed readback, including the six array properties and the `Connection` enum member.
- Do not state a default you cannot defend. Where the constructor literal and the readback differ (`Cuf` 20.47 µF derived from 1200 kvar, `NormAmps`/`EmergAmps` derived from the rating), state both and say which one a user sees.
- Represent the three families in `property_requirements.conditionals` exactly as the engine declares them, note that `kV` participates in two of them, and state that the Python constructor applies arguments in order.
- Record the `CapControl` coupling as a scope note with a citation, and do not catalog its properties.
- Do not modify prior catalogs, packages 1–4, or existing audits and QA reports. Additions to `dss_capi.json` and `sources.json` only.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt` and record the environment block.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_capacitor.py
```

The matrix must cover, at minimum: default readbacks for every catalogued row including array shapes and the `Connection` enum; each of the three families and what the other families' readbacks do afterwards; the `Cuf`-family rating anomaly with a solve that reports the actual reactive output; the `NumSteps` division and array-length error; the `Conn`/`Phases` terminal and conductor counts including delta; the `Bus2` default and series-element behavior; the `States` text-versus-attribute divergence and its electrical effect; the `NormAmps` stickiness probe; the `Like` keyword path; and a solve that reads back per-terminal complex power. Label anything not executed as `not-run`.

## Definition of done

1. Schema pair registered and passing (14/14 or more).
2. Catalog validates; every row has source refs; one element class; array and enum types match the wrapper's readback.
3. Engine records cite `0.14.5` ranges; `tested` reflects what actually ran.
4. Workflow documents the three families, `NumSteps`/array ordering, wye/delta/shunt/series wiring, `States` and `CapControl` coupling, and the traps.
5. Examples pass through the harness and are recorded `Observed-working` with the environment.
6. Readback matrix committed with the environment block and date.
7. Audit records method, counts, checks, limitations, and the `CapControl` scope note.
8. QA handoff prepared and pinned to the package commit.
9. Manifest, plan, READMEs, and skill updated to the real validation level.

## Out of scope

`CapControl` property catalog, `Reactor`, `Generator`, energy meters, `Fault`, harmonic and reliability studies beyond the documented filter properties, Phase 4 fixtures, `opendss_objects` roll-up, `python_interface_comparison`, and `troubleshooting` seeding.

## Commit and review

- Commit package 5 on `wp/phase3` with a message naming the package; keep unrelated edits out and do not mix it with package 4.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings; do not start package 6 (`Generator`) until the owner accepts this one.
