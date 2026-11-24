# Phase 5.3 release record — architect audit

**Reviewed** `wp/phase5` at `410fd93` (coder package `6b918de`, QA/QC report `410fd93`; inputs baseline `8ee36b7`), `git status` clean, synced with `origin/wp/phase5`, no tag exists.
**Audit date** 2026-11-23 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **Independent QA/QC** Mistral 4
**Environment** Windows 11 AMD64 (10.0.26300), Python 3.14.6, `jsonschema` 4.26.0, `altdss` 0.2.4, `dss-python` 0.15.7, backend `0.14.5`, `OpenDSSDirect.py` 0.9.4. Probes run with `python -S -B` to keep the retrieval tool on the standard library.

## STATUS: PASS WITH FINDINGS

The package does what the handoff asked, and the two things most likely to be faked — the evidence arithmetic and the alias being data rather than a hard-coded branch — survive independent measurement. Two documentation surfaces were not extended for the new registry, and the release record's `Official-current` row needs a scope clause. Neither is a data or evidence error.

**Source review** (do the documents say what the pinned sources say, and do their numbers match the catalogs): PASS WITH FINDINGS, R-1 and F-2 below.
**Runtime execution** (do the harnesses and the tool actually behave): PASS — 19/19 schema pairs, 19/19 examples, 3/3 fixtures, `--check` exit 0 on the committed tree, and seven alias mutations each producing the intended failure.

## What I re-measured rather than read

I counted the catalogs myself with `json` and `collections.Counter`, walking `properties`, `methods` and record arrays rather than trusting the release table.

| Measurement | Result |
|---|---|
| Element catalogs | 9 files, **16** class records, **461** property rows = **460** `Official-versioned` + **1** `Unverified` |
| `altdss_python_api.json` | **99** class records, **180** methods, **1094** properties |
| `dss_capi.json` | **144** records, all `Official-versioned` |
| Examples / troubleshooting / object index | 19 / 16 / 16, all `Observed-working` |
| Interface comparison | 13 records = 11 `Official-versioned` + 2 `Observed-working` |
| Object index | 24 records = 16 catalogued + 8 deferred |

That resolves the two tallies exactly as the release record publishes them: 460 + 180 + 1094 + 144 = **1878**, and 19 + 16 + 16 = **51**; full corpus 1878 + 99 + 16 + 8 + 11 = **2012** and 51 + 2 = **53**, with **1** `Unverified` at both scopes. The 2,200 figure closes too: 2012 + 53 + 1 labeled and 132 sources + 2 fixture definitions unlabeled = 2,200, which is 926 addressable records plus 1,274 API members.

The single `Unverified` record is `Line.epsrmedium` in `references/lines/opendss_line_linecode_properties.json`, `supported_in_target: false`, no DSS or AltDSS keyword. The release record names it, which is the point of the row.

## Findings

### R-1 — the new registry is in the code and the schemas but not in the two documents that describe the corpus

**Where:** `docs/workflows/retrieval.md` lines 22, 35 and 40; `opendss_altdss_library/README.md` inventory list (lines 13–18 and 29–30).
**Source:** `references/symbol_aliases.json` (committed at `6b918de`), `schemas/catalogs/symbol_aliases.schema.json`, `tools/validate_catalogs.py` pair 19.
**Problem:** the workflow still says the classic `TapNumber` spelling "points to the `TapNum` records with an explicit alias label" without saying the mapping now lives in a validated data file, and its `--check` description enumerates the property and engine counts, example IDs, fixture usage and pointer checks but not the alias section — a reader would conclude `--check` does not cover aliases. The exit-code row compounds it: "the index check found a mismatch" is now only half of what exit 1 means. `opendss_altdss_library/README.md` inventories the object index, sources, examples, element catalogs, fixtures and interface comparison, but not the symbol alias registry, so the package README's inventory is one catalog short of the directory.
**Requested correction:** one clause in each place. In the query rules, name `references/symbol_aliases.json` as the declared source of the alias and its schema as the nineteenth validated pair. In the check description and the exit-code row, add the alias section (`Symbol alias check: PASS/FAIL (n registered)`) to what `--check` reports and to what exit 1 covers. Add one line to the package README inventory for the registry beside the retrieval tool entry.
**Responsibility:** mine as much as the coder's — the 5.3 handoff listed `skill.md` for updating and did not list these two files, so the omission was not a deviation from the brief.

### F-2 — `Official-current` reads 0 in the release record while 63 labels with that value ship in the repository

**Where:** `docs/release/README.md`, Validation levels table, `Official-current` row (0 handoff / 0 full corpus).
**Source:** `references/lines/opendss_line_linecode_properties_legacy.json` — 2 class records and 66 property rows carrying **63** `Official-current` and 3 `Official-versioned` labels. The file is not in the retrieval corpus, is not in `SCHEMA_PAIRS`, and is described in the record's known gaps only as "retained for provenance".
**Problem:** the table's own definition ("every labeled record exposed by retrieval") makes 0 correct, so this is not an arithmetic error. But a labeled catalog named `*_legacy.json` sitting inside `references/` and excluded from both validation and retrieval is exactly the case a reader would not think to ask about, and the release record is the document that teaches them these seven labels mean something. An unvalidated, unsearched, unlabelled-as-such catalog is the one place where a future editor could quietly cite `Official-current` evidence that nothing checks.
**Requested correction (owner's call, one sentence):** under the table, state that the corpus is the 17 files the retrieval tool reads, and that `references/lines/opendss_line_linecode_properties_legacy.json` is excluded by design — provenance only, unvalidated, and the sole holder of `Official-current` labels in the repository. Alternatively retire the legacy file to `archive/`, which would make the 0 true without a footnote. I have no preference between them; I do want the choice recorded rather than implied.

## Observations

- **O-1 — duplicate-alias uniqueness is a `--check` property, not a schema property.** I verified both directions: a duplicated registry row passes `validate_catalogs` (19/19, exit 0) and fails `--check` with `TapNumber: duplicate alias` (exit 1). That division is sound — JSON Schema cannot express cross-item uniqueness — but nothing in the schema or the workflow says so, so a future editor could reasonably assume the schema covers it. One clause in the schema's `description` or the workflow would close it.
- **O-2 — the release record carries internal finding IDs without pointers.** The known-gaps bullet on schema metadata cites `E-3` and Capacitor `O-1` with no link. Both are real and I verified them (below), but a release document is the wrong place for a reader to have to hunt a finding ID.
- **O-3 — two architect-owned bookkeeping items, to be applied at acceptance, not by the coder.** `manifest.json` `known_gaps[1]` still says `opendss_objects` "is still empty pending a later phase", which Phase 5.1 falsified; and the manifest `catalogs` object has no phase-5 entry for `references/symbol_aliases.json`. The release record dispositions the first honestly and the second is invisible to it, so neither is a package defect — both are mine to fix in the acceptance commit.
- **O-4 — the coder's evidence-count paragraph reads oddly without the handoff in hand.** "Moving one out of the element count and one into the engine count leaves the reported 1878 total intact" is exactly right about *my* handoff (which said 461 element rows + 143 engine records), but a reader of the audit alone cannot see why two rows move. The fix belongs in a clause, not a re-derivation (see A-1).
- **O-5 — the changelog's Phase 2 date and acceptance are two different events and it says so, once.** "Decision 1 recorded owner acceptance in the Phase 3A planning history" is accurate — the implementation landed 2026-11-20 (`1d4088f`) and the owner approved 2026-11-21 — but the phrasing is the only place that distinction is visible. It survives my check; I note it because it is the kind of sentence a later editor compresses into a wrong date.

## Handoff errata (architect, not coder)

**A-1.** My 5.3 handoff said the tally resolves as "461 element property rows + 180 wrapper methods + 1094 wrapper properties + 143 engine records". Both counts were wrong: 461 is the raw element row count *including* the one `Unverified` row, so the `Official-versioned` element count is **460**, and the engine catalog holds **144** records, not 143. The published 1878 was right; the decomposition was not. The coder measured the truth, published 460/144, and left the total intact — the correct handling of an erroneous handoff figure.

**A-2.** The handoff listed five deliverables and did not name `docs/workflows/retrieval.md` or the package README inventory, which is where R-1 lives. I own that gap.

## What I verified about the alias, from scratch

Each case is a fresh copy of the repository (not the library alone, so the index's repository-relative pointers resolve), with one edit to `references/symbol_aliases.json`.

| Case | `--check` | `--symbol TapNumber` |
|---|---|---|
| Committed registry | exit 0, `Symbol alias check: PASS (1 registered)` | 3 hits: `altdss.RegControl:RegControl.TapNum`, `capi-regcontrol-tap-number`, `RegControl.tapnum` |
| Registry emptied to `[]` | exit 1, `no aliases registered` | **0 hits** — the alias comes from the data |
| `record_ids[0]` → `RegControl.tapnumX` | exit 1, `'RegControl.tapnumX' does not resolve` | 2 hits (per-id) |
| `record_ids[0]` → `RegControl.ptratio` | exit 1, `does not carry 'TapNum'` | 3 hits (the other two ids still resolve) |
| `source_ids[0]` → `no-such-source` | exit 1, `'no-such-source' does not resolve` | 3 hits |
| `alias` → `TapNum` | exit 1, `TapNum: collides with an exact symbol` | 0 hits |
| `element_class` → `Line` | exit 1, three `does not belong to Line` lines | 0 hits |
| Duplicated row | exit 1, `TapNumber: duplicate alias` | 3 hits |

Schema wiring, tested by corrupting the registry and running `validate_catalogs.py`: unknown property → FAIL (`Additional properties are not allowed`), empty `record_ids` → FAIL (`should be non-empty`), missing `source_ids` → FAIL (`is a required property`), empty `alias` → FAIL (`should be non-empty`). The nineteenth pair is real, not a registration that validates nothing.

**5.2 behaviour is unchanged.** `--symbol Conductors`, `--class PVSystem`, `--symbol IRegControl --class regcontrol`, the concept query `"manual tap static" --class RegControl --evidence observed-working`, `--symbol TapNum`, `--stats` and `--check --json` all behave as the 5.2 audit recorded; `--symbol TapNum` returns exact matches only, so the alias does not double-count. `--check --json` reports `errors: []` and `aliases: {records: 1, errors: []}`, corpus unchanged at 926 records / 17 files.

## Release record — the five charter items

| Charter item | Section present | My check |
|---|---|---|
| Package versions | `## Package versions` | `support_targets` block parses equal to the manifest verbatim; engine build line `0.14.5` / `87d85c2…` matches `sources.json`, `dss_capi.json` and `python_interface_comparison.json`; beta line marked unvalidated |
| Source check date | `## Source check date` | manifest `2026-11-21`; EPRI mixed-version caution stated |
| Validation levels | `## Validation levels` | seven labels, both scopes, arithmetic re-derived above; `Line.epsrmedium` named; see F-2 for the scope clause |
| Known gaps | `## Known gaps` | all 16 manifest entries mapped to the eight bullets — see below |
| Supported tasks | `## Supported tasks` | 10 rows, each with an existing workflow link; 19/19 example ids and 3/3 fixture runs cited; zero unresolved tokens |

Known-gaps mapping, entry by entry: [1]→bullet 1, [2][3]→bullet 2, [4][5]→bullet 3, [6][8][9][10]→bullet 4, [13]→bullet 5, [11][12][15]→bullet 6, [14][16]→bullet 7, [7]→bullet 8. Nothing is dropped, and the two entries that time has overtaken ([1] the empty index, [13] the schema fields) are dispositioned against the work that closed them rather than deleted. I verified both dispositions: `opendss_objects.json` holds 24 records, and commit `f8fac0c` (2026-11-22) added exactly seven row fields — `array_element_type`, `array_length`, `dss_text_write`, `python_creation_status`, `python_method`, `python_write_status`, `readback_type` — and its message records the `O-1` closure.

## Changelog, skill and scope

- All 25 cited commits exist. Dates match `git log`: 2026-11-13 (`c8edd43`, `7d1bb90`), 2026-11-20 (`3263daa`, `1d4088f`), 2026-11-21 (Phase 3A/3B), 2026-11-22 (Phase 4, 5.1), 2026-11-23 (5.2, 5.3). Decision attributions check out against the plan: 2 and 4 scope and roles, 5–12 the Phase 3B acceptances and preparation/handoff timing (8 and 10 are preparation, which is why the entry says "acceptance and handoff timing" rather than "acceptance"), 3 and 13 the stop gate and fixture pin, 14–17 and 18–21 the Phase 4 packages, 22–24 Phase 5.
- `skill.md` is 64 lines, its phase paragraph states the closed Phase 1–4 state and the Phase 5 release candidate, and its 30 links resolve. The release record's 34 links resolve, including both anchors (`phase5_release_audit.md#evidence-counts`, `implementation_plan.md#11-owner-decisions`).
- `git diff 8ee36b7..410fd93` touches 10 files and nothing else: `CHANGELOG.md`, `docs/release/README.md`, the coder audit, the QA handoff, the QA report, `references/symbol_aliases.json`, its schema, `skill.md`, `search_catalogs.py`, and the single-line pair registration in `validate_catalogs.py`. `manifest.json`, `docs/implementation_plan.md`, all goldens, all element catalogs, `requirements-validation.txt` and the examples are untouched. No tag was created.

## SCHEMA RESULT: pass

`validate_catalogs.py` → exit 0, **19/19 schema pairs**, `RESULT: PASS`, with the alias registry as the nineteenth pair. Malformations of that registry fail as shown above.

## RUNTIME RESULT: pass

`run_examples.py` → 19/19 PASS, environment block Python 3.14.6 / `altdss` 0.2.4 / `dss-python` 0.15.7 / backend 0.14.5 / Windows 11 AMD64. `run_fixtures.py` → 3/3 PASS (`ieee13 snapshot`, `ieee13 daily`, `ieee34 snapshot`). `search_catalogs.py --check` → exit 0 with both sections passing.

## REQUIRED CORRECTIONS

1. **R-1** — name the alias registry and the alias check in `docs/workflows/retrieval.md` (lines 22, 35, 40) and add the registry to the `opendss_altdss_library/README.md` inventory. Sources: `references/symbol_aliases.json`, `schemas/catalogs/symbol_aliases.schema.json`, `tools/validate_catalogs.py`.
2. **F-2 decision** — either add the one-sentence scope clause to the Validation levels section naming the excluded legacy catalog as the repository's only holder of `Official-current` labels, or retire that file to `archive/`. Owner's choice; the current state should not stand undocumented.

## Disposition

PASS WITH FINDINGS. The package is technically correct: every number in it re-derives, the alias is genuinely data-driven, the schema pair is real, and the changelog is traceable. R-1 is a three-line documentation fix; F-2 is a sentence or a file move. I recommend applying both in one small remediation commit before the phase closes, then acceptance, the version/tag decision and the `schema_version` promotion.

## Remediation verification (R-1, F-2) — appended 2026-11-23

**Reviewed** `wp/phase5` at `bc58ece`; remediation commit `6fcd1a0` against handoff `65120fa`. Tree clean, synced, no tag.

**STATUS: PASS.** Both findings are closed and nothing moved except documentation.

- **R-1 closed.** `docs/workflows/retrieval.md` now names the registry as the declared mapping, states that removing the row removes the alias hits, records its place as the nineteenth validation pair, and links the registry and its schema. The `--check` description carries all four behaviours the checker implements — record id resolution, canonical-symbol presence under the declared class, source id resolution, and rejection of duplicates and exact-symbol collisions — plus the exact output line `Symbol alias check: PASS (n registered)`, which is the string the tool actually prints. The exit-code table now covers both checks. The library README carries the one-line inventory entry.
- **F-2 closed.** The one sentence under the validation table states the corpus is the 17 files retrieval reads, that the legacy Line/LineCode catalog is excluded deliberately as provenance, and that it is the repository's sole holder of `Official-current` labels — without claiming validation or search for it and without adding a count to the table. I re-verified the underlying facts repo-wide: exactly one JSON file in the repository carries `Official-current` labels (63 of them, plus 3 `Official-versioned`, in that file), the retrieval corpus is 17 files, and neither tool contains a legacy reference.
- **Nothing moved.** `validate_catalogs.py` 19/19; `search_catalogs.py --check` exit 0 with both sections PASS; `run_examples.py` 19/19; `run_fixtures.py` 3/3; `skill.md` 64 lines; every relative link in the four touched files resolves; `git diff 65120fa..bc58ece` touches only the three documentation files plus the QA report.

Observations carried to the acceptance commit, all architect-owned:

- **O-6 — the root `README.md` understates the schema pairs.** Line 26 reads "The pinned stack passed 18 schema checks"; with the registry registered it is 19. The sentence is scoped to Phase 4, so it was true when written, but 5.3 is the first change to the count and a reader takes that paragraph as the current state. My remediation handoff confined the diff to three files, which is why it was not fixed in the pass — the omission is mine to repair, alongside O-3.

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
