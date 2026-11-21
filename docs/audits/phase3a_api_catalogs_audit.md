# Phase 3A API and Engine Catalogs — Build Audit

**Build date:** 2026-11-21
**Artifacts:** [altdss_python_api.json](../../opendss_altdss_library/references/altdss_python_api.json) · [dss_capi.json](../../opendss_altdss_library/references/dss_capi.json) · [sources.json](../../opendss_altdss_library/references/sources.json) · [generator](../../opendss_altdss_library/tools/build_altdss_api_catalog.py)
**Targets:** AltDSS-Python `0.2.4` (tag `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee`), DSS C-API `0.14.5` (tag `87d85c2622c8281b92255335bc7c09b11191b21d`)
**Status:** built and schema-valid at commit `45a004d` on `wp/phase3`; independent QA/QC pending.

## Method

- **API catalog:** generated, not hand-written. `tools/build_altdss_api_catalog.py` parses the extracted `altdss==0.2.4` pure-Python wheel with the standard library `ast` module (the package is never imported or executed). It records object classes (`DSSObj` subclasses), collection interfaces (`I<Element>`, which carry `new` and `batch_new`), and the `AltDSS` context class. Property type hints come from `# type:` comments or the matching `*Properties` TypedDict; descriptions come from the wrapper docstrings with the `DSS property name:` trailer removed. Records are sorted deterministically.
- **Engine catalog:** 26 hand-curated records for Line and LineCode, each tied to a `0.14.5` file and line range in `src/PDElements/Line.pas` or `src/General/LineCode.pas`. `tested` records what was actually executed through the pinned stack; static source facts are `not-run`.
- **Source index:** the 15 Line/LineCode records were migrated and three Phase 3A entries added, for 18 total. Identifiers are unchanged, so existing `source_ids` references still resolve. `line_linecode_sources.json` and its schema were removed rather than stubbed, leaving one authoritative index.

## Coverage

| Catalog | Records | Detail |
|---|---|---|
| `altdss_python_api.json` | 99 classes | 46 object classes, 52 collection interfaces, 1 context class; 1,094 properties and 180 methods |
| `dss_capi.json` | 26 records | 17 observed `pass`, 9 `not-run` |
| `sources.json` | 18 records | 15 migrated + 3 Phase 3A entries |

## Checks performed

1. `tools/validate_catalogs.py`: 9/9 manifest and catalog schema pairs pass (Draft 2020-12 with format checking, `jsonschema` 4.26.0).
2. Generator determinism: a second run over the same wheel produced a byte-identical catalog (SHA-256 match).
3. Coverage spot check: the `Line` record contains exactly the 35 DSS properties exposed by the wrapper (internal `_str` proxies excluded), matching the keyword set in the Line/LineCode property catalog; `LineCode` likewise.
4. Casing check: `Conductors`, `pctPerm` (Line), `PctPerm` (LineCode), and `rho` match the pinned source exactly.
5. Citation check: every engine record cites a `0.14.5` URL and line range; no mutable `master` citations.
6. Source-index integrity: every `source_ids` value used by `examples.json` resolves in `sources.json`; all ids are unique and match the schema pattern.

## Known limitations

- Batch classes (`<Element>Batch`) are not separate records; `batch_new` describes batch behavior on the collection interface, and batch property proxies are not itemized.
- Setter-only pseudo-properties such as `Like` and `Kron` are not `property()` objects in the wrapper, so they appear as creation keywords or actions rather than properties.
- Internal `_str` proxies (string views of object-reference properties) are excluded by design.
- Engine records currently cover Line and LineCode only; other element classes are added as Phase 3B packages land.
- Descriptions are copied from wrapper docstrings; they are API documentation, not independent behavioral evidence.

## Open for independent QA/QC

- Re-run the generator on the pinned wheel and confirm the output matches the committed catalog.
- Sample object and collection records against the 0.2.4 source: class names, signatures, property lists, and type hints.
- Verify the 26 engine records against `Line.pas` and `LineCode.pas`: enums, specification sets, scaling, defaults, Switch behavior, and `tested` status.
- Confirm the source-index migration left no dangling `source_ids` and no duplicate ids.
- Confirm the catalog does not imply runtime validation beyond the recorded `tested` entries.

Review instructions: [Phase 3A QA/QC handoff](../handoffs/Phase_3A_API_Catalogs_QAQC_handoff.md).
