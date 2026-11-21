# Phase 3B Line Geometry and Conductor Data Build Audit

- **Date** 2026-11-21
- **Status** Coder verification passed. Independent QA/QC pending.
- **Targets** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5.
- **Scope** LineGeometry, LineSpacing, WireData, CNData, and TSData.

[Property catalog](../../opendss_altdss_library/references/lines/line_geometry_wires_properties.json) · [Schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json) · [Workflow](../workflows/line_geometry_wires.md) · [QA/QC handoff](../handoffs/Phase_3B_LineGeometry_WireData_QAQC_handoff.md)

## Method and coverage

- The property catalog follows the tagged AltDSS-Python `*Properties` creation keywords and includes a separate `name` row for each object. Engine definitions, constructor assignments, and setter code establish version-specific defaults and behavior. Each row cites its sources.
- The generalized schema retains the Line/LineCode field shape, accepts any nonempty element class, and requires property-level citations. The EPRI page field can be null when a standalone page is unavailable, as for TSData.
- The catalog contains 82 rows across five classes. Counts include one object identifier and one `Like` action per class.

| Class | Rows | Regular readbacks |
| --- | ---: | ---: |
| LineGeometry | 15 | 13 |
| LineSpacing | 7 | 6 |
| WireData | 15 | 14 |
| CNData | 23 | 22 |
| TSData | 22 | 21 |
| Total | 82 | 76 |

The shared source index gained 16 entries and now contains 34. The engine catalog gained 19 records and now contains 45. The additions cover the five classes, inherited conductor and cable fields, and their use from Line. Existing catalog rows are retained. [Source index](../../opendss_altdss_library/references/sources.json) · [Engine catalog](../../opendss_altdss_library/references/dss_capi.json)

## Checks performed

- The repository catalog validator passed all **10 schema pairs**. The example harness passed **all four examples**, including both new geometry/spacing examples.
- The property matrix used a fresh virtual environment populated from the local audited package set. Package metadata matched the required pins. The run used Windows 11 AMD64, Python 3.14.6, and jsonschema 4.26.0. The matrix records 76 readbacks, five `Like` actions without a getter, and one unavailable scalar getter.
- In the overhead probe, both paths solved, retained three phases from four conductor positions, and gave a length of 1 km. Separate CNData and TSData spacing probes also solved, and each read back three typed conductors and a 3×3 resistance matrix. The probe also checked the spacing unit reset and selected inherited conductor defaults derived by setters.
- A same-frequency `rho` edit changed the exposed value but left the resistance matrix cached at 60 Hz. The next solve at 50 Hz changed the matrix. [Pinned cache](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L1905-L1938)

[Recorded matrix](phase3b_line_geometry_wires_readback.json) · [Readback tool](../../opendss_altdss_library/tools/readback_line_geometry_wires.py)

## Limits and open items

- `LineGeometry.Units` is array-backed in the engine. The bare object has no slots, and a targeted probe after allocating slots raised `ValueError` through the scalar Python accessor. The matrix records this cell as unavailable and the workflow uses the spacing unit or explicit DSS per-conductor units. [Engine field](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineGeometry.pas#L301-L305) · [Pinned getter](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/LineGeometry.py#L164-L177)
- Constructor sentinel values are recorded in the matrix. Catalog defaults remain unspecified where a sentinel would be unusable input.
- The examples use synthetic parameters and homogeneous cable constructions for the cable probes. They establish the selected creation, solve, and readback paths. Engineering accuracy, mixed cable cases, and feeder regression coverage remain outside this check.
- Independent QA/QC will verify property coverage, source references, engine scope, and reproducibility.
