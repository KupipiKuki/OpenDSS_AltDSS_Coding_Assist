# OpenDSS and AltDSS Library Instructions

## Target and boundaries

Use `manifest.json` for supported versions. The primary Python target is AltDSS-Python 0.2.4 with DSS-Python 0.15.7 and DSS C-API backend 0.14.5. Treat beta releases as future compatibility notes. EPRI documentation can be mixed-version; retain page URLs, access dates, and version qualifiers.

Keep `altdss`, `dss`, `opendssdirect`, and low-level C-API namespaces distinct. EPRI sources establish the OpenDSS model; DSS-Extensions sources establish their own package and engine behavior.

## Where to look

- Element properties: use the [Line/LineCode catalog](references/lines/opendss_line_linecode_properties.json) or the [line geometry and conductor catalog](references/lines/line_geometry_wires_properties.json) for LineGeometry, LineSpacing, WireData, CNData, and TSData.
- Python signatures and property types: [altdss_python_api.json](references/altdss_python_api.json), generated from the pinned 0.2.4 wheel.
- Engine behavior: [dss_capi.json](references/dss_capi.json), with file and line citations and a `tested` status per record.
- Source and version index: [sources.json](references/sources.json); every example and catalog entry resolves its ids there.

## Working with records

1. Search the library and source inventory before adding a claim.
2. Preserve source URLs, revision or tag, and access date. Use `Official-versioned` for official material tied to a specific version. Cite undated pages for the information they explicitly document and seek pinned evidence for behavior that depends on the selected release.
3. Use `Observed-working` only after recording a reproducible run and environment. `Example-only` means inspected but not run.
4. Mark properties excluded from the target with `supported_in_target: false`; do not generate target API calls for them.
5. Represent conditional creation requirements as structured groups, not prose inside `required_properties`.
6. Do not infer defaults or method names. Record unresolved items as `Unverified`.

## Phase placement

Phase 1 established schemas, source inventory, package structure, handoffs, audits, and starter catalogs. Phase 2 delivered the Line/LineCode pilot and is complete: catalog, source index, workflow, examples (`Observed-working`), validation harness, and independent QA/QC. Phase 3A added the generated AltDSS-Python API catalog and the DSS C-API engine catalog; Phase 3B continues with dependency-ordered element packages; Phase 4 runs fixture-based validation against recorded golden results; Phase 5 adds retrieval and release packaging. The [implementation plan](../docs/implementation_plan.md) carries scope, order, and exit criteria. Use the Line/LineCode package as the worked example, and confirm any version-sensitive claim against pinned primary evidence before generating code.

For Line and LineCode creation, start with the workflow guide. Use the example catalog to find the script and its execution status, then resolve its `source_ids` in the source index. [Workflow guide](../docs/workflows/line_linecode.md) · [Example catalog](references/examples.json) · [Source index](references/sources.json)

For construction-based lines, use the geometry and conductor workflow for property order, units, and the limits of the pinned geometry readbacks. [Workflow](../docs/workflows/line_geometry_wires.md) · [Package audit](../docs/audits/phase3b_line_geometry_wires_audit.md)

For circuit initialization, use the context command `New Circuit.<name>` and read the built-in source through `ctx.Vsource["source"]`. The Vsource workflow explains impedance families, frequency, terminal defaults, and the DSS text path for `Z1` and `Z0`. [Workflow](../docs/workflows/circuit_vsource.md) · [Property catalog](references/circuit/vsource_properties.json) · [Runtime matrix](../docs/audits/phase3b_circuit_vsource_readback.json)

For Transformer and XfmrCode, use two or three windings. Set dimensions or assign the code before winding arrays, bus connections, and overrides. Use `wdg` for selected-winding DSS text access. The workflow covers reactance ordering, tap writes, winding results, and pinned engine behavior. [Workflow](../docs/workflows/transformer.md) · [Property catalog](references/transformers/transformer_properties.json) · [Runtime matrix](../docs/audits/phase3b_transformer_readback.json)

For Load, choose one base-power family and complete the edit before reading derived fields. Set PF before connected-kVA allocation inputs. Provide seven ZIPV coefficients when using Model 8. The workflow covers topology, shape assignment, and actual served power. [Workflow](../docs/workflows/load.md) · [Property catalog](references/loads/load_properties.json) · [Runtime matrix](../docs/audits/phase3b_load_readback.json)

For Capacitor, set connection and step count before wiring the bank and writing the step arrays. Choose one capacitance family. Write `States` through DSS text on the pinned backend, then solve and inspect complex per-terminal power. Check the pinned caveats for unequal kvar inputs, derived amp ratings, and copy actions. [Workflow](../docs/workflows/capacitor.md) · [Property catalog](references/capacitors/capacitor_properties.json) · [Runtime matrix](../docs/audits/phase3b_capacitor_readback.json)

For Generator, choose a scheduled power pair and use kVA for the machine rating. Set Model 3 reactive limits after the power pair, and check achieved voltage and complex terminal power after solving. Generator's built-in dispatch flags and the separate GenDispatcher controller have distinct paths. [Workflow](../docs/workflows/generator.md) · [Property catalog](references/generators/generator_properties.json) · [Runtime matrix](../docs/audits/phase3b_generator_readback.json)

## Validation language

Distinguish schema review, source review, example inspection, and runtime execution. Do not claim compatibility until representative tasks run against the manifest target and record the environment and result. `Observed-working` requires a committed example file, a harness run with the recorded environment, and a date; use `Example-only` until that exists.

Run the committed harness before any catalog or example change:

```powershell
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_transformer.py
python opendss_altdss_library/tools/readback_load.py
python opendss_altdss_library/tools/readback_capacitor.py
python opendss_altdss_library/tools/readback_generator.py
python opendss_altdss_library/tools/build_altdss_api_catalog.py --source-dir <extracted-wheel>/altdss --out opendss_altdss_library/references/altdss_python_api.json
```

Every catalog declared in `manifest.json` must have a schema pairing in `validate_catalogs.py`; an unpinned catalog fails the run on purpose. When the Phase 4 harness lands, fixture results are compared against `golden.json` within recorded tolerances, and golden files change only through the approved update path.


