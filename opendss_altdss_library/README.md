# OpenDSS AltDSS Library Package

**Status:** Phase 3A API and engine catalog QA/QC passed with findings. The corrections are applied. [Finding disposition](../docs/audits/phase3a_api_catalogs_audit.md#independent-qaqc-disposition) · [Implementation plan](../docs/implementation_plan.md)
**Target:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5

## Contents

- `manifest.json`: support targets, catalog paths, validation state, phase status, and next actions
- `skill.md`: instructions for agents using or extending the library
- `schemas/records/`: reusable evidence, property, API, example, and issue record schemas
- `schemas/catalogs/`: manifest and catalog schemas
- `references/`: source catalogs and reference materials, including the shared [source index](references/sources.json)
- `references/lines/`: Line and LineCode property catalog (Phase 2 remediated)
- [AltDSS-Python API catalog](references/altdss_python_api.json) (99 class records) and [DSS C-API engine catalog](references/dss_capi.json) (26 records)
- [Source index](references/sources.json) shared by catalogs and examples
- [Example catalog](references/examples.json) with two `Observed-working` Line/LineCode records
- [Line/LineCode workflow guide](../docs/workflows/line_linecode.md) and [example files](examples/line_linecode/)
- `tools/`: validation harness — [requirements-validation.txt](tools/requirements-validation.txt), [validate_catalogs.py](tools/validate_catalogs.py), [run_examples.py](tools/run_examples.py), [build_altdss_api_catalog.py](tools/build_altdss_api_catalog.py)
- `tools/archive/` and `references/lines/*legacy.json`: retained historical extraction artifacts, not active sources

## Validation

```powershell
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
```

Three catalogs remain empty pending later phases (`opendss_objects`, `python_interface_comparison`, `troubleshooting`). See the [Phase 3A audit](../docs/audits/phase3a_api_catalogs_audit.md), [Line/LineCode audit](../docs/audits/line_linecode_schema_audit.md), [independent QA/QC report](../docs/audits/line_linecode_phase2_qaqc.md), and [implementation plan](../docs/implementation_plan.md).
