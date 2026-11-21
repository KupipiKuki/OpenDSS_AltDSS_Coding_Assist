# Phase 3A API and Engine Catalogs — Build Audit

**Build date:** 2026-11-21
**Artifacts:** [altdss_python_api.json](../../opendss_altdss_library/references/altdss_python_api.json) · [dss_capi.json](../../opendss_altdss_library/references/dss_capi.json) · [sources.json](../../opendss_altdss_library/references/sources.json) · [generator](../../opendss_altdss_library/tools/build_altdss_api_catalog.py)
**Targets:** AltDSS-Python `0.2.4` (tag `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee`), DSS C-API `0.14.5` (tag `87d85c2622c8281b92255335bc7c09b11191b21d`)
**Status:** Built at commit `45a004d` on `wp/phase3`. Independent QA/QC passed with findings. The corrections are recorded below. [Independent report](phase3a_api_catalogs_qaqc.md)

## Method

- **API catalog:** generated, not hand-written. `tools/build_altdss_api_catalog.py` parses the extracted `altdss==0.2.4` pure-Python wheel with the standard library `ast` module (the package is never imported or executed). It records object classes (`DSSObj` subclasses), collection interfaces (`I<Element>`, which carry `new` and `batch_new`), and the `AltDSS` context class. Property type hints come from `# type:` comments or the matching `*Properties` TypedDict; descriptions come from the wrapper docstrings with the `DSS property name:` trailer removed. Records are sorted deterministically.
- **Engine catalog:** 26 hand-curated records for Line and LineCode, each tied to a `0.14.5` file and line range in `src/PDElements/Line.pas` or `src/General/LineCode.pas`. `tested` records what was actually executed through the pinned stack; static source facts are `not-run`.
- **Source index:** the 15 Line/LineCode records were migrated and three Phase 3A entries added, for 18 total. Identifiers are unchanged, so existing `source_ids` references still resolve. `line_linecode_sources.json` and its schema were removed rather than stubbed, leaving one authoritative index.

## Coverage

| Catalog | Records | Detail |
|---|---|---|
| `altdss_python_api.json` | 99 classes | 49 object classes, 49 collection interfaces, and 1 context class. 1,094 properties and 180 methods. |
| `dss_capi.json` | 26 records | 17 observed `pass`, 9 `not-run` |
| `sources.json` | 18 records | 15 migrated + 3 Phase 3A entries |

## Checks performed

1. `tools/validate_catalogs.py`: 9/9 manifest and catalog schema pairs pass (Draft 2020-12 with format checking, `jsonschema` 4.26.0).
2. Generator determinism: a second run over the same wheel produced a byte-identical catalog (SHA-256 match).
3. Coverage spot check: the `Line` record contains the 35 public DSS properties exposed by the wrapper. The Line/LineCode property catalog also records creation keywords for actions such as `Like`.
4. Casing check: `Conductors`, `pctPerm` (Line), `PctPerm` (LineCode), and `rho` match the pinned source exactly.
5. Citation check: every engine record cites a `0.14.5` URL and line range; no mutable `master` citations.
6. Source-index integrity: every `source_ids` value used by `examples.json` resolves in `sources.json`; all ids are unique and match the schema pattern.

## Known limitations

- Batch classes (`<Element>Batch`) are not separate records; `batch_new` describes batch behavior on the collection interface, and batch property proxies are not itemized.
- Non-element interfaces exposed by the context, including `IBuses`, `ISettings`, and `ISolution`, are outside the current catalog scope, as are the `Element`, `PCElement`, and `PDElement` batch proxies.
- Setter-only pseudo-properties such as `Like` and `Kron` are not `property()` objects in the wrapper, so they appear as creation keywords or actions rather than properties.
- Internal `_str` proxies (string views of object-reference properties) are excluded by design.
- Engine records currently cover Line and LineCode only; other element classes are added as Phase 3B packages land.
- Descriptions are copied from wrapper docstrings; they are API documentation, not independent behavioral evidence.

## Independent QA/QC disposition

The independent review reproduced the generated catalog byte for byte, checked all 99 API records and 26 engine records, and reran the schema and example harnesses on the pinned stack. [Independent report](phase3a_api_catalogs_qaqc.md)

- **C-1 and C-2 resolved.** The coverage table records the 49/49/1 split, and the limitations list the excluded context interfaces and proxies.
- **S-1 through S-4 resolved.** The Line enum citations now point to L60–L91, the LineCode enum citation to L60–L89, and the LineCode B1/B0 citation to L308–L315. [Pinned Line enum](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L60-L91) · [Pinned LineCode enum](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L60-L89) · [Pinned B1/B0 handling](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L308-L315)
- **S-5 resolved.** The Line note distinguishes the 28 enum mappings from the seven inherited properties.
- **S-6 resolved.** The implementation plan records migration to `sources.json` and removal of the superseded index and schema. [Implementation plan](../implementation_plan.md#51-sequencing-decisions)
