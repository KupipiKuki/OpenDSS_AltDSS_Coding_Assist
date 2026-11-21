# Coder Handoff: Phase 3B Package 1 — LineGeometry, LineSpacing, Conductor Data

## Roles and gate

- **Coder:** GPT-6.2 Sol.
- **Architect / auditor:** DeepSeek.
- **Independent QA/QC:** Mistral 4.
- **Owner:** decides which findings block merge and approves scope changes.

Work on `wp/phase3` (or a task branch from it), commit the package there, and hand it to independent QA/QC before the owner considers it complete.

## Goal

Deliver the first Phase 3B element package — `LineGeometry`, `LineSpacing`, `WireData`, `CNData`, and `TSData` — using the same six-artifact pattern that passed review for Line/LineCode. This package unblocks the Line geometry path and the `Spacing` + `Conductors` (`wires`) path already described in the Line/LineCode workflow.

**Targets:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5`.

## Read first

- [Implementation plan](../implementation_plan.md) — §5.3 order, §5.4 template and definition of done, §8 evidence policy
- [Manifest](../../opendss_altdss_library/manifest.json) — support targets and known gaps
- [Line/LineCode package](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties.json) and its [audit](../audits/line_linecode_schema_audit.md) — the worked example
- [Phase 3A audit](../audits/phase3a_api_catalogs_audit.md) and [QA report](../audits/phase3a_api_catalogs_qaqc.md) — catalogs, generator, and the review standard
- [Skill](../../opendss_altdss_library/skill.md) — working rules and validation commands

## Deliverables

| # | Artifact | Path | Notes |
|---|---|---|---|
| 1 | Generalized element schema | `schemas/catalogs/element_properties.schema.json` | Same field set as the Line/LineCode schema; `element_class` is a non-empty string (not an enum); every property row requires a non-empty `source_refs` array. Future packages reuse this schema; the Line/LineCode schema stays as published. |
| 2 | Property catalog | `references/lines/line_geometry_wires_properties.json` | One file, five `element_class` values: `LineGeometry`, `LineSpacing`, `WireData`, `CNData`, `TSData`. Grouping decision: these are the line-construction inputs and share one workflow; split later only if review shows a reason. |
| 3 | Source index additions | `references/sources.json` | Add EPRI pages and tagged wrapper/engine files. Preserve existing ids; new ids follow the kebab-case pattern. |
| 4 | Engine records | `references/dss_capi.json` | Add property enums, defaults, unit/scale flags, alias and redundancy rows, and required/ordering flags for the five classes. Confirm exact enum names from source (for example `TLineGeometryProp`); do not guess. |
| 5 | Workflow | `docs/workflows/line_geometry_wires.md` | Geometry path (`LineGeometry` + `Line.Geometry` + `Length`) and spacing path (`LineSpacing` + `WireData`/`CNData`/`TSData` + `Line.Spacing` before `Line.Conductors`). State unit rules, `reduce`, and which setters replace prior impedance definitions. |
| 6 | Examples | `examples/line_geometry/` + `references/examples.json` | At least one Python `altdss` example and one DSS text example; records use `source_ids`; run through `tools/run_examples.py` and record `Observed-working` with the environment block. |
| 7 | Audit | `docs/audits/phase3b_line_geometry_wires_audit.md` | Method, coverage counts, checks performed, limitations, open items. |
| 8 | QA handoff | `docs/handoffs/Phase_3B_LineGeometry_WireData_QAQC_handoff.md` | Same shape as the Phase 3A handoff: review target pinned to commit, setup commands, checklist, report format, declared scope boundaries. |

## Sources

| Element | EPRI page | Wrapper (0.2.4) | Engine (0.14.5) |
|---|---|---|---|
| LineGeometry | `https://opendss.epri.com/LineGeometry.html` | `altdss/LineGeometry.py` | `src/General/LineGeometry.pas` |
| LineSpacing | `https://opendss.epri.com/LineSpacing.html` | `altdss/LineSpacing.py` | `src/General/LineSpacing.pas` |
| WireData | `https://opendss.epri.com/WireData.html` | `altdss/WireData.py` | `src/General/WireData.pas` |
| CNData | `https://opendss.epri.com/CNData.html` | `altdss/CNData.py` | `src/General/CNData.pas` |
| TSData | No page found (404 on `TSData.html` at check time) | `altdss/TSData.py` | `src/General/TSData.pas` |

Record the TSData page absence in the source index scope note rather than inventing a citation. EPRI pages establish OpenDSS model behavior; the tagged wrapper and engine establish API names, types, units, and defaults. Keep those families separate in every row.

## Required approach

- Every property row carries `source_refs`; if a row is supported by the element-level sources only, cite the specific page or module that supports the type/default claim.
- Verify defaults against the pinned engine constructor, units against the engine property flags (for example nF/uS/ohm-per-length), and names/types against the 0.2.4 wrapper `*Properties` TypedDicts and property blocks.
- Record exact creation keyword casing and the collection member (`altdss.LineGeometry`, `altdss.LineSpacing`, `altdss.WireData`, `altdss.CNData`, `altdss.TSData`) as exposed by the 0.2.4 context.
- Distinguish complete engine specification sets from minimum text-command or Python constructor inputs.
- Document cross-element effects: `Line.Geometry` supersedes other impedance definitions and recomputes on frequency or `rho` changes; `Line.Spacing` must be assigned before `Conductors`; conductor objects share storage across `WireData`/`CNData`/`TSData` aliases where the engine does so.
- Mark any property absent from the pinned target with `supported_in_target: false` and exclude it from generated calls.
- Do not infer defaults, names, or equivalence. Unresolved items stay `Unverified` or open questions.
- Do not modify the Line/LineCode catalog, the Phase 3A catalogs, or existing QA reports. Additions to `dss_capi.json` and `sources.json` are expected; no deletions.

## Runtime evidence

Use a fresh environment from `tools/requirements-validation.txt`. Produce a property-readback matrix (defaults for every catalogued property) for each of the five classes on the pinned stack, and record the environment. Run both examples through the harness; only then label them `Observed-working`. A source-only pass is not runtime validation.

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
```

Register the new catalog and schema in `tools/validate_catalogs.py`; the run fails on a manifest catalog without a schema pairing.

## Definition of done

1. Schema pair registered and passing (10/10 or more).
2. Catalog validates against `element_properties.schema.json`; every row has source refs.
3. Engine records cite `0.14.5` file and line ranges; `tested` reflects what actually ran.
4. Workflow documents both impedance paths and the ordering rules.
5. Examples pass through the harness and are recorded `Observed-working` with environment.
6. Audit records method, counts, checks, and limitations.
7. QA handoff prepared and pinned to the package commit.
8. Manifest, plan, READMEs, and skill updated to the real validation level.

## Out of scope

`Circuit`/`Vsource`, `Transformer`, `Load`, `Capacitor`, `Generator` (later packages), `opendss_objects` roll-up, `python_interface_comparison`, `troubleshooting` seeding beyond anything the examples force, and the Phase 4 fixture harness.

## Commit and review

- Commit the package on `wp/phase3` with a message naming the package; keep unrelated edits out.
- Push and hand to QA/QC with the commit hash and clean-tree state.
- The owner dispositions QA findings; do not start the next package until the owner accepts this one.
