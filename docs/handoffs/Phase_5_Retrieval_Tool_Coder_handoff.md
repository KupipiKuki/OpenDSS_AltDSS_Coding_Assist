# Phase 5 Package 5.2 — Retrieval tool (coder handoff)

**Issued** 2026-11-22 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** package 5.1, accepted as decision 23. **Scope authority** plan section 7 and decision 22.

## Goal

One command that answers "where is this documented, catalogued, exemplified and validated?" across everything Phase 2–5 delivered, and that fails when the index's own numbers go stale. `tools/search_catalogs.py` is a reader, not a new source of truth: it opens the committed catalogs, matches, and prints pointers with citations — it never writes a catalog and never caches one.

## The corpus, measured while preparing this handoff

926 addressable records across ten files:

| Catalog | Records | Identity key | Notes |
|---|---|---|---|
| `references/sources.json` | 132 | `id` | `kind`, `title`, `url`, `version_or_ref`, `accessed`, `topics`, `scope` |
| `references/examples.json` | 19 | `example_id` | `task_description`, `object_classes`, `file`, `expected_result` |
| `references/altdss_python_api.json` | 99 classes | `class_name` + `module_path` | **180 methods** and **1094 properties** nested inside — searchable rows, not classes |
| `references/dss_capi.json` | 144 | `id` | `namespace_or_type`, `name`, `signature_or_shape`, `source` |
| nine element property catalogs | 16 classes | `element_class` | **461 property rows**, each with `name`, `altdss_keyword`, `description`, `units` where applicable |
| `references/opendss_objects.json` | 24 | `element_class` | `status`, `evidence_label`, pointers |
| `references/python_interface_comparison.json` | 13 | `opendss_concept` | `interfaces`, `source_refs` |
| `references/troubleshooting.json` | 16 | `id` | `title`, `symptom`, `cause`, `safe_fix`, `source` |
| `references/fixtures.json` | 2 | `fixture_id` | `files`, `golden_path`, `golden_revision` |

The tool must print its corpus size when asked (`--check` or `--stats`) and the numbers must be these, measured from the files at run time rather than hard-coded.

## Contract

```
tools/search_catalogs.py --symbol Conductors          # exact keyword, either casing regime
tools/search_catalogs.py "tap reverts after solve"    # concept: token AND over text fields
  [--class RegControl] [--version 0.14.5] [--evidence Observed-working] [--json]
tools/search_catalogs.py --check                      # re-derive the object index
```

- **`--symbol NAME`** — case-insensitive exact match against symbol-bearing fields: element-property `name` and `altdss_keyword`, API `class_name`, API method `name`, API property `name`, `dss_capi` `name`, `element_class`. Report **which field** matched, and when both keyword regimes exist print both: a hit on `Conductors` must show `dss=wires python=Conductors`.
- **Positional `QUERY`** — concept search: split into tokens, require all tokens (case-insensitive substring) across the designated text fields per catalog, in any order. No stemming, no fuzzy matching, no scoring beyond the ordering rule.
- **`--class CLASS`** — resolve through `opendss_objects.json` first. An unknown class is a usage error (exit 2) with the near-miss list, **not** an empty result.
- **`--version V`** — keep records whose `version_range`, `version_or_ref`, `target_versions` or `target_version` contains `V` as a substring. Records with none of those fields, or `null`, are **kept** by default and marked `version=unstated` — dropping them would silently hide all 32 EPRI sources, whose `version_or_ref` is null.
- **`--evidence LABEL`** — accept the enum value case-insensitively. The catalogs spell it two ways: `evidence_label` in the element, API, object, example, interface and fixture records, and `evidence_level` in `dss_capi` and issue records. Normalise in the adapter; **do not edit the catalogs to unify them.**
- **`--json`** — one object with `query`, `filters`, `corpus`, `hits[]`. Sorted by `(catalog, record_id, field)`, byte-stable across runs.
- **Exit codes** — `0` hits found, `1` no hits, `2` usage error (unknown flag, unknown class, missing catalog). `--check` returns `0`/`1`.
- The human line format is one hit per line: `catalog_path  record_id  field=value  source_url  tag  accessed`, with `tag` taken from the citation the record carries (`version_range`, `upstream_commit`, `version_or_ref`) and `accessed` from `source.accessed_or_captured`, `accessed` or `retrieved`.

## `--check`: the carry-forward from 5.1

The 5.1 review found that two properties of the object index cannot be expressed in JSON Schema — count accuracy and `fixture_usage` — and were caught only by an architect writing a throwaway script. `--check` makes that a command:

1. For every record in `references/opendss_objects.json`: re-derive `property_catalog.record_count` and `property_row_count` from the file it names; `engine.record_count` from `dss_capi.json` over the listed namespaces; `example_ids` from `examples.json` `object_classes`; `fixture_usage` from the golden `elements` maps plus the daily `peak_step.elements`, with `Circuit` and `LineCode` from the entry scripts and `LoadShape` from `fixtures.json` `daily`; and check that every `workflow_path`, `readback_evidence` and `source_ids` entry resolves.
2. Print every mismatch with the record and field, and exit 1 if any.
3. Prove it in the audit by editing one count by hand, showing the failure, and restoring the file.

The derivation rules are exactly those recorded in the 5.1 build audit and the architect review; if you find a rule that does not match the committed data, report the discrepancy rather than "fixing" the index to suit the tool.

## Traps, measured on the committed data

1. **Two evidence spellings** — `evidence_label` (element, API, object, example, interface) versus `evidence_level` (`dss_capi`, issue records). A single-field filter misses half the corpus.
2. **Two keyword regimes on 2 of 461 property rows** — `wires` (DSS) is `Conductors` (Python) on both `Line` and `LineGeometry`. Every other row has matching names, so a naive search looks correct until someone asks for `Conductors`.
3. **`sources.json` `version_or_ref` is null on all 32 EPRI records** — a strict `--version` filter erases the documentation index.
4. **`troubleshooting.json` `source.url_or_path` is sometimes a repository path** (`docs/audits/...`), not a URL. Do not `urlparse` it; print it as given.
5. **`altdss_python_api.json` ships class pairs** — `RegControl` and `IRegControl`. `--class RegControl` should surface both, or the tool will report one wrapper class where the package ships two.
6. **`dss_capi.json` namespaces are not all public classes** — `TLineObj`, `TLineCodeObj`, `ConductorData`, `TVsourceProp` and the shared bases. Searching that field must not imply "DSS class".
7. **`examples.json` lists `Circuit` on 18 examples** — a class hit there says the example builds a circuit, nothing about the class's fixture usage.
8. **Scope is `opendss_altdss_library/references/**`** — do not index the `docs/` prose. Prose is not evidence and it changes for reasons unrelated to the data.
9. **Standard library only.** `tools/requirements-validation.txt` must stay unchanged; the pinned stack is the evidence base and a search tool must not perturb it.
10. **Determinism.** No set iteration order in output, no timestamps in `--json`, stable sort keys. Two identical runs must be byte-identical.

## Deliverables

| # | Artifact | Notes |
|---|---|---|
| 1 | `tools/search_catalogs.py` | Adapter-per-catalog registry, both query modes, all filters, `--check`, `--stats`, `--json`, exit codes |
| 2 | `docs/workflows/retrieval.md` | Six canonical queries with their real output, the filter semantics, the exit codes, and what the tool deliberately does not do (no ranking, no fuzzy, no web) |
| 3 | `docs/audits/phase5_retrieval_audit.md` | Environment, corpus counts, the six queries, the `--check` pass **and** the hand-edited failure, the unknown-class error, and determinism proof (two runs, same bytes) |
| 4 | `opendss_altdss_library/README.md` and `skill.md` | One line each: the tool exists, what it answers |

## Acceptance

1. `--stats` reports the corpus table above, measured at run time: 132 / 19 / 99 (+180 methods, +1094 properties) / 144 / 16 (+461 rows) / 24 / 13 / 16 / 2.
2. `--symbol TapNumber` returns the RegControl property row, the API method or property that carries it, and the `dss_capi` record — each with its citation.
3. `--symbol Conductors` returns exactly the two `wires` rows and prints both keyword spellings.
4. `--class PVSystem` returns the deferred object record and states `status: deferred`; it returns no property rows, and the workflow says why that is correct.
5. `--check` exits 0 on the committed index and exits 1 after a single hand-edited count, with the record and field named. Both runs appear in the audit.
6. `--class NotAClassy` exits 2 with a near-miss suggestion; a query with no hits exits 1; a hit exits 0.
7. Two identical invocations produce byte-identical output, and `--json` is sorted.
8. No catalog, schema, example, fixture, golden or `requirements-validation.txt` changes; `git diff` stays inside `tools/`, `docs/` and the two README/skill files. `manifest.json` and the plan remain architect-owned.
9. `validate_catalogs.py` still passes 18/18, `run_examples.py` 19/19, `run_fixtures.py` 3/3.

## Out of scope

No release record, no version tag, no skill rewrite — that is 5.3. No web retrieval, no ranking or relevance scoring beyond exact-then-substring, no index file of the tool's own (it reads the catalogs each run; if that ever becomes too slow, measure it and raise it rather than adding a cache nobody validates), and no edits to any catalog.
