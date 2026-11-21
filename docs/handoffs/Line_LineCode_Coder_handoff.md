# Coder Handoff: Line and LineCode Catalog

## Goal

Maintain the Phase 1 starter catalog at `opendss_altdss_library/references/lines/opendss_line_linecode_properties.json` for the stable target in the package manifest: AltDSS-Python 0.2.4, DSS-Python 0.15.7, and backend 0.14.5. Complete its source remediation during Phase 2.

## Required approach

- Read the charter, package skill, manifest, current catalog, external audit, and current Line/LineCode audit before editing.
- Use EPRI pages for OpenDSS behavior and release-tagged DSS-Extensions sources for target API and engine behavior. Keep these source families distinct.
- Record source URL, tag/revision, access date, and which fields the source supports.
- Keep `required_properties` limited to unconditional requirements. Put alternatives and conditions in `property_requirements.conditional`.
- Use `Official-versioned` for official evidence tied to a specific version. For undated documentation, cite the page and verify version-sensitive behavior against a pinned source. Use `Observed-working` only for a recorded run.
- Mark properties excluded from the target with `supported_in_target: false`; do not emit target API calls for them.
- Preserve historical artifacts under archive names; do not use them as active data.

## Current known gaps

- Correct the starter's collection mappings to `altdss.Line` and `altdss.LineCode` using the pinned 0.2.4 source. [Catalog audit](../audits/line_linecode_schema_audit.md)
- Verify property names and support against pinned sources, especially `epsrmedium`, `repair`, and `linetype`.
- Review defaults and units, especially EPRI C1/C0 text versus Python/engine representation.
- Validate the catalog against `schemas/catalogs/line_linecode_properties.schema.json`.
- Runtime behavior remains untested.

## Deliverable

Update the JSON and audit document together. Summarize fields changed, sources used, unresolved evidence, and whether runtime execution occurred. Do not label source-only work as runtime validated.
