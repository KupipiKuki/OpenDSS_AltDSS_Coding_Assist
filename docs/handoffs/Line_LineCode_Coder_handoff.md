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

## QA/QC outcome and follow-up

- The first remediation pass corrected the collection names and selected defaults, added exact Python creation keywords, and documented the complete engine specification sets. [Catalog audit](../audits/line_linecode_schema_audit.md)
- Independent QA/QC passed with findings. The catalog now reflects both requested description corrections. Record remaining optional property citations as related records are curated. [Finding disposition](../audits/line_linecode_schema_audit.md#independent-qaqc-disposition)
- QA/QC observed an initial `LineCode.Repair` readback of `0.0`. Broader fixture and edit coverage remain for later validation. [Runtime evidence](../audits/line_linecode_phase2_qaqc.md#runtime-result-pass)

## Deliverable

Update the JSON and audit document together. Summarize fields changed, sources used, unresolved evidence, and whether runtime execution occurred. Do not label source-only work as runtime validated.
