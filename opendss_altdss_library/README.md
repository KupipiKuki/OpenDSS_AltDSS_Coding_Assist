# OpenDSS AltDSS Library Package

**Status** The owner accepted Phase 3B packages 1 through 6, closing the Phase 3 exit gate. Package 6 (Generator) was accepted after independent QA/QC and the architect review, with its two non-blocking findings applied. Phase 4 has started: the fixture source is pinned, the golden format and harness contract are fixed, and package 4.1 delivered byte-verified IEEE 13- and 34-node fixtures plus revision 1 snapshot goldens that passed QA/QC and architect review and are accepted by the owner, freezing both goldens as reference data. Package 4.2 (RegControl catalog) delivered the 35-key wrapper surface, workflow, two standalone examples and a readback matrix, and is accepted by the owner. Package 4.3 delivered the LoadShape catalog and the daily profile golden, and awaits the owner's disposition. The Capacitor schema declarations (O-1) are closed, so no element catalog has undeclared row fields. [Package 4.2 handoff](../docs/handoffs/Phase_4_RegControl_Catalog_Coder_handoff.md) · [Generator audit](../docs/audits/phase3b_generator_audit.md) · [Generator QA/QC report](../docs/audits/phase3b_generator_qaqc.md) · [Generator architect review](../docs/audits/phase3b_generator_architect_audit.md) · [Implementation plan](../docs/implementation_plan.md)
**Target:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5

## Contents

- `manifest.json`: support targets, catalog paths, validation state, phase status, and next actions
- `skill.md`: instructions for agents using or extending the library
- `schemas/records/`: reusable evidence, property, API, example, and issue record schemas
- `schemas/catalogs/`: manifest and catalog schemas
- `references/`: source catalogs and reference materials, including the shared [source index](references/sources.json)
- `references/lines/`: Line and LineCode property catalog (Phase 2 remediated)
- [AltDSS-Python API catalog](references/altdss_python_api.json) (99 class records) and [DSS C-API engine catalog](references/dss_capi.json) (119 records)
- [Source index](references/sources.json) shared by catalogs and examples
- [Example catalog](references/examples.json) with 14 `Observed-working` records
- [Line/LineCode workflow guide](../docs/workflows/line_linecode.md) and [example files](examples/line_linecode/)
- [Line geometry and conductor catalog](references/lines/line_geometry_wires_properties.json), [workflow](../docs/workflows/line_geometry_wires.md), and [runtime matrix](../docs/audits/phase3b_line_geometry_wires_readback.json)
- [Circuit and Vsource catalog](references/circuit/vsource_properties.json), [workflow](../docs/workflows/circuit_vsource.md), and [runtime matrix](../docs/audits/phase3b_circuit_vsource_readback.json)
- [Transformer and XfmrCode catalog](references/transformers/transformer_properties.json), [workflow](../docs/workflows/transformer.md), and [runtime matrix](../docs/audits/phase3b_transformer_readback.json)
- [Load catalog](references/loads/load_properties.json), [workflow](../docs/workflows/load.md), and [runtime matrix](../docs/audits/phase3b_load_readback.json)
- [Capacitor catalog](references/capacitors/capacitor_properties.json), [workflow](../docs/workflows/capacitor.md), and [runtime matrix](../docs/audits/phase3b_capacitor_readback.json)
- [Generator catalog](references/generators/generator_properties.json), [workflow](../docs/workflows/generator.md), and [runtime matrix](../docs/audits/phase3b_generator_readback.json)
- `tools/`: validation harness — [requirements-validation.txt](tools/requirements-validation.txt), [validate_catalogs.py](tools/validate_catalogs.py), [run_examples.py](tools/run_examples.py), [build_altdss_api_catalog.py](tools/build_altdss_api_catalog.py)
- `tools/archive/` and `references/lines/*legacy.json`: retained historical extraction artifacts, not active sources

## Validation

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_transformer.py
python opendss_altdss_library/tools/readback_load.py
python opendss_altdss_library/tools/readback_capacitor.py
python opendss_altdss_library/tools/readback_generator.py
```

Three catalogs remain empty pending later phases (`opendss_objects`, `python_interface_comparison`, `troubleshooting`). See the [Phase 3A audit](../docs/audits/phase3a_api_catalogs_audit.md), [Line/LineCode audit](../docs/audits/line_linecode_schema_audit.md), [independent QA/QC report](../docs/audits/line_linecode_phase2_qaqc.md), and [implementation plan](../docs/implementation_plan.md).
