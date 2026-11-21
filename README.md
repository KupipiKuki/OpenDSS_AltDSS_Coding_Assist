# OpenDSS and AltDSS Coding Assistant Library

Evidence-based reference material for OpenDSS models and AltDSS-Python development.

## Project map

- [Implementation plan](docs/implementation_plan.md) — phase state, sequencing, gates, and golden-fixture design
- [Phase 1 scope, inventory, handoff, and external audit](docs/phase_1/README.md)
- [Library package, manifest, skill, and schemas](opendss_altdss_library/README.md)
- [Line and LineCode property catalog](opendss_altdss_library/references/lines/opendss_line_linecode_properties.json)
- [Line and LineCode workflows](docs/workflows/line_linecode.md) and [source and release index](opendss_altdss_library/references/line_linecode_sources.json)
- [Line and LineCode audit](docs/audits/line_linecode_schema_audit.md) and [independent QA/QC report](docs/audits/line_linecode_phase2_qaqc.md)
- [Line and LineCode coder handoff](docs/handoffs/Line_LineCode_Coder_handoff.md) and [QA/QC handoff](docs/handoffs/Line_LineCode_QAQC_handoff.md)

The library targets AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. **Phase 2 is complete and merged:** the Line/LineCode package passed independent QA/QC, both workflow examples are recorded `Observed-working` from a harness run on the pinned stack, and the schema/example harness is committed under `opendss_altdss_library/tools/`.

Next is Phase 3 (API and engine catalogs, then dependency-ordered element packages) and Phase 4, which the owner fixed to require recorded golden results for the IEEE 13- and 34-node fixtures. Phase 3 scope confirmation is the remaining open owner decision. See the [implementation plan](docs/implementation_plan.md).
