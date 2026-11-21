# Phase 1 External Audit Report

**Audit type:** Independent Phase 1 audit per `PHASE_1_EXTERNAL_AUDIT_HANDOFF.md`
**Auditor:** DeepSeek (external model, owner-selected)
**Source checks performed:** 2026-11-13 (GitHub API, PyPI JSON API, live documentation site, SourceForge API)
**Report prepared:** 2026-11-14
**Artifacts reviewed:** `OpenDSS_AltDSS_Library_Charter.md`, `README.md`, `PHASE_1_SOURCE_INVENTORY.md`, `PHASE_1_EXTERNAL_AUDIT_HANDOFF.md`
**Repository changes made by audit:** none (read-only review)

**Current owner decision:** The report's unresolved support-target question was resolved after the audit. The project selected the stable target: AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. Other findings remain historical audit findings and are tracked in the source inventory and package manifest.

The report's finding that the Phase 1 exit gate was not satisfied describes the repository at the time of the audit. The current Phase 1 package foundation, schemas, handoffs, and starter Line/LineCode catalog are now present; remaining catalog remediation is assigned to Phase 2.

---

## Audit status

**Pass with findings — the Phase 1 exit gate is not yet satisfied.** The inventory exists and most recorded version numbers are individually correct, but the central docs↔release comparison is only partly done, two links in the audit trail are broken, and the "latest release observed" figures miss a coordinated 2026 beta line that changes what "current" means.

All checks below were performed on 2026-11-13 against the GitHub REST API, the PyPI JSON API, the live `dss-extensions.org` documentation site, and the SourceForge project API.

---

## 1. Version alignment (verified against primary sources)

| Package | Docs banner (live) | Docs build ref | Latest stable | Latest prerelease | Default branch HEAD | Changelog coverage |
|---|---|---|---|---|---|---|
| AltDSS-Python (`altdss`) | 0.2.3 | `gh-pages` HEAD `a712ac4c`, msg "0.2.3" (2024-03-19) | 0.2.4 (GitHub + PyPI) | **0.3.0b2** (PyPI 2026-02-26; tag `0.3.0b2`) | `main` `2b6fa7e5` = 0.2.4 tag (2024-03-29) | `docs/changelog.md` stops at 0.2.4; **no 0.3.0 entry even at tag `0.3.0b2`** |
| DSS-Python (`dss`) | 0.15.4 | `gh-pages` HEAD `e2f8010b`, msg "0.15.4" (2024-03-13) | 0.15.7 | **0.16.0b1/b2** (PyPI 2026-02-20/26); also 0.15.8a1 (2024-06-26, **no GitHub tag**) | `master` `85783cf8` (2024-03-21) — *older than 0.15.7* | Tag `0.15.7` changelog tops at **0.15.6**; docs changelog tops at 0.15.4 |
| OpenDSSDirect.py (`opendssdirect`) | 0.9.1 | `gh-pages` HEAD `c2688af1` (2024-02-25) | 0.9.4 | **v0.10.0b1/b2 tags exist, not on PyPI** | `master` `d654af20` = v0.9.4 | **No changelog file in repo or docs**; GitHub Releases only |
| DSS C-API (`dss_capi`) | n/a (Doxygen) | — | 0.14.5 | 0.15.0b4 (2026-02-26) | `master` `f5728aec` (2024-07-11), **263 commits behind tag 0.15.0b4** | `master/docs/changelog.md` has **no 0.15.0 section**; the tag's does (marked "not released") |
| EPRI OpenDSS | — | — | Site page: **10.0.0.1 "Columbus"** | — | — | SourceForge best release: `OpenDSSInstaller_1100_1.exe`, 2026-01-30 → **11.0.0.1** |

---

## 2. Findings

### High

**H1 — AltDSS-Python mismatch is understated (stale docs *plus* release/source-selection issue).**
`PHASE_1_SOURCE_INVENTORY.md` ALT-01/ALT-03 and coverage map line 62 present this as "docs 0.2.3 vs release 0.2.4". Verified: 0.2.3 docs are correct, 0.2.4 is the last GitHub Release, **but PyPI `altdss` 0.3.0b1/b2 were published 2026-02-26**, tag `0.3.0b2` is 19 commits ahead of `main`, and `main` HEAD is still the 0.2.4 commit. So `main` is *not* the 0.3 line; the beta lives on branch `fastdss` (`247ffeeb`, 2026-02-27).
*Correction:* record docs=0.2.3, stable=0.2.4, current beta=0.3.0b2, and state that `main` ≠ beta branch. Classification per handoff: stale documentation + release/source-selection issue. Cite tag `0.3.0b2`, PyPI upload timestamp, and `main` commit `2b6fa7e5`.

**H2 — AltDSS-Python changelog evidence is broken and incomplete.**
ALT-03 links `https://dss-extensions.org/AltDSS-Python/CHANGELOG.html` → **HTTP 404**. The working page is `/AltDSS-Python/changelog.html` (banner 0.2.3, top entry 0.2.3). Additionally, `docs/changelog.md` at tag `0.3.0b2` still has no 0.3.0 section, so the required "compare the docs version with the … change log" comparison could not have been completed as written.
*Correction:* fix the URL and record "changelog has no 0.3.x entry; only PyPI upload + tag exist" as the documented gap.

**H3 — DSS-Python: the changelog does not document 0.15.7 (release-notes deficiency).**
At tag `0.15.7`, `docs/changelog.md` top section is 0.15.6; the 0.15.7 change is only in the GitHub release body (LineGeometries API returns all conductors). The docs changelog (0.15.4) is therefore two minor versions behind. Also, `master` HEAD (`85783cf8`, 2024-03-21) predates the 0.15.7 tag (`c59181aa`, 2024-03-29) — the 0.15.7 code is on branch `0.15.x`. And PyPI carries **0.16.0b2** (2026-02-26) plus an untagged 0.15.8a1.
*Correction:* split the row into stable (0.15.7), beta (0.16.0b2), and "untagged PyPI artifact" (0.15.8a1); cite branch `0.15.x` for the stable tag; classify the 0.15.7 changelog as missing.

**H4 — OpenDSSDirect.py has no change log to compare.**
Repo tree at `v0.9.4` contains no `*changelog*`/release-notes file under `docs/`. The handoff's requirement is satisfiable only via the GitHub Releases page (already cited in ODD-03), which should be stated explicitly. Tags `v0.10.0b1/b2` exist (branch `fastdss`) but are not on PyPI; v0.10 raises `requires-python` to ≥3.11 and pins `dss-python==0.16.0b2`.
*Correction:* note "release page is the sole change log"; add the unpublished beta tags so a later reader does not mistake 0.9.4 for the newest code.

**H5 — DSS C-API rows cite the wrong ref; `master` is ~2 years stale.**
DSSX-03/04/05 cite `master`. Verified: `master` HEAD `f5728aec` (2024-07-11) is **263 commits behind** tag `0.15.0b4` (`e936d210`, 2026-02-25, on branch `0.15.x`). `master/docs/changelog.md` has no 0.15.0 section; the tag's has one but marks 0.15.0 "not released", and actual beta changes appear only in the GitHub release body (e.g. b4: JSON input, cross-validation against OpenDSS v11, pending `DynamicExp` issue). `docs/known_differences.md` also differs materially (`master` 14,335 chars vs tag 19,455).
*Correction:* replace `master` with tag `0.15.0b4` (or branch `0.15.x`) in DSSX-04/DSSX-05, and record that known-differences content is ref-dependent. Keep the existing "pin a tag" warning but make it a stated finding, not a caution.

**H6 — EPRI "What's New" is stale relative to the distributed release.**
`opendss.epri.com/Whatsnew.html` shows 10.0.0.1 "Columbus" (© 2024) while the same page's boilerplate still says "Version 9 is the latest update." SourceForge `best_release.json` reports `OpenDSSInstaller_1100_1.exe`, dated **2026-01-30** (v11.0.0.1), and `dss_capi` 0.15.0b4 release notes state results were "cross-validated with OpenDSS v11."
*Correction:* change EPRI-08 from "whether this is the newest stable release is not established" to **stale documentation**, citing both the page and the SourceForge artifact. Keep the page as `Official-versioned` for 10.0.0.1 content; do not treat it as describing the current installer.

### Medium

**M1 — The 2026 beta set is a hard-pinned, mutually dependent line that the inventory does not record.**
`altdss==0.3.0b2` requires `dss_python>=0.16.0b2,<0.17`, `dss_python_backend==0.15.0b4`, `numpy>=2,<3`, Python ≥3.11. `dss-python==0.16.0b2` requires backend `0.15.0b4`, numpy ≥2, Python ≥3.11. `opendssdirect.py v0.10.0b2` pins `dss-python==0.16.0b2`. By contrast the stable line is Python ≥3.7 / numpy ≥1.21 / backend 0.14.5. This affects the charter's stop gate ("target version stated") and belongs in the inventory as a version-coupling note, not a decision.

**M2 — "Latest release observed" conflates GitHub Releases with the installable package channel.**
For all three Python packages the stable figures are right for GitHub Releases but the package index now carries newer prereleases. Recommend separate columns: `GitHub latest release`, `PyPI latest stable`, `PyPI prerelease`, `default-branch HEAD`.

**M3 — Internally inconsistent exit checklist.**
Lines 84–85 mark "Version mismatches and source-release selection are reconciled" as checked `[x]` while its own audit sub-item is `[ ]`. Given H1–H6, the parent item is not reconciled; only the owner's confirmation that a mismatch exists is.

**M4 — `master`/`main` branch assumptions.**
ALT-02/PY-02/ODD-02 correctly warn that default branches are mutable, but their recorded default-branch contents are stale for AltDSS-Python (`main` = 0.2.4 only) and DSS-Python (`master` predates 0.15.7). A reader following the record to clone `main`/`master` would not get the version discussed in the same row.

### Verified accurate (no action)

- Docs banners exactly 0.2.3 / 0.15.4 / 0.9.1 (page `<title>` and logo alt text).
- GitHub latest stable releases 0.2.4 / 0.15.7 / v0.9.4; `dss_capi` 0.14.5 stable and 0.15.0b4 prerelease.
- ODD-02's `dss-python==0.15.7` pin at `v0.9.4` — confirmed in `pyproject.toml`.
- Dynamic version derivation (`versioningit`) in all three Python repos.
- FW-01: pinned template commit resolves and contains exactly the seven labels, including `Observed-export`.
- XREF-01 URL `/python_apis` resolves (200).
- EPRI-09's statement that installers are posted irregularly via SourceForge — confirmed.

---

## 3. Coverage gaps

1. **No version-alignment artifact.** The comparison lives only as prose inside rows; there is no single table with columns `source → docs version/build ref → stable tag → prerelease tag → default-branch HEAD → changelog coverage → classification → evidence URL → date`.
2. **No per-package changelog coverage statement** (which release range is documented where), which is why H2–H5 were invisible.
3. **EPRI release artifact not examined** — now partially mitigated (filename, size 148,463,752 bytes, date 2026-01-30, MD5 from SourceForge), but the installer/Help output was not opened, so page-level command/property currency cannot be asserted.
4. **Examples still unenumerated** (already declared at EPRI-04 / exit item line 86) — unchanged by this audit.
5. **No record of the `dss-python-backend` package as a distinct versioned artifact**, even though it is the actual engine carrier (`0.14.5` for the stable line, `0.15.0b4` for the beta line).

---

## 4. Unresolved owner decisions

1. **Support line:** 0.2.4 (Python 3.7+, NumPy 1.x, engine 0.14.5) versus 0.3.0b2 (Python 3.11+, NumPy 2, engine 0.15.0b4). These are not a patch apart; they are different platform baselines.
2. **Docs-as-evidence policy:** whether 0.2.3 docs may back `Official-versioned` claims about 0.2.4 (one patch gap) and, if the beta is chosen, whether any docs may be cited for 0.3.0 at all.
3. **Prereleases in the catalog:** whether beta tags (`0.3.0b2`, `0.16.0b2`, `v0.10.0b2`, `0.15.0b4`) are admissible evidence records or only `Unverified` context.
4. **Authoritative change log:** which source wins when the docs changelog and the repo changelog disagree (as they do for DSS-Python 0.15.5–0.15.7).
5. **Untagged artifact:** how to treat PyPI `dss-python 0.15.8a1`, which has no corresponding GitHub tag or release.

---

## 5. Suggested Phase 1 exit criteria (objective)

- [ ] A single `docs ↔ release ↔ tag ↔ branch ↔ changelog` table exists, one row per package, each cell carrying a URL/tag/commit and a check date.
- [ ] Each mismatch is labelled **stale documentation**, **release/source selection**, or **unresolved pending direct evidence** — with no row left implicitly "resolved".
- [ ] Stable and prerelease channels are recorded separately (GitHub Releases vs PyPI), including any tag/PyPI divergence.
- [ ] Every cited changelog URL returns HTTP 200 and the cited section exists in the page at that ref.
- [ ] Every "pin a tag" advice names the correct ref (e.g. `dss_capi@0.15.0b4`, not `master`) and the ref is verified to contain the discussed code.
- [ ] The EPRI baseline states both the documentation page version and the distributed installer version, with the divergence classified.
- [ ] Each of the five namespaces has at least one record whose docs version, release tag, and engine/backend dependency are stated.
- [ ] Remaining open decisions in §4 are answered by the project owner and recorded as decisions, not inferred.
