# OpenDSS and AltDSS Coding Assistant Library

Evidence-based reference material for OpenDSS models and AltDSS-Python development.

## Project map

- [Implementation plan](docs/implementation_plan.md) — phase state, sequencing, gates, and golden-fixture design
- [Phase 1 scope, inventory, handoff, and external audit](docs/phase_1/README.md)
- [Library package, manifest, skill, and schemas](opendss_altdss_library/README.md)
- [Line and LineCode property catalog](opendss_altdss_library/references/lines/opendss_line_linecode_properties.json)
- [Line and LineCode workflows](docs/workflows/line_linecode.md) and [source and release index](opendss_altdss_library/references/sources.json)
- [Line geometry and conductor workflow](docs/workflows/line_geometry_wires.md) with the [package audit](docs/audits/phase3b_line_geometry_wires_audit.md), [QA/QC report](docs/audits/phase3b_line_geometry_wires_qaqc.md), and [architect/auditor review](docs/audits/phase3b_line_geometry_wires_architect_audit.md)
- [AltDSS-Python API catalog](opendss_altdss_library/references/altdss_python_api.json) and [DSS C-API engine catalog](opendss_altdss_library/references/dss_capi.json) with the [Phase 3A audit](docs/audits/phase3a_api_catalogs_audit.md)
- [Line and LineCode audit](docs/audits/line_linecode_schema_audit.md) and [independent QA/QC report](docs/audits/line_linecode_phase2_qaqc.md)
- [Line and LineCode coder handoff](docs/handoffs/Line_LineCode_Coder_handoff.md) and [QA/QC handoff](docs/handoffs/Line_LineCode_QAQC_handoff.md)

The library targets AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. **Phase 2 is complete and merged:** the Line/LineCode package passed independent QA/QC, both workflow examples are recorded `Observed-working` from a harness run on the pinned stack, and the schema/example harness is committed under `opendss_altdss_library/tools/`.

Phase 3A delivered 99 AltDSS-Python class records and the initial DSS C-API engine catalog. Independent QA/QC passed with findings, and the corrections are applied. Phase 3B package 1 adds line geometry, spacing, and conductor data with runtime readbacks on the pinned stack; independent QA/QC found no blocking issues, and architect/auditor review applied one optional citation correction. Owner disposition precedes package 2. Phase 4 requires recorded golden results for the IEEE 13- and 34-node fixtures. [Phase 3B QA/QC handoff](docs/handoffs/Phase_3B_LineGeometry_WireData_QAQC_handoff.md) · [Architect/auditor review](docs/audits/phase3b_line_geometry_wires_architect_audit.md) · [Implementation plan](docs/implementation_plan.md)
