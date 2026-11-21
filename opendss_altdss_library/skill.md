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

Phase 1 establishes schemas, source inventory, package structure, handoffs, audits, and starter catalogs. Use the Line/LineCode starter catalog as a source index and confirm any version-sensitive claim against pinned primary evidence before generating code. Phase 2 covers source remediation. Run engine examples during the project's runtime validation phase.

## Validation language

Distinguish schema review, source review, example inspection, and runtime execution. Do not claim compatibility until representative tasks run against the manifest target and record the environment and result.
