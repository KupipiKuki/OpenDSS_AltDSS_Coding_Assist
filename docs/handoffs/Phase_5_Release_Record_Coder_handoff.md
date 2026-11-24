# Phase 5 Package 5.3 — Release record (coder handoff)

**Issued** 2026-11-23 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** packages 5.1 and 5.2, accepted as decisions 23 and 24. **Scope authority** charter step 7 and plan section 7.
**Paths** as in the 5.2 handoff: library paths (`tools/…`, `references/…`, `schemas/…`, `skill.md`) are relative to `opendss_altdss_library/`; `CHANGELOG.md` and anything under `docs/` are relative to the repository root.

## Goal

Close Phase 5 and satisfy the charter's release step: *"package the skill with a manifest listing package versions, source check date, validation levels, known gaps, and supported tasks."* Plus the one piece of 5.2 that should live in data rather than code — the `TapNumber` alias.

Nothing here invents new knowledge. This package makes what exists legible, dated and checkable, and it is judged on that: a release record that overstates coverage is worse than none.

## Deliverable 1 — `CHANGELOG.md` at the repository root

One entry per phase, oldest first, each with the date the work landed, the owner decisions that shaped it, and the artifacts delivered. Rules:

- Every date must be one `git log` supports. Do not backfill a date that no commit carries.
- Every entry names decisions by number where one applies (13 through 24 are recorded in the plan).
- No "various improvements". If an entry cannot name a file, a commit or a decision, it does not belong.

Phases to cover: Phase 1 foundation, Phase 2 Line/LineCode pilot, Phase 3A catalogs, Phase 3B element packages 1–6, Phase 4.1–4.5, Phase 5.1–5.3.

## Deliverable 2 — `docs/release/README.md`, the release record

Five sections, because the charter names five things. Keep them separate and named; a reviewer should be able to tick each one off.

1. **Package versions.** `manifest.support_targets` verbatim, plus the engine build line `DSS C-API 0.14.5 revision 87d85c2…`, and the validated environment: Python 3.14.6 on Windows 11 AMD64. State plainly that the beta package line is documented as future compatibility and not validated.
2. **Source check date.** `source_check_date` from the manifest, what it covers (the pinned source inventory), and the standing caution that EPRI online documentation does not state one OpenDSS version, so version-sensitive claims cite a pinned release instead.
3. **Validation levels.** A table over the seven evidence values, each with its measured record count and what it licenses. The measured totals at the 5.2 head are:

   | Level | Records | What it licenses |
   |---|---|---|
   | `Official-versioned` | 1878 | tied to a pinned release, file and line, or a tagged package |
   | `Observed-working` | 51 | 19 examples, 16 troubleshooting records, 16 object-index records reproduced on the pinned stack |
   | `Official-current` | 0 | — |
   | `Observed-export`, `Example-only`, `Inferred` | 0 | — |
   | `Unverified` | **1** | `Line.epsrmedium`, held from the Phase 2 starter catalog |

   Re-measure rather than trusting this table, and **name the single `Unverified` record explicitly**. A release that hides its one open question has used up the trust the other 1878 records earned. The 1878 resolves as 461 element property rows + 180 wrapper methods + 1094 wrapper properties + 143 engine records; the 51 as 19 + 16 + 16, keeping the arithmetic visible.
4. **Known gaps.** The manifest's 16 `known_gaps` entries, reorganised for reading but not softened, plus the three Phase 4 scope limits (no year-long QSTS, no harmonics, no unbalanced-fault study), the 8 classes deferred by decision 17, and the cross-interface caveat that wrapper agreement speaks to the API layer and not to the numerics.
5. **Supported tasks.** One row per task area, and every row must name a workflow page **and** at least one example id or fixture run that exercises it. Derive the rows from what exists — 10 workflow pages, 19 examples, 3 fixture runs — not from what would be nice. A task with no example and no fixture is a gap, not a supported task.

Close with a short **what this release does not claim** list: not a numerical validation of the engine, not coverage of the deferred classes, not a substitute for the pinned primary sources.

## Deliverable 3 — the alias registry, so `TapNumber` stops being a special case

The 5.2 review found the one durable risk in the retrieval tool: the `TapNumber` → `TapNum` mapping is a hard-coded `elif` keyed to three literal record ids, so a rename loses it silently. Move it into validated data.

`references/symbol_aliases.json`:

```json
[
  {
    "alias": "TapNumber",
    "canonical": "TapNum",
    "element_class": "RegControl",
    "record_ids": ["RegControl.tapnum", "altdss.RegControl:RegControl.TapNum", "capi-regcontrol-tap-number"],
    "source_ids": ["opendssdirect-active-regulator-tap"],
    "notes": ["Classic COM spelling retained by DSS-Python and OpenDSSDirect.py for the same engine tap."]
  }
]
```

- New schema `schemas/catalogs/symbol_aliases.schema.json`, array of records, `additionalProperties: false`, `alias`/`canonical`/`element_class` non-empty, `record_ids` `minItems: 1` and unique, `source_ids` `minItems: 1`. Register the pair in `tools/validate_catalogs.py` so the run goes **18 → 19**.
- `search_catalogs.py` reads the registry and drops the hard-coded branch. Behaviour at the CLI must not change: `--symbol TapNumber` still returns the same three hits with the same labels.
- `--check` gains an **alias section**: every `record_ids` entry must exist in the corpus, every listed record must actually carry the canonical symbol, every `source_ids` id must resolve, and no alias may collide with a symbol that already matches exactly. A failure exits 1 naming the alias.

## Deliverable 4 — `skill.md`

- The "Phase placement" paragraph is stale: it says Phase 3B continues and Phases 4–5 are planned. Rewrite it to the closed state in the same voice.
- Add the retrieval tool and the release record to "Where to look", and one line stating that the release record carries the validation levels and known gaps.
- Keep it under 90 lines (it is 63 today), keep every existing link, and do not turn it into a second release record.

## Deliverable 5 — `docs/audits/phase5_release_audit.md`

Commands, versions, the 19/19 pair count, the changelog traceability check, `skill.md` line count, and a checklist mapping each of the charter's five release items to the section of `docs/release/README.md` that satisfies it. Include the alias demonstration described in acceptance 2 and 3.

## Do not

- **Do not create a git tag** and do not edit `manifest.json` or `docs/implementation_plan.md`. The version decision and the tag are the owner's, and the architect applies them at acceptance. Recommend a version in the audit if you want a view; do not act on it.
- Do not invent history in the changelog, and do not soften a known gap.
- Do not add catalogs beyond the alias registry, and do not touch element catalogs, schemas other than the two named, examples, fixtures, goldens, or `requirements-validation.txt`.

## Acceptance

1. `validate_catalogs.py` passes **19/19**, with the alias registry as the nineteenth pair.
2. `--symbol TapNumber` output is unchanged from 5.2, and it is now driven by data: in a scratch copy, removing the alias record makes `--check` fail and drops the alias hits. Both halves shown in the audit.
3. `--check` passes on the committed tree, includes the alias section, and exits 1 when a `record_ids` entry is corrupted.
4. The release record carries all five charter items as named sections; the `Unverified` record is named; every count in it matches a measurement you show; every supported task names a workflow and an example or fixture run.
5. Every `CHANGELOG.md` date is one `git log` supports, and every entry names a decision, a file or a commit.
6. `skill.md` is under 90 lines, its phase paragraph is current, and all links resolve.
7. `run_examples.py` 19/19 and `run_fixtures.py` 3/3 still pass; `git diff` stays inside `CHANGELOG.md`, `docs/`, `references/symbol_aliases.json`, its schema, `tools/validate_catalogs.py` (the pair only) and `tools/search_catalogs.py`.
