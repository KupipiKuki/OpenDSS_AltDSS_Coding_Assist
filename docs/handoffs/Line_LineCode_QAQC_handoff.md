# QA/QC Handoff: Line and LineCode Catalog

## Review target

Mistral is the proposed independent QA/QC reviewer, Codex is the primary coder, and the project owner decides which findings must be resolved before merge.

Review the Phase 2 working revision against Phase 1 baseline `3263daa`. Read the catalog and schema, then inspect the tagged sources cited in the catalog and audit. Record the reviewed branch and commit or working tree state in your report. [Catalog](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties.json) · [Schema](../../opendss_altdss_library/schemas/catalogs/line_linecode_properties.schema.json) · [Audit](../audits/line_linecode_schema_audit.md)

## Audit checklist

- Confirm each property exists in the cited EPRI reference or release-tagged target source.
- Check types, defaults, units, and descriptions; flag claims that combine sources without showing which source supports each field.
- Confirm the corrected collection mappings `altdss.Line` and `altdss.LineCode` and the exact creation keyword casing. Confirm `Conductors` is the Python keyword for the DSS `wires` row. [Tagged collection definitions](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Obj.py#L170-L184)
- Compare the complete engine specification sets to the catalog. Check that the catalog distinguishes them from minimum command or Python constructor inputs.
- Check the C1/C0 farad-to-nanofarad scaling, `Switch` side effects, initial ratings, circuit-dependent frequency defaults, and treatment of `LineCode.Repair` and `Line.epsrmedium`.
- Confirm version metadata and evidence labels do not imply an unpinned current EPRI release.
- Confirm unsupported target properties are marked and excluded from generation.
- Validate against `schemas/catalogs/line_linecode_properties.schema.json`.
- Report source review and runtime execution as separate outcomes.

## Report format

Save the report as `docs/audits/line_linecode_phase2_qaqc.md`. For each finding, include the exact property or field, the source URL and tag, and the requested correction.

- **STATUS:** PASS / PASS WITH FINDINGS / FAIL
- **PROPERTY FINDINGS:** missing, unsupported, duplicate, or questionable properties
- **EVIDENCE FINDINGS:** source, version, type, default, or unit problems
- **REQUIREMENT FINDINGS:** unconditional/conditional requirements and mappings
- **SCHEMA RESULT:** pass / fail / not run
- **RUNTIME RESULT:** pass / fail / not run, with environment if run
- **REQUIRED CORRECTIONS:** specific changes and supporting sources

Do not infer engine behavior from an EPRI page or treat schema validity as runtime validation.
