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
- [Load workflow](docs/workflows/load.md) with the [package audit](docs/audits/phase3b_load_audit.md) and [QA/QC handoff](docs/handoffs/Phase_3B_Load_QAQC_handoff.md)
- [Capacitor workflow](docs/workflows/capacitor.md) with the [package audit](docs/audits/phase3b_capacitor_audit.md) and [QA/QC handoff](docs/handoffs/Phase_3B_Capacitor_QAQC_handoff.md)
- [Generator workflow](docs/workflows/generator.md) with the [package audit](docs/audits/phase3b_generator_audit.md) and [QA/QC handoff](docs/handoffs/Phase_3B_Generator_QAQC_handoff.md)
- [Line and LineCode audit](docs/audits/line_linecode_schema_audit.md) and [independent QA/QC report](docs/audits/line_linecode_phase2_qaqc.md)
- [Line and LineCode coder handoff](docs/handoffs/Line_LineCode_Coder_handoff.md) and [QA/QC handoff](docs/handoffs/Line_LineCode_QAQC_handoff.md)

The library targets AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. **Phase 2 is complete and merged:** the Line/LineCode package passed independent QA/QC, both workflow examples are recorded `Observed-working` from a harness run on the pinned stack, and the schema/example harness is committed under `opendss_altdss_library/tools/`.

Phase 3 delivered 99 AltDSS-Python class records, the DSS C-API engine catalog, and six accepted element packages. [Implementation plan](docs/implementation_plan.md) · [Generator QA/QC handoff](docs/handoffs/Phase_3B_Generator_QAQC_handoff.md)

Phase 4 delivered two IEEE snapshots, the IEEE 13 daily profile, RegControl and LoadShape catalogs, and a cross-interface comparison. AltDSS-Python, DSS-Python, and OpenDSSDirect.py agree on their shared DSS C-API 0.14.5 engine. The pinned stack passed 18 schema checks, 19 examples, and all three fixture-to-golden checks. Package 4.5 adds the 16-record troubleshooting catalog and exit checklist and is accepted by the owner, which **closes the Phase 4 stop gate**: every gate item maps to a reproducible command and a recorded artifact. Phase 5 has begun: the thin object index covers all 24 classes — the 16 catalogued and the 8 deliberately deferred — with every count re-derived from the catalog it points at, and the retrieval tool is in progress. [Phase 4 design](docs/phase_4/README.md) · [Troubleshooting index](docs/workflows/troubleshooting.md) · [Exit checklist](docs/phase_4/exit_checklist.md) · [Build audit](docs/audits/phase4_exit_audit.md)
