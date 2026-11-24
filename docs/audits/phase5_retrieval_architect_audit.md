# Phase 5.2 retrieval tool — Architect/Auditor Review

**Reviewed branch:** `wp/phase5`, tip `b5ad76d` (QA/QC report), clean working tree at review start.
**Package revision under review:** `4b4430b4869f02514111243f3bb998c4ba57b613` (tool, workflow, retrieval audit, README and skill lines).
**Inputs/baseline revision:** `02fe261e87018d1287a64af21ef9ffc92369a2d5` (decision 23, package issued).
**Review date:** 2026-11-23 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, backend `0.14.5`, `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`.

**STATUS:** PASS — no required corrections, four observations, and two corrections to **my own handoff** that the coder caught and recorded rather than papering over.

## What I ran

| Check | Result |
|---|---|
| `--stats` | 926 addressable records across 17 files (2200 including API members), 16 element classes / 461 property rows, 180 API methods / 1094 API properties — reproduces the handoff's numbers exactly |
| `--symbol TapNumber` | three hits: `altdss.RegControl:RegControl.TapNum`, `capi-regcontrol-tap-number`, `RegControl.tapnum`, each labelled `canonical=TapNum`, each with its own citation and access date |
| `--symbol Conductors` | exactly two hits, `LineGeometry.wires` and `Line.wires`, each printing `dss=wires python=Conductors` |
| `--symbol NewContext` | the `altdss.AltDSS:AltDSS.NewContext` method record — symbol search reaches nested API members |
| `--class PVSystem` | one deferred object record, `status: deferred`, `version=unstated`, EPRI pointer, no property rows |
| `--class NotAClassy` | exit **2**, `unknown class 'NotAClassy'. Did you mean AutoTrans, CNData, LoadShape?` |
| `--symbol NotAThing` | exit **1**, no output |
| `--evidence NotALabel` | exit **2** listing the enum |
| `wires --class LineGeometry` | six hits across API, engine and element catalogs, correctly narrowed |
| `--check` | `Object index check: PASS`, exit 0 |

Filters are real, not decorative: `--symbol TapNum --version 0.14.5` narrows to the one element row, `--version 0.2.4` keeps two, and `--symbol TapNum --evidence Observed-working` returns **zero** because both matches are `Official-versioned`. Records with no stated version survive a `--version` filter as `version=unstated`, so the 32 EPRI sources are not erased.

## `--check` carries the 5.1 finding forward correctly

The committed index passes. In a scratch copy of the library I corrupted three fields at once — `RegControl.property_catalog.property_row_count` 35 → 34, `Load.fixture_usage` → `["ieee34 snapshot"]`, `Generator.example_ids` → `["no-such-example"]` — and the tool failed with the tool's own exit code 1 and named each field:

```text
Generator.example_ids: recorded ['no-such-example'], derived ['generator-constant-pq-altdss', 'generator-pv-voltage-target-dss']
Load.fixture_usage: recorded ['ieee34 snapshot'], derived ['ieee13 daily', 'ieee13 snapshot', 'ieee34 snapshot']
RegControl.property_catalog.property_row_count: recorded 34, derived 35
```

That second line is the one that matters: `fixture_usage` is a property JSON Schema cannot express, and the 5.1 review could only catch it with a throwaway script. It is now a command that exits 1.

## Two errors of mine, found by the coder

- **A-1** My handoff's sixth canonical query — `"tap reverts after solve"` — is **unanswerable**: the word `reverts` appears nowhere in the corpus (`grep -ci revert troubleshooting.json` → 0), and concept search is literal AND-token matching, so exit 1 was the only possible outcome. The coder substituted `"manual tap static" --class RegControl --evidence observed-working`, which does return `ts-controlled-solve-retaps`, and wrote the discrepancy into the build audit in as many words. I wrote an acceptance criterion that could not be met; the package is right and the handoff was not.
- **A-2** I described the corpus as "926 addressable records across ten files". There are **17** JSON files across 10 catalog types, because the nine element property catalogs are separate files. The tool measures 17 and says so, and the build audit flags the difference explicitly.

Both are now part of the record rather than silently absorbed, which is the behaviour I want when a handoff and the data disagree.

## Reading the tool rather than only its output

- **Read-only.** No `write_text`, `write_bytes`, `open(`, `mkdir`, `unlink` or `rename` anywhere in the file; it reads the committed catalogs each run and holds no state between runs. `grep` count is 0.
- **Standard library only** — `argparse`, `json`, `re`, `difflib`, `collections`, `dataclasses`, `pathlib`, `sys`. `requirements-validation.txt` is untouched, so the pinned evidence stack cannot drift because of a search tool.
- **Matching is data-driven per catalog** with a per-entry `matches()` returning every field that hit, so a dual-spelling row keeps both.
- **Determinism** holds under repetition: five consecutive `--json` runs of the same query gave one digest (`5daa88a7…8bcd`), and parsed hits are already sorted by `(catalog, record_id, field)`.

## Observations (no action requested)

- **O-1** The `TapNumber` → `TapNum` alias is a single **hard-coded** case in `search()` (`elif symbol == "tapnumber" and entry.record_id in (...)`), not data. It is correct today and labels itself honestly (`canonical_symbol`, `alias_sources`), but a rename of any of those three record ids, or a second alias, silently loses the mapping with no test to notice. Moving it to `python_interface_comparison.json` or a small data file with one regression test would make it durable — a 5.3 or later candidate.
- **O-2** `combine_keyword_matches` folds the generated wrapper accessor into `related_api` on the element hit, so the human output for `--symbol Conductors` shows two lines citing the element and engine sources while the **Python accessor citation is JSON-only**. That is a deliberate de-duplication and documented, but a reader using only human output sees the DSS side of a dual-spelling property and not the wrapper side.
- **O-3** `--check` resolves `docs/...` pointers relative to the **repository root**. Run against a copy of the library outside the repo — exactly what a scratch-tree test does — it reports spurious "does not resolve" failures for every workflow and readback path. My corruption test hit this and it cost a moment of confusion; one sentence in the workflow, or resolving both roots and naming which was used, would prevent it.
- **O-4** Exit code 1 means "no hits", which for a search tool is the common case on a natural phrase. The workflow documents it, but any future script wrapping this tool must distinguish 1 from 2 rather than treating nonzero as failure. An `--allow-empty` flag would make that ergonomic if it ever bites.

## Scope and regressions

`git diff 02fe261..HEAD` touches seven files: the tool, the retrieval workflow, the build audit, the QA/QC report and handoff, the library README and `skill.md`. No catalog, schema, example, fixture, golden, validation requirement, manifest or plan changed — verified by an explicit diff over those paths, which came back empty. `validate_catalogs.py` 18/18, `run_examples.py` 19/19, `run_fixtures.py` 3/3 after the package.

## Where the package lands

Phase 5's retrieval half is done: 926 records are addressable by symbol, concept, class, version and evidence, each hit carrying its citation, tag and access date, and the index that points at them now fails a command when it goes stale. What remains for 5.3 is the release record — and the alias table is the one piece of this package that would benefit from moving out of code first.
