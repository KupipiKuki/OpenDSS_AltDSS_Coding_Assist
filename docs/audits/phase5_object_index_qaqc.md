# Phase 5.1 thin object index — Independent QA/QC Report

**Reviewed branch:** `wp/phase5` (tip `6da5498`, synced with `origin/wp/phase5`; the tip is docs-only — it pins the handoff's package-revision line, verified by `git diff 4f78c26..6da5498`, one line in the QA/QC handoff). **Package revision under review:** `4f78c264a5f4ad81a09dd5b4d4cc4c23fe0360c9` (per the pinned handoff at `6da5498`). **Inputs/baseline revision:** `5c7797e29d6d4e24e9ad4aa7b3c82d387e6df0c1`. **Reviewed state:** `git status --porcelain` clean; `git diff --check 5c7797e..6da5498` clean.
**Review date:** 2026-11-22. **Reviewer environment:** venv installed from `tools/requirements-validation.txt`, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine `DSS C-API 0.14.5 revision 87d85c2…`), `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`.

**STATUS:** PASS (no blocking findings; no required corrections)

## Structure and mechanical re-derivation (351 checks, 0 failures)

- `references/opendss_objects.json` holds **24 records** with unique `element_class` values: exactly the **16 catalogued** classes (Capacitor, Circuit, CNData, Generator, Line, LineCode, LineGeometry, LineSpacing, Load, LoadShape, RegControl, Transformer, TSData, Vsource, WireData, XfmrCode) plus the **8 deferred** classes from decision 17 (AutoTrans, CapControl, ExpControl, GenDispatcher, GrowthShape, InvControl, PVSystem, Storage). Deferred records carry `property_catalog`/`workflow_path` null and empty `example_ids`/`fixture_usage`, as the schema's if/then enforces.
- Every `property_catalog.record_count` equals the length of the file it names and every `property_row_count` equals the summed `properties` lengths (e.g. `vsource_properties.json` 2/37, `opendss_line_linecode_properties.json` 2/67, `line_geometry_wires_properties.json` 5/82, `transformer_properties.json` 2/104, single-record catalogs 1/22, 1/49, 1/43, 1/35).
- Every `engine.record_count` equals the count of `dss_capi.json` records whose `namespace_or_type` is in the listed namespaces, including the internal type namespaces (Line = `Line`+`TLineObj`+`TLineProp` → 17; LineCode = `TLineCodeObj`+`TLineCodeProp`+`TLineCode` → 10; Vsource = `Vsource`+`TVsourceProp` → 10; WireData/CNData/TSData share `ConductorData` (+`CableData` for the cable classes) → 4/5/5). Shared base namespaces (`TPCElement`, `TDSSCktElement`, `TDSSCircuit`, `Solution`, `DSS C-API`) are attached to no class; the `Load.Daily` one-record quirk is unattached and mentioned in `Load.notes`.
- Every `example_ids` entry exists in `examples.json` with that class in `object_classes`, and the sets match exactly (e.g. Circuit 18, Load 11, Line 6, Transformer 5, Capacitor/RegControl/Vsource 3, Generator/LineCode/LineGeometry/LineSpacing/LoadShape/WireData 2, XfmrCode 1, CNData/TSData 0).
- Every `source_ids` id exists in `sources.json`; every non-null `epri_doc_url` equals the `url` of one of that record's `source_ids`. Every `workflow_path` and `readback_evidence` path exists on disk.
- Both wrapper pointers resolve in `references/altdss_python_api.json` by `module_path`/`class_name` for all 24 records (`Circuit` → `altdss.AltDSS` with a null `interface_record`, as documented); at runtime all 24 `context_accessor` values resolve on the `AltDSS` class and on a fresh context instance (23 collections plus `ctx.Commands`).
- `fixture_usage` re-derived from the golden element captures (both snapshots and the daily `peak_step` hold capacitor/line/load/regcontrol/transformer/vsource), the two upstream entry scripts (Circuit and LineCode data assignment), and `fixtures.json` `daily.shape.assignment: "Load.daily"` (LoadShape → `["ieee13 daily"]` only, correctly not read from golden `elements` since shapes are not circuit elements). All match.
- TSData pointer: `epri_doc_url` is the cable-modeling technote `https://opendss.epri.com/CableModelinginOpenDSS.html`, present among its `source_ids`; live checks confirm `TSData.html` and `TSData1.html` are both 404 while the technote is 200. GenDispatcher has `epri_doc_url: null` — `GenDispatcher.html` and `GenDispatcher1.html` are both 404 live. The five new source records are exactly the five newly indexed EPRI pages (TSData technote, PVSystem, Storage, InvControl, ExpControl — all 200 live); `CapControl.html` 404 / `CapControl1.html` 200 and `RegControl.html` 200 / `RegControl1.html` 404 confirm the catalog uses the live name forms.
- Thin-index rule verified textually: no `properties`, `data_type`, `default_value`, `units` or `description` string appears anywhere in the catalog file.

## Harness runs (pinned stack, `python -B` from the repo root)

- `validate_catalogs.py` → exit 0, **18/18 schema pairs**, including `references/opendss_objects.json` with **24 records** against the replaced thin schema.
- `run_examples.py` → exit 0, **19/19 PASS**. `run_fixtures.py` → exit 0, **3/3 PASS** (ieee13 snapshot, ieee13 daily, ieee34 snapshot). `compare_interfaces.py` → exit 0, both fixtures PASS, and the regenerated report is **byte-identical to the committed blob** (SHA-256 `578d56f9a4d024205e9f652b49e17371da2b58b74b49191c639905595ab8c97a`; the working-tree copy differs only by autocrlf line endings, which git reports as clean).

## Schema guard (thin-record enforcement, injected cases)

Through the same registry `validate_catalogs.py` builds: the committed index validates; an injected `properties` array fails with `Additional properties are not allowed ('properties' was unexpected)` (the audit's exact text); an unknown nested field (`engine.extra`) fails with `Additional properties are not allowed ('extra' was unexpected)`; a top-level `units` field fails likewise; a duplicate class with differing metadata fails via `maxContains` + `maxItems`, and even an identical duplicate fails `maxItems: 24`.

## Baseline preservation and scope

- `git diff 5c7797e..6da5498` touches exactly the 7 declared files: the build audit, the QA/QC handoff (pin), `docs/workflows/object_index.md`, the library README (index added to Contents, "remains empty" line dropped), `references/opendss_objects.json`, `references/sources.json`, and `schemas/catalogs/opendss_objects.schema.json`.
- Everything else is byte-identical to the inputs revision: all accepted property catalogs, `dss_capi.json`, `altdss_python_api.json`, `examples.json`, `fixtures.json`, the whole fixture tree and all three goldens, every other schema, every example file, all tools, `docs/implementation_plan.md`, and `manifest.json` (both architect-owned files untouched, as the handoff required).
- `sources.json` 127 → 132: **+5 records, zero removed, zero pre-existing changed**, and only for classes with no prior EPRI entry.

## Limitations (as documented, confirmed)

- The index is a pointer file: it answers "where is this class documented, catalogued, exemplified, validated" and deliberately restates no property data; the mechanical schema guard enforces that. Retrieval CLI / batch search is package 5.2; the release record is 5.3.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
