# Phase 5 Package 5.1 — Thin object index (coder handoff)

**Issued** 2026-11-22 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** the closed Phase 4 exit (decision 21). **Scope authority** decision 22: `opendss_objects` is a **thin index**, not a second property catalog.

## Goal

Fill the last empty catalog with a *pointer* file: one record per object class, saying where that class is documented, catalogued, exemplified and validated, with counts but **no property rows**. Phase 4 delivered sixteen property catalogs. This package makes them reachable as an index without copying a single property into a second place where it can rot.

The governing rule, which the acceptance criteria test rather than assume: **the element catalogs are the only place a property, its type, its units or its description may live. This catalog must not restate any of them.**

## The existing schema is the wrong shape and must be replaced

`schemas/catalogs/opendss_objects.schema.json` currently *requires* `element_class`, `epri_doc_url`, `properties`, and `evidence_label`, where `properties` is an array of `{name, data_type, default_value, units, description, evidence_label}`. That is the thick shape — a full duplicate of the property catalogs under a second schema, which is exactly what decision 22 declines.

Replace that schema with the thin record below. This is safe and is the only schema change this package may make: the catalog is empty, and `validate_catalogs.py` is its sole consumer (checked — no record schema, tool or document `$ref`s it). Keep the file path and the pairing so the pair count stays **18/18**.

A record that carries a `properties` array, or any property name/type/units/description fields, must **fail** validation. That is the mechanical guarantee that the index stays thin.

## The thin record

```json
{
  "element_class": "RegControl",
  "status": "catalogued",
  "evidence_label": "Observed-working",
  "property_catalog": {
    "path": "references/regcontrols/regcontrol_properties.json",
    "record_count": 1,
    "property_row_count": 35
  },
  "workflow_path": "docs/workflows/regcontrol.md",
  "altdss": {
    "context_accessor": "ctx.RegControl",
    "class_record": "altdss.RegControl",
    "interface_record": "altdss.RegControl:IRegControl"
  },
  "engine": { "namespaces": ["RegControl"], "record_count": 15 },
  "example_ids": ["regcontrol-controlled-voltage-altdss", "regcontrol-fixed-tap-voltage-dss", "ieee13-snapshot-cross-interface"],
  "readback_evidence": ["docs/audits/phase4_regcontrol_readback.json"],
  "fixture_usage": ["ieee13 snapshot", "ieee34 snapshot"],
  "source_ids": ["epri-regcontrol-element", "epri-regcontrol-properties", "capi-release-0145"],
  "epri_doc_url": "https://opendss.epri.com/RegControl.html",
  "notes": []
}
```

Field rules:

- `element_class` — the DSS class name as it is spelled in a `New` command and in the catalogs' own `element_class`. Exactly one record per class; duplicates fail.
- `status` — `catalogued` or `deferred`. No third value.
- `property_catalog` — `null` for deferred classes; otherwise the path plus **two measured counts**: `record_count` (entries in that file) and `property_row_count` (sum of the `properties` arrays across those entries).
- `workflow_path` — `null` when no workflow page covers the class. `docs/workflows/cross_interface.md` and `troubleshooting.md` are not per-class pages; do not attach them.
- `altdss` — `null` for deferred classes with no wrapper class. `class_record` is `altdss.<Class>` and `interface_record` is `altdss.<Class>:I<Class>`, verified against `references/altdss_python_api.json` `class_name`/`module_path`, not guessed. Both are pointers into that catalog; do not copy method or property rows.
- `engine.namespaces` — the entries in `references/dss_capi.json` whose `namespace_or_type` covers this class. `engine.record_count` is the number of records matching those namespaces, measured.
- `example_ids` — every `example_id` in `references/examples.json` whose `object_classes` contains this class. Copy them from the catalog; do not invent or re-assign.
- `readback_evidence` — the runtime matrix or matrices that exercise the class. `[]` when none.
- `fixture_usage` — which pinned runs use the class: `"ieee13 snapshot"`, `"ieee34 snapshot"`, `"ieee13 daily"`. `[]` when none.
- `source_ids` — ids that exist in `references/sources.json`. **Do not invent source records for classes already covered**; only add one when a class has no EPRI page recorded, and then only with a URL you fetched and an access date.
- `epri_doc_url` — must equal the `url` of one of your `source_ids`, or be `null` when the project has recorded that no page exists. Probe both name forms first (`CapControl.html` is 404 while `CapControl1.html` is live, and the reverse holds for `RegControl`).

## What exists, measured while preparing this handoff

Re-derive every number yourself; these are here so you inherit the layout, not so you can paste it.

| Class | Catalog | Catalog records | `dss_capi` namespace records | Fixture use | Example ids |
|---|---|---|---|---|---|
| Capacitor | `references/capacitors/capacitor_properties.json` | 1 | 14 | yes | 2 + cross-interface |
| Circuit | `references/circuit/vsource_properties.json` | 2 | 1 | – | 18 |
| Generator | `references/generators/generator_properties.json` | 1 | 17 | – | 2 |
| Line | `references/lines/opendss_line_linecode_properties.json` | 2 | 2 | yes | 5 + cross-interface |
| LineCode | same file | 2 | 0 | – | 2 |
| LineGeometry | `references/lines/line_geometry_wires_properties.json` | 5 | 8 | – | 2 |
| LineSpacing | same file | 5 | 2 | – | 2 |
| WireData / CNData / TSData | same file | 5 | 1 each | – | WireData 2, CNData 0, TSData 0 |
| Load | `references/loads/load_properties.json` | 1 | 13 | yes | 10 + cross-interface |
| LoadShape | `references/loadshapes/loadshape_properties.json` | 1 | 8 | daily only | 2 |
| RegControl | `references/regcontrols/regcontrol_properties.json` | 1 | 15 | yes | 2 + cross-interface |
| Transformer | `references/transformers/transformer_properties.json` | 2 | 12 | yes | 4 + cross-interface |
| XfmrCode | same file | 2 | 4 | – | 1 |
| Vsource | `references/circuit/vsource_properties.json` | 2 | 9 | yes | 2 + cross-interface |

Sixteen catalogued classes. `LoadShape` shows no fixture use through the goldens because shapes are not circuit elements: it is assigned by the daily harness to all 15 loads, so its `fixture_usage` is `["ieee13 daily"]` — derive that from `fixtures.json` `daily`, not from the golden `elements` blocks.

Internal type names appear in `dss_capi.json` beside the public ones and are how the engine catalogs some records: `TLineObj` (13), `TLineCodeObj` (8), `TLineProp` (2), `TLineCodeProp` (1), `TLineCode` (1), `ConductorData` (3), `CableData` (1), `TVsourceProp` (1). Attach them to their family where the records are specific to it — for example Line → `["Line", "TLineObj", "TLineProp"]` and LineCode → `["LineCode", "TLineCodeObj", "TLineCodeProp", "TLineCode"]`. **Do not** attach the shared base namespaces (`TPCElement`, `TDSSCktElement`, `TDSSCircuit`, `Solution`, `DSS C-API`) to any element class; they are cross-class and stay reachable through the batch search in package 5.2. `Load.Daily` is a one-record naming quirk in the engine catalog, not a class; leave it unattached and mention it in `Load.notes`.

## The eight deferred classes must be in the index

`CapControl`, `GenDispatcher`, `AutoTrans`, `GrowthShape`, `PVSystem`, `Storage`, `InvControl`, `ExpControl` are deferred by decision 17. Index them with `status: "deferred"`, `property_catalog: null`, `workflow_path: null`, `example_ids: []`, `fixture_usage: []`, and whatever `epri_doc_url` the project has recorded — `null` for `GenDispatcher`, which has no page under any probed name. A retrieval query for `PVSystem` must land on a record that says *documented, deliberately not catalogued, here is why*, rather than on nothing.

That gives **24 records**: 16 catalogued, 8 deferred. If you conclude a class belongs that is in neither list, say so in the build audit rather than adding it silently.

## Deliverables

| # | Artifact | Notes |
|---|---|---|
| 1 | `references/opendss_objects.json` | 24 thin records, measured counts, no property rows |
| 2 | `schemas/catalogs/opendss_objects.schema.json` | Replaced with the thin record; `additionalProperties`/`unevaluatedProperties` closed; `property_catalog` and `epri_doc_url` nullable |
| 3 | `docs/workflows/object_index.md` | How to use the index: what it answers, what it deliberately does not, and the rule that property detail lives in the element catalogs |
| 4 | `references/sources.json` | Additive only, and only for classes with no EPRI record yet |
| 5 | `docs/audits/phase5_object_index_audit.md` | Build audit: environment, commands, and **for each record** the file and rule its counts came from |
| 6 | `opendss_altdss_library/README.md` | Add the index to Contents, drop the "only empty catalog" line |

## Acceptance

1. `validate_catalogs.py` passes **18/18** with `references/opendss_objects.json` carrying 24 records.
2. Every `property_catalog.record_count` equals the length of the file it names, every `property_row_count` equals the sum of its `properties` arrays, every `engine.record_count` equals the number of `dss_capi.json` records in the listed namespaces, every `example_ids` entry exists in `examples.json` with that class in `object_classes`, every `workflow_path` and `readback_evidence` path exists, and every `source_ids` id exists in `sources.json`. The architect will re-derive all of this mechanically; a count that cannot be reproduced is a defect, not a rounding difference.
3. No property name, type, units or description appears in the new catalog, and a record carrying a `properties` array fails validation — demonstrated in the build audit with the validation error text.
4. `element_class` values are unique, and the set is exactly the 16 catalogued classes plus the 8 deferred ones.
5. No element catalog, schema other than the object-index schema, example, fixture, golden or tool changes. `git diff` stays inside `docs/`, `references/`, `schemas/catalogs/opendss_objects.schema.json` and the library README.
6. `manifest.json` and `docs/implementation_plan.md` are untouched — they are architect-owned.

## Out of scope

No retrieval CLI, no search tool, no release packaging, no version tag: those are packages 5.2 and 5.3. No new element catalogs, no deferred class promoted to `catalogued`, no examples, no fixtures, no golden regeneration. Do not restate property data anywhere, including in the workflow page or the audit.
