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
- [Circuit and Vsource workflow](docs/workflows/circuit_vsource.md) with the [package audit](docs/audits/phase3b_circuit_vsource_audit.md), [QA/QC report](docs/audits/phase3b_circuit_vsource_qaqc.md), and [architect/auditor review](docs/audits/phase3b_circuit_vsource_architect_audit.md)
- [Transformer and XfmrCode workflow](docs/workflows/transformer.md) with the [package audit](docs/audits/phase3b_transformer_audit.md), [QA/QC report](docs/audits/phase3b_transformer_qaqc.md), and [architect/auditor review](docs/audits/phase3b_transformer_architect_audit.md)
- [Line and LineCode audit](docs/audits/line_linecode_schema_audit.md) and [independent QA/QC report](docs/audits/line_linecode_phase2_qaqc.md)
- [Line and LineCode coder handoff](docs/handoffs/Line_LineCode_Coder_handoff.md) and [QA/QC handoff](docs/handoffs/Line_LineCode_QAQC_handoff.md)

The library targets AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. **Phase 2 is complete and merged:** the Line/LineCode package passed independent QA/QC, both workflow examples are recorded `Observed-working` from a harness run on the pinned stack, and the schema/example harness is committed under `opendss_altdss_library/tools/`.

Phase 3A delivered 99 AltDSS-Python class records and the initial DSS C-API engine catalog. The owner accepted Phase 3B packages 1 and 2. Package 3 covers two- and three-winding Transformer and XfmrCode models; independent QA/QC and the architect review passed, with one broken citation corrected. Owner disposition precedes package 4. The pinned stack passes 12 schema pairs and eight catalogued examples. Phase 4 will record golden results for the IEEE 13- and 34-node fixtures. [Package 3 QA/QC report](docs/audits/phase3b_transformer_qaqc.md) · [Architect/auditor review](docs/audits/phase3b_transformer_architect_audit.md) · [Implementation plan](docs/implementation_plan.md)
