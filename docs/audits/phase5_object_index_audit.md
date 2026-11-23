# Phase 5.1 object index build audit

- **Validation date** 2026-11-22
- **Inputs revision** `5c7797e29d6d4e24e9ad4aa7b3c82d387e6df0c1` on `wp/phase5`
- **Result** Coder validation passed. The index has 16 catalogued and eight deferred classes. [Coder handoff](../handoffs/Phase_5_Object_Index_Coder_handoff.md) · [Index](../../opendss_altdss_library/references/opendss_objects.json) · [Lookup workflow](../workflows/object_index.md)

## Re-derivation

Read `references/opendss_objects.json` under the library root. For each linked property file, count its top-level records and sum the lengths of their `properties` arrays. This gives the same file-level counts to every class that shares the file. Count exact `namespace_or_type` matches in `dss_capi.json` for each listed namespace. For examples, select every row in `examples.json` whose `object_classes` contains the class. A deferred class has no property file to count.

| Class | Property file (records / rows) | Engine namespaces (records) | Examples | Fixture usage |
| --- | --- | --- | ---: | --- |
| AutoTrans | Deferred | 0 | 0 | None |
| Capacitor | `references/capacitors/capacitor_properties.json` (1 / 22) | `Capacitor` (14) | 3 | Both snapshots and IEEE 13 daily |
| CapControl | Deferred | 0 | 0 | None |
| Circuit | `references/circuit/vsource_properties.json` (2 / 37) | `Circuit` (1) | 18 | Both snapshots and IEEE 13 daily |
| CNData | `references/lines/line_geometry_wires_properties.json` (5 / 82) | `CNData`, `ConductorData`, `CableData` (5) | 0 | None |
| ExpControl | Deferred | 0 | 0 | None |
| GenDispatcher | Deferred | 0 | 0 | None |
| Generator | `references/generators/generator_properties.json` (1 / 49) | `Generator` (17) | 2 | None |
| GrowthShape | Deferred | 0 | 0 | None |
| InvControl | Deferred | 0 | 0 | None |
| Line | `references/lines/opendss_line_linecode_properties.json` (2 / 67) | `Line`, `TLineObj`, `TLineProp` (17) | 6 | Both snapshots and IEEE 13 daily |
| LineCode | `references/lines/opendss_line_linecode_properties.json` (2 / 67) | `TLineCodeObj`, `TLineCodeProp`, `TLineCode` (10) | 2 | Both snapshots and IEEE 13 daily |
| LineGeometry | `references/lines/line_geometry_wires_properties.json` (5 / 82) | `LineGeometry` (8) | 2 | None |
| LineSpacing | `references/lines/line_geometry_wires_properties.json` (5 / 82) | `LineSpacing` (2) | 2 | None |
| Load | `references/loads/load_properties.json` (1 / 43) | `Load` (13) | 11 | Both snapshots and IEEE 13 daily |
| LoadShape | `references/loadshapes/loadshape_properties.json` (1 / 22) | `LoadShape` (8) | 2 | ieee13 daily |
| PVSystem | Deferred | 0 | 0 | None |
| RegControl | `references/regcontrols/regcontrol_properties.json` (1 / 35) | `RegControl` (15) | 3 | Both snapshots and IEEE 13 daily |
| Storage | Deferred | 0 | 0 | None |
| Transformer | `references/transformers/transformer_properties.json` (2 / 104) | `Transformer` (12) | 5 | Both snapshots and IEEE 13 daily |
| TSData | `references/lines/line_geometry_wires_properties.json` (5 / 82) | `TSData`, `ConductorData`, `CableData` (5) | 0 | None |
| Vsource | `references/circuit/vsource_properties.json` (2 / 37) | `Vsource`, `TVsourceProp` (10) | 3 | Both snapshots and IEEE 13 daily |
| WireData | `references/lines/line_geometry_wires_properties.json` (5 / 82) | `WireData`, `ConductorData` (4) | 2 | None |
| XfmrCode | `references/transformers/transformer_properties.json` (2 / 104) | `XfmrCode` (4) | 1 | None |

The Line and LineCode engine counts include the class-specific internal namespaces. The public `LineCode` namespace has zero records, so the index lists the three internal namespaces that resolve. The conductor entries include `ConductorData` for WireData, CNData and TSData, and `CableData` for CNData and TSData. Vsource includes `TVsourceProp`. Shared circuit and element base namespaces stay in the engine catalog, as does the `Load.Daily` retrieval key. [Engine catalog](../../opendss_altdss_library/references/dss_capi.json)

The AltDSS API pointers resolve by `module_path` and `class_name`. The pinned runtime exposed the corresponding context accessors for all 24 rows. Circuit uses `ctx.Commands` and the `altdss.AltDSS` context record. Its interface pointer is null. CNData and TSData have runtime readbacks and zero entries tagged for those classes in `examples.json`. [AltDSS API catalog](../../opendss_altdss_library/references/altdss_python_api.json) · [Conductor readbacks](phase3b_line_geometry_wires_readback.json)

Fixture usage came from the snapshot `elements` maps and the daily `peak_step.elements` map. Both upstream entry scripts create a Circuit and assign LineCode data, so both classes are listed for all three runs. The daily scenario inherits the IEEE 13 input script and assigns LoadShape through `daily.shape.assignment` in `fixtures.json`. This accounts for the daily use of RegControl and the other IEEE 13 circuit elements. [Fixture catalog](../../opendss_altdss_library/references/fixtures.json) · [Fixture tree](../../opendss_altdss_library/examples/fixtures/)

All workflow, readback, and source references resolve. The source index preserves its 127 initial records and adds five EPRI pointers for classes without an existing EPRI entry. The direct numbered and unnumbered TSData pages were unavailable during the check. The fetched cable-modeling technote has a TSData section, so it supplies that pointer. The GenDispatcher class-page check produced no usable class page, and the existing pinned implementation pointers are retained. CapControl and RegControl use their previously verified class URLs. [TSData technote](https://opendss.epri.com/CableModelinginOpenDSS.html) · [PVSystem](https://opendss.epri.com/PVSystem.html) · [Storage](https://opendss.epri.com/Storage.html) · [InvControl](https://opendss.epri.com/InvControl.html) · [ExpControl](https://opendss.epri.com/ExpControl.html)

## Commands and results

Run from the repository root in the pinned validation environment. Validation used Windows 11 AMD64, Python 3.14.6, jsonschema 4.26.0, AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5, and OpenDSSDirect.py 0.9.4.

~~~powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
git diff --check
~~~

All 18 schema pairs, 19 examples, and three fixture runs passed. The object index uses the existing schema pairing. The schema requires each of the 24 class and status pairs exactly once. A reversed index still validated, and a duplicate class with different notes failed. The document and nested pointer objects reject additional fields.

The injected `properties` array failed with `Additional properties are not allowed ('properties' was unexpected)`. Adding top-level `name`, `data_type`, `units`, or `description`, or a nested `description`, also failed. The following reproduces the `properties` check against the registered schema.

~~~powershell
@'
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker

root = Path("opendss_altdss_library").resolve()
sys.path.insert(0, str(root / "tools"))
from validate_catalogs import build_registry

schema = root / "schemas/catalogs/opendss_objects.schema.json"
index = json.loads((root / "references/opendss_objects.json").read_bytes())
validator = Draft202012Validator(
    {"$id": schema.as_uri(), **json.loads(schema.read_bytes())},
    registry=build_registry(root), format_checker=FormatChecker(),
)
validator.validate(index)
index[0]["properties"] = []
print(next(error.message for error in validator.iter_errors(index)
           if error.validator == "additionalProperties"))
'@ | python -B -
~~~

The property catalogs, existing API and engine records, examples, fixture and golden files, tools, other schemas, plan, and manifest match the inputs revision. Package 5.2 owns the retrieval tool. Package 5.3 owns the release record.
