# Search the committed catalogs

Run the tool from the repository root. It reads the committed JSON data using Python's standard library.

~~~powershell
$search = 'opendss_altdss_library/tools/search_catalogs.py'
~~~

The examples below show selected fields from actual results. Human output also includes the catalog path, citation, tag, and access date.

| Command | Result |
| --- | --- |
| `python -B $search --symbol TapNumber` | Three alias hits for `TapNum`: `altdss.RegControl:RegControl.TapNum`, `capi-regcontrol-tap-number`, and `RegControl.tapnum`. |
| `python -B $search --symbol Conductors` | `LineGeometry.wires` and `Line.wires`, each showing `dss=wires python=Conductors`. |
| `python -B $search --class PVSystem` | `PVSystem  element_class=PVSystem  status: deferred` with its EPRI pointer. The owner deferred this class under decision 17, so its class record has no property catalog. |
| `python -B $search "manual tap static" --class RegControl --evidence observed-working` | `ts-controlled-solve-retaps` in the troubleshooting catalog, cited to `docs/workflows/regcontrol.md`. |
| `python -B $search "cable modeling technote" --version 0.14.5` | The `TSData` object and `epri-tsdata-cable-modeling` source both qualify with `version=unstated`. |
| `python -B $search --symbol IRegControl --class regcontrol --json` | One hit for `altdss.RegControl:IRegControl` with `field: class_name` and target version `0.2.4`. |

## Query and filter rules

- `--symbol` matches names and keywords exactly, ignoring case. The classic `TapNumber` spelling returns `TapNum` records with an explicit alias label. The registry declares the alias, canonical symbol, element class, record IDs, and source IDs. Removing the row removes its alias hits. The registry and its schema are the nineteenth validation pair. For a dual-spelling property such as `Conductors`, JSON attaches the matching wrapper citation under `related_api`. [Registry](../../opendss_altdss_library/references/symbol_aliases.json) · [Registry schema](../../opendss_altdss_library/schemas/catalogs/symbol_aliases.schema.json)
- A quoted concept query requires every whitespace-delimited token to occur somewhere in a record's searchable fields. Use terms that appear in the committed evidence. The tool uses literal substring matching, deterministic ordering, and local catalogs only.
- `--class` resolves a name in the object index before searching. It follows the class's wrapper modules, engine namespaces, example tags, and relevant text records. A class-only lookup for a deferred class returns its index entry. An unknown class gives candidate names.
- `--version` matches the stated version fields by substring. Records with no stated version remain in the result with `version=unstated`. This includes undated EPRI documentation. `--evidence` matches the recorded evidence label case-insensitively across both catalog spellings.
- `--json` emits a single object with `query`, `filters`, `corpus`, and `hits`. Hits sort by catalog path, record ID, and match field. Full citations and object pointers are available in the JSON.

## Check the index

~~~powershell
python -B $search --stats
python -B $search --check
~~~

`--stats` counts the data files and searchable rows. `--check` re-derives the property and engine counts, example IDs, and fixture usage, and verifies workflow, readback, and source pointers. It also resolves every registered record ID and source ID, verifies that each listed record carries the canonical symbol for the declared element class, and rejects duplicate aliases and collisions with existing exact symbols. The alias section reports `Symbol alias check: PASS (n registered)` on success.

| Exit code | Meaning |
| --- | --- |
| 0 | Search found hits, statistics printed, or both the index and alias checks passed. |
| 1 | Search found no hits, or the index or alias check failed. |
| 2 | Invalid usage or unavailable catalog during search or statistics. |

Use the linked property catalog for property detail and the fixture audit for validation scope. [Object index workflow](object_index.md) · [Retrieval build audit](../audits/phase5_retrieval_audit.md)
