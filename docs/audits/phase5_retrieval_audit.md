# Phase 5.2 retrieval tool build audit

- **Validation date** 2026-11-23
- **Inputs revision** `02fe261e87018d1287a64af21ef9ffc92369a2d5` on `wp/phase5`
- **Result** Coder validation passed. [Coder handoff](../handoffs/Phase_5_Retrieval_Tool_Coder_handoff.md) · [Retrieval workflow](../workflows/retrieval.md)

Validation used Windows 11 AMD64 and Python 3.14.6. The schema, example, and fixture regressions used jsonschema 4.26.0, AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5, and OpenDSSDirect.py 0.9.4. Retrieval and checker probes also ran with `python -S`, which skips site-package setup.

## Measured corpus

| Catalog | Records |
| --- | ---: |
| Sources | 132 |
| Examples | 19 |
| AltDSS API | 99 class records, with 180 methods and 1,094 properties |
| DSS C-API | 144 |
| Element property catalogs | 16 class records and 461 property rows across nine files |
| Object index | 24 |
| Python interface comparison | 13 |
| Troubleshooting | 16 |
| Fixtures | 2 |

The 926 addressable records include the 461 element property rows. They span 17 JSON files. Flattening the nested API methods and properties yields 2,200 searchable records. These are measured values. The handoff's ten-file count differs from the committed data.

## Query verification

~~~powershell
$search = 'opendss_altdss_library/tools/search_catalogs.py'
python -S -B $search --symbol TapNumber
python -S -B $search --symbol Conductors
python -S -B $search --class PVSystem
python -S -B $search "manual tap static" --class RegControl --evidence observed-working
python -S -B $search "cable modeling technote" --version 0.14.5
python -S -B $search --symbol IRegControl --class regcontrol --json
~~~

| Query | Observed result |
| --- | --- |
| `TapNumber` | Three explicitly labeled alias hits at the RegControl element property, AltDSS property, and engine record. The committed names are `tapnum`, `TapNum`, and `Immediate tap readback and bounds`. The alias cites the classic `TapNumber` accessor. |
| `Conductors` | Exactly two top-level hits, `LineGeometry.wires` and `Line.wires`. Each says `dss=wires python=Conductors` and carries its generated API property under `related_api` in JSON. |
| Class `PVSystem` | One deferred object record with its EPRI URL and a null property catalog. |
| `manual tap static` | The observed-working `ts-controlled-solve-retaps` issue, with the repository path `docs/workflows/regcontrol.md` printed as recorded. The handoff's phrase `tap reverts after solve` returned 1 because the evidence does not contain `reverts`. |
| `cable modeling technote` | `TSData` and `epri-tsdata-cable-modeling` survived the version filter with `version=unstated`. |
| `IRegControl` | The collection class resolved through the RegControl class filter. A separate exact query for `RegControl` also surfaced the object wrapper. |

`--class NotAClassy` returned 2 with `unknown class 'NotAClassy'. Did you mean AutoTrans, CNData, LoadShape?`. An unknown flag and a missing examples catalog in a disposable copy also returned 2. A query for `no_such_catalog_concept_qa` returned 1 with an empty JSON hit list. The six successful commands returned 0.

Two separate invocations of `python -S -B $search --symbol Conductors --json` produced byte-identical output. SHA-256 was `fb7bccf650fb8436370f15fa0425f0a28c2b79215902a7d8aebd2f06b31f9570`. Parsed hit keys were already in `(catalog, record_id, field)` order.

## Object index check

`python -S -B $search --check` reported `Object index check: PASS` and exited 0 on the committed index. The check reads the accepted property files, engine namespace records, example tags, fixture scripts, and the snapshot and daily golden captures.

In a disposable copy, I manually changed RegControl's `property_catalog.property_row_count` from 35 to 36 and ran the same command. It exited 1 with:

~~~text
RegControl.property_catalog.property_row_count: recorded 36, derived 35
~~~

Restoring the exact file bytes returned the check to PASS. A separate probe changed the RegControl engine count and removed IEEE 13 daily from its fixture usage. The check reported both fields in the same run. The accepted index was read-only throughout.

## Regression checks

~~~powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
git diff --check
~~~

All 18 schema pairs, 19 examples, and three fixture runs passed. Catalogs, schemas, examples, fixtures and goldens, validation requirements, plan, and manifest match the inputs revision.
