# Phase 5.3 remediation (R-1, F-2) — Independent QA/QC Report

**Reviewed branch:** `wp/phase5` (tip `6fcd1a0`, synced with `origin/wp/phase5`). **Remediation commit under review:** `6fcd1a0` ("docs: resolve Phase 5.3 release audit findings R-1 and F-2"), issued via handoff `65120fa` after the architect audit `246b343` (pass with findings R-1 and F-2). **Audit/baseline revision:** `246b343`. **Reviewed state:** `git status --porcelain` clean; `git diff --check 246b343..6fcd1a0` clean; `git tag -l` empty (no tag created, as directed).
**Review date:** 2026-11-23. **Reviewer environment:** venv from `tools/requirements-validation.txt`, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, backend `0.14.5`, `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`; retrieval probes under `python -S -B`.

**STATUS:** PASS (both findings resolved; no blocking findings; no required corrections)

## Nothing moved except the three documentation files

- `git diff 65120fa..6fcd1a0` touches exactly `docs/workflows/retrieval.md`, `docs/release/README.md` and `opendss_altdss_library/README.md` (the handoff file itself was added by `65120fa`; the range `246b343..6fcd1a0` is those three plus that handoff). No data, schema, tool, catalog, example, fixture, golden, `requirements-validation.txt`, `manifest.json` or plan change; all three goldens byte-identical to `246b343` (`f72d59d8…`, `0f8d5400…`, `b06282a6…`).
- Regressions re-run on the pinned stack: `validate_catalogs.py` **19/19** PASS; `search_catalogs.py --check` exit 0 with `Object index check: PASS` and `Symbol alias check: PASS (1 registered)`; `run_examples.py` **19/19**; `run_fixtures.py` **3/3**. `skill.md` remains 64 lines. No added line restates a verified count (scanned the diff: none of 1878/2012/460/461/1094/926/2200/144/180 appears in the added lines).

## R-1 — the alias registry is now documented where the corpus is described

- `docs/workflows/retrieval.md` query rules now state that the classic `TapNumber` spelling returns `TapNum` records via a registry declaring alias, canonical symbol, element class, record IDs and source IDs, that removing the row removes the alias hits, and that the registry and its schema are the nineteenth validation pair — with working links to `references/symbol_aliases.json` and its schema.
- The `--check` description now covers the alias section: resolving every registered record ID and source ID, verifying each listed record carries the canonical symbol for the declared element class, rejecting duplicate aliases and exact-symbol collisions, and the `Symbol alias check: PASS (n registered)` output line.
- The exit-code table now reads exit 0 = "both the index and alias checks passed" and exit 1 = "the index or alias check failed".
- The library README inventory has the one-line entry for the schema-validated `TapNumber` → `TapNum` registry with its record IDs.
- All links in all four touched files (including the handoff) resolve to existing files.
- These statements describe behaviour I ran, not inferred: `--check` printed both PASS lines with exit 0 on the committed tree, and in the 5.3 review's scratch copies the empty registry, bogus record ID, missing canonical symbol, wrong-class record, missing source ID and exact-symbol collision each produced exit 1 with the alias named, while an empty registry dropped `--symbol TapNumber` to zero hits (exit 1) with direct `--symbol TapNum` unaffected.

## F-2 — the `Official-current` scope clause is in place

- The sentence under the validation-levels table states that the 17-file search corpus deliberately excludes the legacy Line/LineCode catalog, the repository's sole catalog with `Official-current` labels, retained for provenance and outside schema validation and search, with a link to the legacy file. It claims neither validation nor search for the file and adds no counts to the table.
- The underlying facts re-verified: `references/lines/opendss_line_linecode_properties_legacy.json` holds 2 class records and 66 property rows carrying exactly **63 `Official-current`** and **3 `Official-versioned`** labels (the only `Official-current` rows in the repository); it is matched by neither the retrieval glob (`references/*/*_properties.json` — 9 files) nor `SCHEMA_PAIRS` (19 pairs, zero legacy entries), and `search_catalogs.py`/`validate_catalogs.py` contain no legacy reference. The release table's `Official-current = 0` therefore stands for the defined corpus, now with the exclusion explicit per the owner's scope-clause choice (file stays in place).

## Required corrections

None.

No files were modified by this review; this report is the only file added. With R-1 and F-2 resolved, Phase 5.3 is ready for owner acceptance (version and tag decision remain the owner's).
