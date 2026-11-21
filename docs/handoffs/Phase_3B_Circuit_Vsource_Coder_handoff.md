# Coder Handoff: Phase 3B Package 2 — Circuit and Vsource

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3` (or a task branch from it). Package 1 is reviewed and accepted by QA/QC and the architect/auditor (`13c3831`); do not reopen it. Commit package 2 on `wp/phase3`, push, and hand it to independent QA/QC before the owner considers it complete.

## Goal

Deliver Phase 3B package 2 — the **Circuit** creation path and the **Vsource** source element — with the same six-artifact pattern used for Line/LineCode and package 1. This package establishes how a circuit is created and how the Thevenin source equivalent behind it is configured and read back, which every later package and the Phase 4 fixtures depend on.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Scope decision: what "Circuit" means in this stack

Treat these as the package's fixed scope. They are verified facts on the pinned stack; re-confirm each with a citation and a readback rather than taking them from this handoff.

1. **There is no `Circuit` element class in AltDSS-Python 0.2.4.** The pinned distribution has `altdss/CircuitElement.py` (a mixin base) but no `Circuit.py`, no `CircuitProperties` TypedDict, and no `ctx.Circuit` attribute. Creation is a command: `dss("new Circuit.test")` (`altdss/AltDSS.py` L436-L444 documents the form). The circuit name is the object identifier users pass in that command.
2. **The engine `TCircuit` is a container, not a property table.** `TDSSCircuit = class(TNamedObject)` (`src/Common/Circuit.pas` L61) holds buses, elements, and the solution; it declares no `TCircuitProp` enum. Circuit-level electrical parameters are not circuit properties.
3. **`New Circuit.<name> ...` parameters configure the automatically created Vsource named `source`.** Verified on 0.2.4: after `New Circuit.t BasekV=12.47 Phases=3 Bus1=src pu=0.98 Angle=5`, the context holds exactly one Vsource, `ctx.Vsource["source"]`, reporting `BasekV` 12.47, `Phases` 3, `Bus1` src, `pu` 0.98, `Angle` 5.0. Document the routing and cite where the command parameters are applied.
4. **Circuit-level readback goes through the source element, `Solution`, and `Bus`,** not through a circuit object. State the recommended readback path for the parameters users most often set on the creation command.

Consequences for the catalog:

- The `Circuit` entry is intentionally thin: the `name` row, plus `property_requirements` and `notes` that give the creation command shape, the parameter-to-Vsource routing, and the readback path.
- **Do not duplicate the Vsource rows under `Circuit`.** One authoritative row per property avoids default drift; the `Circuit` entry points at the `Vsource` rows.
- The `Vsource` entry carries the full property set, including inherited rows.
- `altdss_mapping` for `Circuit` must describe the command path (for example `altdss context Commands("New Circuit.<name> ...")`), since no element class exists. `altdss_mapping` for `Vsource` is `altdss.Vsource`.

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- Package 1 for the current standard: [catalog](../../opendss_altdss_library/references/lines/line_geometry_wires_properties.json) · [workflow](../workflows/line_geometry_wires.md) · [build audit](../audits/phase3b_line_geometry_wires_audit.md) · [QA report](../audits/phase3b_line_geometry_wires_qaqc.md) · [architect review](../audits/phase3b_line_geometry_wires_architect_audit.md)
- [Line/LineCode package](../audits/line_linecode_schema_audit.md) — the original worked example, including the `Line.Geometry`/`Line.Spacing` reuse path
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Property catalog | `references/circuit/vsource_properties.json` | Two `element_class` values: `Circuit` (thin, routing only) and `Vsource` (full). Reuse `schemas/catalogs/element_properties.schema.json`; no new schema is expected. Every row needs `source_refs`. |
| 2 | Source index additions | `references/sources.json` | EPRI `Vsource.html` and `Circuit.html`, the 0.2.4 wrapper modules, the 0.14.5 engine files, and the inherited-class files cited by `Spectrum`, `BaseFreq`, and `Enabled`. Preserve existing ids; additions only. |
| 3 | Engine records | `references/dss_capi.json` | Add `TVsourceProp` rows and the behaviors below: spec-type precedence, ZBase scaling, the `Z1`/`Z0` wrapper gap, `Spectrum` default object, `Frequency` tracking the circuit, and the `New Circuit` routing. Cite `0.14.5` file and line ranges. |
| 4 | Workflow | `docs/workflows/circuit_vsource.md` | Circuit creation, source configuration paths, impedance specification precedence, unit/base rules, readback paths, and the traps listed below. |
| 5 | Examples | `examples/circuit_source/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; `source_ids` recorded; run through `tools/run_examples.py` and labelled `Observed-working` with the environment block. |
| 6 | Readback tool and matrix | `tools/readback_circuit_vsource.py`, `docs/audits/phase3b_circuit_vsource_readback.json` | Defaults for every catalogued row plus the behavior probes below, with the environment block and date. |
| 7 | Audit | `docs/audits/phase3b_circuit_vsource_audit.md` | Method, coverage counts, checks performed, limitations, open items. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_Circuit_Vsource_QAQC_handoff.md` | Pinned to the package commit; checklist and report format as in the package 1 handoff. |

Register the new catalog in `tools/validate_catalogs.py` (`SCHEMA_PAIRS`); the run fails on a manifest catalog without a schema pairing. Expect 11/11 pairs.

## Sources

| Surface | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| Circuit creation | `https://opendss.epri.com/Circuit.html` (200; content is JS-rendered) | `altdss/AltDSS.py` (`dss(...)` context commands), `altdss/CircuitElement.py` | `src/Common/Circuit.pas` (`TDSSCircuit`) |
| Vsource | `https://opendss.epri.com/Vsource.html` (200; intro paragraph only in static HTML) | `altdss/Vsource.py` | `src/PCElements/VSource.pas` (note the capital `S`) |
| Inherited `Enabled` | — | `altdss/Vsource.py` TypedDict | `src/Common/CktElement.pas` (`Enabled`, default TRUE) |
| Inherited `BaseFreq` | — | `altdss/Vsource.py` TypedDict | `src/Common/CktElement.pas` (`BaseFrequency`) |
| Inherited `Spectrum` | — | `altdss/Vsource.py` TypedDict | `src/PCElements/PCElement.pas` |

The EPRI `Vsource.html` static HTML carries the model concept only: "A Vsource object is a two-terminal, multi-phase Thevenin (short circuit) equivalent … Line-line voltage (kV) and short circuit MVA." The property table is loaded by script, so field-level types, defaults, and units must rest on the tagged wrapper and engine. Cite the EPRI page for the model concept and keep it separate from field claims, as in package 1. `Circuit.html` returns 200 but is likewise not a field-level source; do not invent citations from it.

## Established facts to reuse and re-verify

Verified by the architect on 0.2.4 / 0.15.7 / 0.14.5 (2026-11-21). Reproduce each in your own environment and record the result; do not copy these numbers without a run.

**Wrapper surface (`altdss/Vsource.py`)**
- Element class L17; `VsourceProperties` TypedDict L694-L725; `IVsource.new` L1498.
- 33 creation keywords: `Bus1`, `BasekV`, `pu`, `Angle`, `Frequency`, `Phases`, `MVASC3`, `MVASC1`, `X1R1`, `X0R0`, `Isc3`, `Isc1`, `R1`, `X1`, `R0`, `X0`, `ScanType`, `Sequence`, `Bus2`, `Z2`, `puZ1`, `puZ0`, `puZ2`, `BaseMVA`, `Yearly`, `Daily`, `Duty`, `Model`, `puZIdeal`, `Spectrum`, `BaseFreq`, `Enabled`, `Like`.
- **Wrapper gap:** the engine enum also declares `Z1` (20) and `Z0` (21), but the pinned wrapper exposes neither (`hasattr(vsource, "Z1")` is False; `"Z0"` likewise) while `Z2`, `puZ1`, `puZ0`, and `puZ2` are present. Record `Z1`/`Z0` as engine rows that are reachable through DSS text, note the absent Python member, and say what you verified. Do not silently drop them.

**Engine surface (`src/PCElements/VSource.pas`)**
- `TVsourceProp` enum L57-L90: 30 properties after `INVALID`, `Bus1` through `puZIdeal`.
- `DefineProperties` L219-L356; `PropertySideEffects` L369-L525; constructor L607-L669.
- Constructor literals: `Phases=3`, `Nconds=3`, `Nterms=2`, `MVAsc3=2000`, `MVAsc1=2100`, spec type defaults to MVAsc, `R1=1.65`, `X1=6.6`, `R2=R1`, `X2=X1`, `R0=1.9`, `X0=5.7`, `Isc3=10000`, `Isc1=10540`, `X1R1=4.0`, `X0R0=3.0`, `pu=1.0`, `BasekV=115`, `BaseMVA=100`, `Angle=0`, `ScanType=1`, `Sequence=1`, `puZIdeal=1e-6+0.001j`, `Spectrum` defaults to the `defaultvsource` spectrum object.
- Property tracking is set on `MVASC3`, `MVASC1`, and `BasekV` at construction, which is how later assignments select and supersede the impedance specification.

**Behavior traps to document and probe**
1. **The literal constructor ohms are not what users read back.** A standalone `Vsource.new("v2", Bus1="b2", BasekV=115, Phases=3)` reported `R1` 1.60377, `X1` 6.41507, `R0` 1.79604, `X0` 5.38811 — derived from the per-unit sequence impedance and `ZBase = BasekV² / BaseMVA`. Catalog defaults must distinguish constructor literals from derived readbacks, or the row will be wrong for one of the two cases.
2. **`R1`/`X1`/`R0`/`X0` are reported in ohms and scale with the base.** Setting `BasekV` from 115 to 12.47 on the same object produced `R1` 0.0188573, `X1` 0.0754290, `R0` 0.0211180, `X0` 0.0633539, while `puZ1` stayed 0.0121268+0.0485071j. This is the unit/base trap of this package; state it as scaling by `ZBase`, with the probe recorded.
3. **`pu` is per-unit voltage, not impedance.** The constructor comments the distinction. Do not describe `pu` as an impedance and do not conflate it with `puZ1`/`puZ0`/`puZ2`/`puZIdeal`.
4. **Specification precedence.** `MVAsc3`/`MVAsc1`, `Isc3`/`Isc1`, `X1R1`/`X0R0`, the `R1`/`X1`/`R0`/`X0` pair, `Z1`/`Z0`, and the per-unit forms select among impedance specifications. Setting `X1R1=10` on the example object moved `X1`/`R1` to a 10:1 ratio while other state persisted. Record which input wins, cite the code path, and show one probe per family.
5. **`Frequency` follows the circuit.** A new source reports 60 in a default circuit because the constructor takes `BaseFrequency`, and `BaseFrequency` follows the circuit fundamental. Record it as circuit-dependent, verify by changing the system frequency, and keep `Frequency` distinct from the inherited `BaseFreq`.
6. **`ScanType`, `Sequence`, and `Model` are enum-valued and read back as integers** (1, 1, 0 on a fresh source) even though the wrapper accepts strings, ints, or enum members. Choose the `data_type` from the observed readback, as package 1 did for `LineGeometry.linetype`, and list the accepted forms in the description.
7. **`Spectrum` returns an object reference** (`<Spectrum.defaultvsource>`), not a name string. Record the default object and how it prints; `Yearly`, `Daily`, and `Duty` default to `None`; `Enabled` defaults to `True`.
8. **`Bus2` and the two-terminal model.** The source is a two-terminal device (`Nterms=2`); document what `Bus2` does when it is unset and what the readback shows.

## Required approach

- Every row carries `source_refs`; cite the pinned wrapper TypedDict or the engine property block that supports each type, default, and unit claim. Inherited rows cite the base-class file, not `Vsource.pas`.
- Record exact creation keyword casing for `ctx.Vsource.new(...)` and confirm the collection member name at runtime. For `Circuit`, record the command form (`New Circuit.<name> ...`) exactly.
- Distinguish complete engine specification sets from minimum constructor inputs in `property_requirements`, with `requirement_groups` where alternatives exist (for example the impedance specification families).
- Mark what the pinned target cannot do. Use `supported_in_target: false` only when the pinned stack cannot reach the property at all; when the Python member is absent but DSS text works, keep the row supported and state the access path.
- Do not infer defaults from an EPRI page or from this handoff. Unresolved items stay `Unverified` or open questions in the audit.
- Do not modify the Line/LineCode catalog, the Phase 3A catalogs, package 1 files, or any existing audit or QA report. Additions to `dss_capi.json` and `sources.json` only.
- Keep the automated-variation surface honest: if the built-in `Vsource` created by `New Circuit` is the only source in scope, say so; do not imply a multi-source sweep was executed.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt` and record the environment block.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_circuit_vsource.py
```

The matrix must cover, at minimum: constructor readbacks for every catalogued `Vsource` row; the `New Circuit` → `source` routing; the ZBase-scaling probe; one probe per impedance specification family; the frequency-follows-circuit probe; the `Z1`/`Z0` access path; and the enum readbacks. A source-only pass is not runtime validation.

## Definition of done

1. Schema pair registered and passing (11/11 or more).
2. Catalog validates; every row has source refs; `Circuit` and `Vsource` mappings are explicit and match runtime.
3. Engine records cite `0.14.5` ranges; `tested` reflects what actually ran.
4. Workflow documents creation, the specification precedence, the base/unit scaling, the frequency behavior, and the readback paths.
5. Examples pass through the harness and are recorded `Observed-working` with the environment.
6. Readback matrix committed with the environment block and date.
7. Audit records method, counts, checks, limitations, and open items.
8. QA handoff prepared and pinned to the package commit.
9. Manifest, plan, READMEs, and skill updated to the real validation level.

## Out of scope

`Transformer`, `Load`, `Capacitor`, `Generator` (later packages), the full C-API `Circuit_*` function surface, `Solution`/`Bus` property catalogs, the `opendss_objects` roll-up, `python_interface_comparison`, `troubleshooting` seeding beyond what the examples force, and the Phase 4 fixture harness.

## Commit and review

- Commit the package on `wp/phase3` with a message naming the package; keep unrelated edits out.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings; do not start package 3 (`Transformer`) until the owner accepts this one.
