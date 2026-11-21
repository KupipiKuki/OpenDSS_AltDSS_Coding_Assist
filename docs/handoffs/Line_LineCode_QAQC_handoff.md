# QA/QC Handoff: Line and LineCode Catalog

## Review target

Review `opendss_altdss_library/references/lines/opendss_line_linecode_properties.json` against the project charter, manifest, package schemas, source inventory, and coder handoff.

## Audit checklist

- Confirm each property exists in the cited EPRI reference or release-tagged target source.
- Check types, defaults, units, and descriptions; flag claims that combine sources without showing which source supports each field.
- Verify collection names against AltDSS-Python 0.2.4. The tagged source declares `altdss.Line` and `altdss.LineCode`. Flag the lower-case mappings in the Phase 1 starter until Phase 2 corrects them. [Tagged collection definitions](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Obj.py#L170-L184)
- Check unconditional and conditional creation requirements.
- Confirm version metadata and evidence labels do not imply an unpinned current EPRI release.
- Confirm unsupported target properties are marked and excluded from generation.
- Validate against `schemas/catalogs/line_linecode_properties.schema.json`.
- Report source review and runtime execution as separate outcomes.

## Report format

- **STATUS:** PASS / PASS WITH FINDINGS / FAIL
- **PROPERTY FINDINGS:** missing, unsupported, duplicate, or questionable properties
- **EVIDENCE FINDINGS:** source, version, type, default, or unit problems
- **REQUIREMENT FINDINGS:** unconditional/conditional requirements and mappings
- **SCHEMA RESULT:** pass / fail / not run
- **RUNTIME RESULT:** pass / fail / not run, with environment if run
- **REQUIRED CORRECTIONS:** specific changes and supporting sources

Do not infer engine behavior from an EPRI page or treat schema validity as runtime validation.
