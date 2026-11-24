# Phase 5.3 release record — remediation handoff (R-1, F-2)

**Issued** 2026-11-23 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **Owner decisions** apply both corrections; F-2 by scope clause, not by moving the file
**Reviewed package** `6b918de` · **Audit** [phase5_release_architect_audit.md](../audits/phase5_release_architect_audit.md) · **Branch** `wp/phase5`

This is a remediation pass, not a new package. Two corrections, documentation only. No data, schema, tool or version changes. Do not create a tag, do not edit `manifest.json` or `docs/implementation_plan.md`.

## R-1 — the alias registry is missing from the two documents that describe the corpus

The registry exists and is validated (pair 19), but the documents a reader uses to learn what the tool does and what the package ships do not mention it. My handoff didn't list these files, so this is my omission as much as yours.

**`docs/workflows/retrieval.md`, line 22 (query rules).** The sentence currently reads that the classic `TapNumber` spelling "points to the `TapNum` records with an explicit alias label". Add that the mapping is declared in `references/symbol_aliases.json` — alias, canonical symbol, element class, the record ids it answers for, and its source ids — and that the file is validated by `schemas/catalogs/symbol_aliases.schema.json` as the nineteenth schema pair. The point a reader must leave with: the alias is data, so removing the row removes the behaviour.

**`docs/workflows/retrieval.md`, line 35 (check description).** The current sentence enumerates property and engine counts, example IDs, fixture usage and pointer checks. Add the alias section: `--check` also resolves every registered record id, verifies each listed record carries the canonical symbol under its element class, resolves every source id, and rejects a duplicate alias or one that collides with an existing exact symbol. Report the section's own output line: `Symbol alias check: PASS (n registered)`.

**`docs/workflows/retrieval.md`, line 40 (exit codes).** "the index check found a mismatch" is now half of what exit 1 means. Make exit 1 cover both checks — index and alias.

**`opendss_altdss_library/README.md`, inventory list.** Add one line for the symbol alias registry (`references/symbol_aliases.json`) beside the retrieval tool entry, naming what it holds (the `TapNumber` → `TapNum` mapping with the record ids it answers for) and that it is schema-validated. One line, in the existing voice.

## F-2 — the `Official-current` row needs its scope stated

**`docs/release/README.md`, Validation levels section.** The `Official-current` row reads 0 at both scopes. That is correct for the corpus as the table defines it — "every labeled record exposed by retrieval" — but `references/lines/opendss_line_linecode_properties_legacy.json` sits inside `references/`, carries **63** `Official-current` property labels (and 3 `Official-versioned`, across 2 class records and 66 property rows), and is not in the retrieval corpus or in `SCHEMA_PAIRS`.

Add one sentence under the table stating that the corpus is the 17 files the retrieval tool reads, that this legacy file is excluded deliberately as provenance only — unvalidated and unsearched — and that it is the repository's only holder of `Official-current` labels. The owner chose the clause over retiring the file to `archive/`, so the file stays where it is; the exclusion simply stops being implicit. Do not claim the file is validated or searched, and do not count its rows into the table.

## Do not

- Do not touch `CHANGELOG.md`, `docs/release/README.md` beyond that one sentence, the alias registry or its schema, `search_catalogs.py`, `validate_catalogs.py`, `skill.md`, the catalogs, the goldens, the examples, `requirements-validation.txt`, `manifest.json` or the plan.
- Do not restate counts anywhere. The numbers in the release record are verified; a second copy of them is how they drift.
- Do not create a tag or move `schema_version` past `0.3.0-draft`. The version decision is the owner's, applied at acceptance.

## Verification before you report back

1. `validate_catalogs.py` → 19/19, exit 0. `search_catalogs.py --check` → exit 0, both sections PASS. `run_examples.py` → 19/19. `run_fixtures.py` → 3/3. Nothing should move; prove it didn't.
2. Every link in the four touched files resolves, including the two new ones (`references/symbol_aliases.json`, its schema). `skill.md` stays at 64 lines.
3. `git diff` against `246b343` stays inside `docs/workflows/retrieval.md`, `opendss_altdss_library/README.md` and that one sentence in `docs/release/README.md`.
4. State in your report that the `--check` alias section, the exit-code row and the README inventory line each now describe behaviour you ran, not behaviour you inferred.
