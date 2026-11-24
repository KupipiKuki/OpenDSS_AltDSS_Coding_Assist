# Phase 5.3 release record build audit

**Run date** 2026-11-23 · **Branch** `wp/phase5` · **Inputs** `8ee36b762d1a1396774ea87e0e99f8deabaf492e` · **Verdict** PASS for coder validation, pending independent QA/QC and architect review.

Environment used for the run was Windows 11 AMD64 (build 26300), Python 3.14.6, `jsonschema` 4.26.0, `altdss` 0.2.4, `dss-python` 0.15.7, `dss-python-backend` 0.14.5, and `OpenDSSDirect.py` 0.9.4. AltDSS reported DSS C-API 0.14.5 revision `87d85c2622c8281b92255335bc7c09b11191b21d`. [Pinned requirements](../../opendss_altdss_library/tools/requirements-validation.txt)

## Validation commands

Run from the repository root with the pinned environment active.

```powershell
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B -S opendss_altdss_library/tools/search_catalogs.py --check
python -B -S opendss_altdss_library/tools/search_catalogs.py --check --json
python -B -S opendss_altdss_library/tools/search_catalogs.py --symbol TapNumber
python -B -S opendss_altdss_library/tools/search_catalogs.py --symbol TapNumber --json
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
```

| Check | Result |
| --- | --- |
| Schema validation | 19/19 pairs, with `references/symbol_aliases.json` registered as the nineteenth pair. |
| Catalog check | `Object index check: PASS` and `Symbol alias check: PASS (1 registered)`, exit 0. JSON reports an empty `errors` list and one registered alias. The corpus stays at 926 addressable records across 17 files, or 2,200 with API members. |
| Examples | 19/19, including the IEEE 13 cross-interface example. |
| Fixtures | 3/3 against revision 1 goldens (`ieee13 snapshot`, `ieee13 daily`, `ieee34 snapshot`). |

## Alias proof

I copied the library and `docs/` together to a temporary repository layout so the index's repository-relative pointers resolved. I ran the Package 5.2 script from `git show 4b4430b:opendss_altdss_library/tools/search_catalogs.py` in that copy beside the new script. Both editions exited 0 and printed byte-identical stdout for `--symbol TapNumber`, `--symbol TapNumber --json`, `--symbol TapNum --json`, `--symbol Conductors --json`, and `--stats --json`. The `TapNumber` output retained these three record IDs in order, each labeled `alias=TapNumber` and `canonical=TapNum`.

1. `altdss.RegControl:RegControl.TapNum`
2. `capi-regcontrol-tap-number`
3. `RegControl.tapnum`

I then applied each edit to a fresh copy of the registry row and repeated the CLI commands. The object index passed in every case. [Registry](../../opendss_altdss_library/references/symbol_aliases.json) · [Schema](../../opendss_altdss_library/schemas/catalogs/symbol_aliases.schema.json)

| Scratch edit | Command | Exit and result |
| --- | --- | --- |
| Replace the registry with `[]` | `--check` | 1, `references/symbol_aliases.json: no aliases registered` |
| Same empty registry | `--symbol TapNumber --json` | 1, `hits: []`. A direct `--symbol TapNum` still exits 0. |
| Replace `record_ids` with `["RegControl.missing"]` | `--check` | 1, `TapNumber.record_ids: 'RegControl.missing' does not resolve` |
| Replace `record_ids` with `["RegControl.ptphase"]` | `--check` | 1, `TapNumber.record_ids: 'RegControl.ptphase' does not carry 'TapNum'` |
| Replace `record_ids` with `["Line.epsrmedium"]` | `--check` | 1, `TapNumber.record_ids: 'Line.epsrmedium' does not belong to RegControl` |
| Replace `source_ids` with `["missing-source"]` | `--check` | 1, `TapNumber.source_ids: 'missing-source' does not resolve` |
| Replace `alias` with `tApNuM` | `--check` | 1, `tApNuM: collides with an exact symbol` |
| Restore the original registry | `--check --json` | 0, `"aliases": {"errors": [], "records": 1}` and no index errors |

The C-API behavior record carries `TapNum` in `signature_or_shape`. The checker matches the full symbol there because the `name` field is `Immediate tap readback and bounds`. Direct symbol search continues to use the same exact-match fields as 5.2. The registry requires at least one row to catch accidental removal of the only alias. [Retrieval tool](../../opendss_altdss_library/tools/search_catalogs.py)

## Evidence counts

I read each JSON file independently with Python's `json` module and counted `evidence_label` or `evidence_level` with `collections.Counter`. For the element files (`references/*/*_properties.json`), I counted each class row and its `properties` separately. For `altdss_python_api.json`, I counted its classes, `methods`, and `properties` separately. Engine, example, object-index, interface-comparison, and troubleshooting rows were counted directly. The 132 source rows and two fixture definitions carry citations or provenance without an evidence label. [Release table](../release/README.md#validation-levels)

| Input rows | Official-versioned | Observed-working | Unverified |
| --- | ---: | ---: | ---: |
| Element properties | 460 | 0 | 1 |
| AltDSS wrapper methods | 180 | 0 | 0 |
| AltDSS wrapper properties | 1094 | 0 | 0 |
| C-API engine catalog | 144 | 0 | 0 |
| Examples | 0 | 19 | 0 |
| Troubleshooting | 0 | 16 | 0 |
| Catalogued object index | 0 | 16 | 0 |
| **Handoff tally** | **1878** | **51** | **1** |
| Wrapper class records | 99 | 0 | 0 |
| Element class records | 16 | 0 | 0 |
| Deferred object index | 8 | 0 | 0 |
| Interface comparison | 11 | 2 | 0 |
| **Full corpus** | **2012** | **53** | **1** |

All remaining labels count zero at both scopes. The handoff's `Official-versioned` arithmetic needs a correction. The 461 element property rows include the one `Unverified` row, `Line.epsrmedium`. All 144 engine rows are `Official-versioned`. Moving one out of the element count and one into the engine count leaves the reported 1878 total intact. The full corpus accounts for 2,200 rows as 2012 + 53 + 1 labeled and 134 unlabeled.

## Release checklist

| Charter item | Release record section | Coder check |
| --- | --- | --- |
| Package versions | [Package versions](../release/README.md#package-versions) | `support_targets` matches the manifest exactly. Environment and engine revision recorded. |
| Source check date | [Source check date](../release/README.md#source-check-date) | Manifest date, pinned inventory, and EPRI version caution recorded. |
| Validation levels | [Validation levels](../release/README.md#validation-levels) | Seven labels listed, both count scopes measured, and `Line.epsrmedium` named. |
| Known gaps | [Known gaps](../release/README.md#known-gaps) | All 16 manifest entries accounted for, including the stale empty-index and schema-debt notes with their repository dispositions. Three Phase 4 scope limits, eight deferred classes, and the shared-engine caveat are explicit. |
| Supported tasks | [Supported tasks](../release/README.md#supported-tasks) | Ten runnable task areas link to workflows. Every ID resolves in the 19-example and three-run fixture inventory. The repository has 13 workflow pages, including separate guides for retrieval, the object index, and troubleshooting. |

## Changelog and skill checks

- Checked all 25 cited commits with `git log -1 --format='%h %as %s' <ref>` and confirmed the five changelog dates of November 13 and 20–23. Phase 2's November 20 date is the implementation commit date. Decision 1 records a later owner approval and closure. Every phase entry points to artifacts and commits, and decisions 13–24 appear against the relevant work.
- `skill.md` has 64 lines. The phase paragraph records the completed Phase 3 and 4 work and the Phase 5 release candidate. All 27 existing link targets were preserved and all 29 links resolve, including the new links to the retrieval tool and release record.
- The 5.3 acceptance path list omits `skill.md`; deliverable 4 explicitly requires it. The package includes that file along with the changelog, release docs, registry and schema, and the two specified tools. The manifest's status and version record apply at owner acceptance.
