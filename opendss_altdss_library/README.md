# OpenDSS AltDSS Library Package

**Status** The six Phase 3 element packages and Phase 4 packages 4.1–4.5 are accepted. The Phase 4 exit package adds 16 confirmed troubleshooting records and the exit checklist and is accepted by the owner, closing the Phase 4 stop gate. Phase 5.1 delivered the thin object index over all 24 classes and is accepted; Phase 5.2 adds the retrieval tool. [Object index](references/opendss_objects.json) · [Exit checklist](../docs/phase_4/exit_checklist.md) · [Build audit](../docs/audits/phase4_exit_audit.md) · [Implementation plan](../docs/implementation_plan.md)

**Target** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5, and OpenDSSDirect.py 0.9.4 for cross-interface checks.

## Contents

- `manifest.json`: support targets, catalog paths, validation state, phase status, and next actions
- `skill.md`: instructions for agents using or extending the library
- `schemas/records/`: reusable evidence, property, API, example, and issue record schemas
- `schemas/catalogs/`: manifest and catalog schemas
- `references/`: source catalogs and reference materials, including the shared [source index](references/sources.json)
- [OpenDSS object index](references/opendss_objects.json) with 16 catalogued and 8 deferred classes, plus the [lookup workflow](../docs/workflows/object_index.md)
- [Catalog retrieval tool](tools/search_catalogs.py) for symbol and concept searches with citations, plus the [retrieval workflow](../docs/workflows/retrieval.md)
- `references/lines/`: Line and LineCode property catalog (Phase 2 remediated)
- [AltDSS-Python API catalog](references/altdss_python_api.json) (99 class records) and [DSS C-API engine catalog](references/dss_capi.json) (144 records)
- [Source index](references/sources.json) shared by catalogs and examples
- [Example catalog](references/examples.json) with 19 `Observed-working` records
- [Line/LineCode workflow guide](../docs/workflows/line_linecode.md) and [example files](examples/line_linecode/)
- [Line geometry and conductor catalog](references/lines/line_geometry_wires_properties.json), [workflow](../docs/workflows/line_geometry_wires.md), and [runtime matrix](../docs/audits/phase3b_line_geometry_wires_readback.json)
- [Circuit and Vsource catalog](references/circuit/vsource_properties.json), [workflow](../docs/workflows/circuit_vsource.md), and [runtime matrix](../docs/audits/phase3b_circuit_vsource_readback.json)
- [Transformer and XfmrCode catalog](references/transformers/transformer_properties.json), [workflow](../docs/workflows/transformer.md), and [runtime matrix](../docs/audits/phase3b_transformer_readback.json)
- [Load catalog](references/loads/load_properties.json), [workflow](../docs/workflows/load.md), and [runtime matrix](../docs/audits/phase3b_load_readback.json)
- [Capacitor catalog](references/capacitors/capacitor_properties.json), [workflow](../docs/workflows/capacitor.md), and [runtime matrix](../docs/audits/phase3b_capacitor_readback.json)
- [Generator catalog](references/generators/generator_properties.json), [workflow](../docs/workflows/generator.md), and [runtime matrix](../docs/audits/phase3b_generator_readback.json)
- [RegControl catalog](references/regcontrols/regcontrol_properties.json), [workflow](../docs/workflows/regcontrol.md), and [runtime matrix](../docs/audits/phase4_regcontrol_readback.json)
- [LoadShape catalog](references/loadshapes/loadshape_properties.json), [workflow](../docs/workflows/loadshape.md), and [runtime matrix](../docs/audits/phase4_loadshape_readback.json)
- [Fixture catalog](references/fixtures.json) and [pinned fixture tree](examples/fixtures/) containing the IEEE 13 and IEEE 34 snapshot goldens and the IEEE 13 daily golden
- [Interface comparison catalog](references/python_interface_comparison.json) (13 records), [workflow](../docs/workflows/cross_interface.md), and [comparison report](../docs/audits/phase4_cross_interface_report.json)
- [Troubleshooting catalog](references/troubleshooting.json) (16 confirmed records) and [symptom index](../docs/workflows/troubleshooting.md)
- [Validation requirements](tools/requirements-validation.txt), [schema runner](tools/validate_catalogs.py), [example runner](tools/run_examples.py), [fixture runner](tools/run_fixtures.py), [interface comparison](tools/compare_interfaces.py), and [AltDSS catalog builder](tools/build_altdss_api_catalog.py)
- `tools/archive/` and `references/lines/*legacy.json`: retained historical extraction artifacts, not active sources

## Validation

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/run_fixtures.py
python opendss_altdss_library/tools/compare_interfaces.py
python opendss_altdss_library/tools/readback_transformer.py
python opendss_altdss_library/tools/readback_load.py
python opendss_altdss_library/tools/readback_capacitor.py
python opendss_altdss_library/tools/readback_generator.py
python opendss_altdss_library/tools/readback_regcontrol.py
python opendss_altdss_library/tools/readback_loadshape.py
```

The fixture runner checks recorded goldens. The comparison checks wrapper agreement on the shared DSS C-API engine. Independent numerical validation requires a separate reference. [Phase 4 exit checklist](../docs/phase_4/exit_checklist.md)
