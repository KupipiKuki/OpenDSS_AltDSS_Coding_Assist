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

Phase 3A delivered 99 AltDSS-Python class records and the initial DSS C-API engine catalog. The owner accepted Phase 3B packages 1 through 5. Package 6 (Generator) completes the element implementation sequence and was accepted after independent QA/QC and an architect review, closing the Phase 3 exit gate: all six element packages are accepted. The pinned stack passed 16 schema pairs and 14 catalogued examples. Phase 4 is under way: the IEEE 13- and 34-node fixtures are pinned to `electricdss-tst` @ `3b20839`, the golden format, tolerances and harness contract are fixed in [docs/phase_4/README.md](docs/phase_4/README.md), and package 4.1 (fixture harness and snapshot goldens) is accepted by the owner, which freezes both revision 1 goldens as reference data. Package 4.2 (RegControl catalog) is accepted by the owner. Package 4.3 delivered the LoadShape catalog and the 24-step daily profile golden on `ieee13`, and awaits the owner's disposition after independent QA/QC and the architect review. [Package 4.2 handoff](docs/handoffs/Phase_4_RegControl_Catalog_Coder_handoff.md) · [Generator QA/QC handoff](docs/handoffs/Phase_3B_Generator_QAQC_handoff.md) · [Implementation plan](docs/implementation_plan.md)
