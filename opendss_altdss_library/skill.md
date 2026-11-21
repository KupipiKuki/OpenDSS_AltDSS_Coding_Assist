# OpenDSS and AltDSS Library Instructions

## Target and boundaries

Use `manifest.json` for supported versions. The primary Python target is AltDSS-Python 0.2.4 with DSS-Python 0.15.7 and DSS C-API backend 0.14.5. Treat beta releases as future compatibility notes. EPRI documentation can be mixed-version; retain page URLs, access dates, and version qualifiers.

Keep `altdss`, `dss`, `opendssdirect`, and low-level C-API namespaces distinct. EPRI sources establish the OpenDSS model; DSS-Extensions sources establish their own package and engine behavior.

## Working with records

1. Search the library and source inventory before adding a claim.
2. Preserve source URLs, revision or tag, and access date. Use `Official-versioned` for official material tied to a specific version. Cite undated pages for the information they explicitly document and seek pinned evidence for behavior that depends on the selected release.
3. Use `Observed-working` only after recording a reproducible run and environment. `Example-only` means inspected but not run.
4. Mark properties excluded from the target with `supported_in_target: false`; do not generate target API calls for them.
5. Represent conditional creation requirements as structured groups, not prose inside `required_properties`.
6. Do not infer defaults or method names. Record unresolved items as `Unverified`.

## Phase placement

Phase 1 established schemas, source inventory, package structure, handoffs, audits, and starter catalogs. Phase 2 delivered the Line/LineCode pilot and is complete: catalog, source index, workflow, examples (`Observed-working`), validation harness, and independent QA/QC. Phase 3 scales the same pattern to the API and engine catalogs and then to dependency-ordered element packages; Phase 4 runs fixture-based validation against recorded golden results; Phase 5 adds retrieval and release packaging. The [implementation plan](../docs/implementation_plan.md) carries scope, order, and exit criteria. Use the Line/LineCode package as the worked example, and confirm any version-sensitive claim against pinned primary evidence before generating code.

For Line and LineCode creation, start with the workflow guide. Use the example catalog to find the script and its execution status, then resolve its `source_ids` in the source index. [Workflow guide](../docs/workflows/line_linecode.md) · [Example catalog](references/examples.json) · [Source index](references/line_linecode_sources.json)

## Validation language

Distinguish schema review, source review, example inspection, and runtime execution. Do not claim compatibility until representative tasks run against the manifest target and record the environment and result. `Observed-working` requires a committed example file, a harness run with the recorded environment, and a date; use `Example-only` until that exists.

Run the committed harness before any catalog or example change:

```powershell
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
```

Every catalog declared in `manifest.json` must have a schema pairing in `validate_catalogs.py`; an unpinned catalog fails the run on purpose. When the Phase 4 harness lands, fixture results are compared against `golden.json` within recorded tolerances, and golden files change only through the approved update path.


