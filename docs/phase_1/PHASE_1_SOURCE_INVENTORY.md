# Phase 1 Source Inventory

**Inventory status:** Phase 1 inventory audited; owner decisions recorded; source enumeration continues in Phase 2  
**Project:** OpenDSS and AltDSS Reference Library  
**Inventory reviewed:** 2026-11-13  
**Source check date:** 2026-11-13  
**Support target:** AltDSS-Python 0.2.4 / DSS-Python 0.15.7 / backend 0.14.5 (stable line)  
**Runtime validation:** None performed in Phase 1

## Purpose and reading notes

This inventory records the primary source families and local project material identified for Phase 1 in `OpenDSS_AltDSS_Library_Charter.md`. It distinguishes upstream EPRI OpenDSS references from DSS-Extensions' alternative engine and Python bindings. Documentation site versions and repository release versions are recorded separately when they differ. The inventory snapshot is distinct from the support target decision recorded in the charter.

Evidence labels follow the [Coding Assistant Skill Framework template](https://github.com/KupipiKuki/coding_assistant_framework_skill/blob/25feceea8490f42c4b7079b1e8a3a62b4523d80d/Coding_Assistant_Skill_Framework_Template.md). `Observed-working` is reserved for code run in a recorded target environment; no such execution has been done for this inventory. `Observed-export` means captured from a real application export or runtime inspection, and likewise is not currently assigned to any project behavior record.

### Version Alignment & Channel Matrix (Audited 2026-11-14)
| Package | Docs Banner | GitHub Latest Stable | PyPI Latest Stable | PyPI Prerelease | Repository Ref or Distribution Channel | Changelog Coverage | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AltDSS-Python** | 0.2.3 | 0.2.4 | 0.2.4 | 0.3.0b2 | `main` = 0.2.4; `fastdss` = 0.3.0b2 | Docs changelog tops at 0.2.3; tagged repo changelog has 0.2.4 but no 0.3.x entry | Stable target; beta noted |
| **DSS-Python** | 0.15.4 | 0.15.7 | 0.15.7 | 0.16.0b2; untagged 0.15.8a1 | `0.15.x` contains tag 0.15.7; `master` predates it | Tag 0.15.7 changelog tops at 0.15.6 | Stable dependency and comparison API |
| **OpenDSSDirect.py** | 0.9.1 | v0.9.4 | 0.9.4 | None for the audited beta tags | `master` = v0.9.4; GitHub tags v0.10.0b1 and v0.10.0b2 on the beta line | GitHub Releases | Comparison only |
| **DSS C-API** | n/a | 0.14.5 | n/a | n/a | Stable tag `0.14.5`; beta tag `0.15.0b4` on `0.15.x`; `master` predates the beta | Changelog varies by tag; beta details in GitHub Releases | Stable engine target (0.14.5) |
| **dss-python-backend** | n/a | See DSS C-API | 0.14.5 | 0.15.0b4 | PyPI distribution of the DSS C-API engine for Python | Engine change history in DSS C-API | Pinned runtime dependency |
| **EPRI OpenDSS** | 10.0.0.1 | n/a | n/a | n/a | SourceForge: 11.0.0.1 (2026-01-30) | "What's New" shows 10.0.0.1 | Docs stale vs. distributed |

*Note: Per audit findings H1-H6, `master`/`main` branches are mutable and often stale. All extraction and validation will pin to specific stable tags (e.g., `altdss@0.2.4`, `dss-python@0.15.7`, `dss_capi@0.14.5`).*

The completed audit comparison and finding-by-finding disposition are recorded in [PHASE_1_AUDIT_DISPOSITION.md](PHASE_1_AUDIT_DISPOSITION.md). Version values in this matrix are the dated audit snapshot, not a live release check.

## Source inventory

| ID | Source and publisher | URL or path | Version / revision observed | Scope and topics | Evidence / known gaps |
|---|---|---|---|---|---|
| EPRI-01 | [OpenDSS Documentation home](https://opendss.epri.com/) — Electric Power Research Institute (EPRI) | `https://opendss.epri.com/` | Site presents mixed-version documentation; no single site-wide version identified | Official OpenDSS concepts, commands, object/property help, interfaces, workflow, and supporting documents | `Official-current` only for material verified against the intended EPRI release; individual pages may be version-specific or undated. Site home timed out during this check; linked EPRI pages below were inspected directly. |
| EPRI-02 | [Basics of the OpenDSS Scripting Language](https://opendss.epri.com/BasicsoftheOpenDSSScriptingLangu.html) — EPRI | Same | No explicit version on page | DSS text command language, scripts, command sources, compile/redirect patterns | Direct language overview; exact command/property availability still needs version-specific Help/reference checks. |
| EPRI-03 | [Circuit Model Concept](https://opendss.epri.com/CircuitModelConcept.html) — EPRI | Same | No explicit version on page | RMS distribution circuit model, power delivery and power conversion elements, buses/nodes, controls | Conceptual page; does not replace exact class property references or versioned behavior. |
| EPRI-04 | [Examples, Docs and Test Cases](https://opendss.epri.com/ExamplesDocsandTestCases.html) — EPRI | Same; links to downloadable source/example folders | No single version stated on index | Example circuits, scripting templates, Python/Matlab/C# COM examples, IEEE PES test cases, EPRI test circuits | Index page covers many folders; examples must be individually indexed with path, dependencies, stated version, and execution status. Inspection of all downloadable files remains outstanding. |
| EPRI-05 | [Basic Examples](https://opendss.epri.com/BasicExamples.html) — EPRI | Same | No explicit version on page | Small introductory DSS examples and circuit construction patterns | Example-only unless independently executed. Example coverage is not exhaustive. |
| EPRI-06 | [COM Interface](https://opendss.epri.com/COMInterface.html) — EPRI | Same | Page copyright 2024; interface/version applicability not specified | Official OpenDSS COM interface purpose and use, text command access, programmatic modeling/results | Does not provide a full machine-readable signature catalog; version and platform details require specific release docs. |
| EPRI-07 | [OpenDSS Shared library — DirectDLL](https://opendss.epri.com/OpenDSSSharedlibrary-DirectDLL1.html) — EPRI | Same | Page copyright 2024; interface/version applicability not specified | Official EPRI OpenDSS DirectDLL description and relationship to COM | This is the EPRI DirectDLL, not DSS C-API. Page is descriptive, not a complete API catalog. |
| EPRI-08 | [What's New](https://opendss.epri.com/Whatsnew.html) — EPRI | Same | Page explicitly displays OpenDSS 10.0.0.1 “Columbus”; Stale documentation (shows 10.0.0.1, but SourceForge distributes 11.0.0.1). Used for conceptual baseline only. | Official release/change notes | [Downloads](https://opendss.epri.com/Downloads.html) says releases are posted irregularly and points to SourceForge plus beta builds; exact current supported build remains to be selected and verified. |
| EPRI-09 | [Downloads](https://opendss.epri.com/Downloads.html) — EPRI | Same; official release installers linked through SourceForge | Page does not give a fixed version | Official release installers and beta builds | Release cadence is irregular. This inventory did not inspect/download installers or determine the latest stable/beta build. |
| DSSX-01 | [DSS-Extensions overview](https://dss-extensions.org/) — DSS-Extensions | `https://dss-extensions.org/` | Current site; no single engine/package version | Alternative/community OpenDSS implementation; package map; supported languages; distinction between DSS-Python, OpenDSSDirect.py, and AltDSS-Python | Project orientation only. Keep this source separate from EPRI's official implementation and consult specific package/API sources for behavior. |
| DSSX-02 | [DSS C-API and dss.hpp documentation](https://dss-extensions.org/dss_capi/) — DSS-Extensions | `https://dss-extensions.org/dss_capi/` | Page describes `dss.hpp` as work in progress; no C-API release pinned on landing page | Low-level C API, C++ header API, `dss::classic` and `dss::obj` namespaces | API docs are mixed across C API and `dss.hpp`; `dss.hpp` is explicitly WIP and must not be treated as AltDSS-Python. Pin repository release/tag for catalog records. |
| DSSX-03 | [DSS C-API repository](https://github.com/dss-extensions/dss_capi) — DSS-Extensions | Repository default branch `master` | Latest stable release observed: `0.14.5`; latest listed prerelease observed: `0.15.0b4` | AltDSS/DSS C-API engine, C headers, source, builds, tests, examples, engine API | Prerelease notes identify known pending issues and validation. Do not equate a prerelease with supported stable version. Branch tip is mutable; use a tag/commit for reproducible records. |
| DSSX-04 | [DSS C-API 0.14.5 release notes](https://github.com/dss-extensions/dss_capi/releases/tag/0.14.5) and [tagged changelog](https://github.com/dss-extensions/dss_capi/blob/0.14.5/docs/changelog.md) — DSS-Extensions | Release notes and `docs/changelog.md` | Stable tag `0.14.5`; the audit tracks beta `0.15.0b4` separately | Engine and low-level API changes, compatibility updates, fixes, extensions | The changelog includes multiple releases and planned items. Cite an explicit release section or tagged release note for a version-specific claim. |
| DSSX-05 | [Known differences at 0.14.5](https://github.com/dss-extensions/dss_capi/blob/0.14.5/docs/known_differences.md) — DSS-Extensions | `docs/known_differences.md` at tag `0.14.5` | Stable tag `0.14.5` | Documented behavior differences between DSS-Extensions engine and official OpenDSS | The audit found ref-dependent content. Use the tag that applies to the claim. |
| DSSX-06 | [dss-python-backend 0.14.5 on PyPI](https://pypi.org/project/dss-python-backend/0.14.5/) — DSS-Extensions | Versioned package listing and wheel files | `0.14.5`; listing checked 2026-11-20 | Python distribution of the native DSS C-API engine and its low-level bindings | `Official-versioned` package metadata. The target environment has yet to be run. |
| ALT-01 | [AltDSS-Python documentation](https://dss-extensions.org/AltDSS-Python/) — DSS-Extensions | `https://dss-extensions.org/AltDSS-Python/` | Documentation banner: `0.2.3` | `altdss` objects, properties, methods, batches, enums, getting started, examples, API reference | Documentation page version differs from latest repository release observed (`0.2.4`). Verify page/package alignment before relying on version-sensitive signatures. The docs state examples are still being added. |
| ALT-02 | [AltDSS-Python repository](https://github.com/dss-extensions/AltDSS-Python) — DSS-Extensions | GitHub default branch `main` | Latest release observed: `0.2.4`; package version is dynamically derived from VCS metadata in `pyproject.toml` | Python package implementation, source declarations, tests, documentation, examples, dependency metadata | Repository contents are mutable; API extraction should use the selected `0.2.4` release tag, not `main`. |
| ALT-03 | [AltDSS-Python releases](https://github.com/dss-extensions/AltDSS-Python/releases) and [documentation changelog](https://dss-extensions.org/AltDSS-Python/changelog.html) — DSS-Extensions | Release page and versioned docs | Stable `0.2.4`; docs banner `0.2.3`; beta `0.3.0b2` | Version changes and package release information | DeepSeek completed the docs/release/changelog comparison; see the audit disposition and external report. |
| PY-01 | [DSS-Python documentation](https://dss-extensions.org/DSS-Python/) — DSS-Extensions | `https://dss-extensions.org/DSS-Python/` | Documentation banner: `0.15.4` | `dss` package/classic COM-like API, enums, getting started, plotting, examples, limitations | Docs label API extensions, but say not all are marked. Docs version differs from latest release observed (`0.15.7`). |
| PY-02 | [DSS-Python 0.15.7 source](https://github.com/dss-extensions/DSS-Python/tree/0.15.7) — DSS-Extensions | Tag `0.15.7` on the `0.15.x` branch | Stable release `0.15.7`; package metadata derives version dynamically | Python bindings, API wrappers, tests, package/dependency metadata, examples | Import package is `dss`. Record the backend dependency and engine version separately. |
| PY-03 | [DSS-Python releases](https://github.com/dss-extensions/DSS-Python/releases) and [documentation changelog](https://dss-extensions.org/DSS-Python/changelog.html) — DSS-Extensions | GitHub releases and docs changelog | Stable `0.15.7`; docs banner `0.15.4`; beta `0.16.0b2` | Package changes, dependency/engine relationships, release guidance | DeepSeek completed the docs/release/changelog comparison; see the audit disposition and external report. |
| ODD-01 | [OpenDSSDirect.py documentation](https://dss-extensions.org/OpenDSSDirect.py/) — DSS-Extensions | `https://dss-extensions.org/OpenDSSDirect.py/` | Documentation banner: `0.9.1` | `opendssdirect` function-style/class-based package API, examples, installation, API reference | Docs banner differs from latest release observed (`0.9.4`). Import namespace and call style must remain distinct from `dss` and `altdss`. |
| ODD-02 | [OpenDSSDirect.py repository](https://github.com/dss-extensions/OpenDSSDirect.py) — DSS-Extensions | Default branch `master` | Latest release observed: `0.9.4`; `pyproject.toml` pins `dss-python==0.15.7` | Package source, API implementation, tests, examples, package dependencies | Package depends on DSS-Python but remains a separate API namespace and package. Mutable branch; pin tag/commit for exact API records. |
| ODD-03 | [OpenDSSDirect.py releases](https://github.com/dss-extensions/OpenDSSDirect.py/releases) and [Getting Started](https://dss-extensions.org/OpenDSSDirect.py/notebooks/GettingStarted.html) — DSS-Extensions | GitHub releases and docs | Stable `0.9.4`; docs banner `0.9.1`; beta tags `v0.10.0b1/b2` | Release changes and usage examples | DeepSeek completed the docs/release/changelog comparison; see the audit disposition and external report. The examples are `Example-only` until run in a named environment. |
| XREF-01 | [DSS-Extensions Python API comparison](https://dss-extensions.org/python_apis) — DSS-Extensions | `https://dss-extensions.org/python_apis` | Current page; no fixed package versions in the overview | Comparison of EPRI COM, DSS-Python, OpenDSSDirect.py, and AltDSS-Python; architectural relationship | Useful namespace map, but not a substitute for version-pinned package docs. Recheck comparison claims against selected package releases. |
| FW-01 | [Coding Assistant Skill Framework repository](https://github.com/KupipiKuki/coding_assistant_framework_skill) and [framework template](https://github.com/KupipiKuki/coding_assistant_framework_skill/blob/25feceea8490f42c4b7079b1e8a3a62b4523d80d/Coding_Assistant_Skill_Framework_Template.md) — KupipiKuki | Repository default branch and pinned template commit `25feceea8490f42c4b7079b1e8a3a62b4523d80d` | No framework release/version found in inspected README/template metadata | Evidence model, source inventory and package workflow, stop gates, skill template, validation distinctions | Template includes seven labels, including `Observed-export`. Framework repository README is brief; pinned template is the substantive source. |

## Existing local project material

| Path | Publisher / status | Scope | Inventory note |
|---|---|---|---|
| `README.md` | Project repository; local, unversioned working copy | Project purpose: AI-agent-formatted documentation for OpenDSS and AltDSS projects | Brief description only; no source or version metadata. |
| `OpenDSS_AltDSS_Library_Charter.md` | Project repository; draft 0.1, source review date 2026-11-13 | Scope, layer boundaries, data strategy, evidence labels, package layout, source starter set, build sequence, stop gate, open decisions | Primary local scope document. Evidence label list was aligned with the framework in this inventory work by adding `Observed-export`. |
| `PHASE_1_SOURCE_INVENTORY.md` | Project repository; initial source inventory reviewed 2026-11-13 | Source pages, repositories, package docs, release notes, examples index, framework, and existing local files | Initial inventory; contains version discrepancies and audit follow-ups. It is not runtime validation or a compatibility claim. |
| `PHASE_1_EXTERNAL_AUDIT_HANDOFF.md` | Project repository; created 2026-11-13 | Instructions for independent Phase 1 audit and required docs/repository/changelog comparison | Handoff document; DeepSeek completed the audit and the report is stored beside it. |
| `LICENSE` | Project repository | Repository licensing terms | License text is local project metadata, not technical OpenDSS/AltDSS evidence. |
| `opendss_altdss_library/` | Not present at inventory time | Package, catalogs, and schemas | The package was created after this inventory snapshot; current contents and status are summarized in the package README and manifest. |

## Initial coverage map

| Source layer | Inventory coverage | Known gap for later phases |
|---|---|---|
| Official OpenDSS concepts and scripting | EPRI home, scripting overview, circuit model, basic examples, example/test-case index, COM, DirectDLL, What's New, Downloads | No exhaustive object/property page index yet; no release artifact was downloaded; source-indexed examples and target version remain to be selected. |
| AltDSS-Python | Docs, repository, release page, changelog pointer, source/package metadata | Docs/release discrepancy was audited; stable 0.2.4 is selected. Keep docs version and release tag distinct in property evidence. |
| DSS C-API / AltDSS engine | Doxygen landing page, repository, releases, cumulative changelog, known differences | Stable backend 0.14.5 is selected; low-level symbol catalog remains to be populated. |
| DSS-Python | Docs, repository, release page, changelog pointer | Pin the runtime dependency at 0.15.7. Its `dss` API is documented for comparison. |
| OpenDSSDirect.py | Docs, repository, release page, getting started example | Docs/release differences are recorded in the external audit; retained for comparison only. |
| Framework | README and pinned framework template | No formal release tag/version observed; use pinned template commit for reproducibility. |
| Local project materials | Five project files found at repository root, including the source inventory and audit handoff | No existing library package, API catalogs, example collection, schema, or executed AltDSS fixture. |

## Phase 1 decisions and follow-up

1. The source families and implementation priority are stated in the charter. The owner selected the stable package line; workflow conventions remain Phase 2 work.
2. The project owner verified the documentation/release mismatches for AltDSS-Python, DSS-Python, and OpenDSSDirect.py. A required independent check must compare each documentation version against the current repository release/tag and change log before version-sensitive extraction.
3. The EPRI documentation site is not version-uniform. Catalog records must cite specific pages and, when relevant, a named release or installation Help output.
4. The examples index advertises many folders and test circuits. Phase 1 has identified the authoritative index but has not yet enumerated individual example files, their dependencies, or execution status.
5. The repository contains no local circuit fixtures or runtime capture. The later validation phase therefore requires selecting and obtaining a fixture and recording the installed package/backend versions.

## Phase 1 Exit Checklist

- [x] Root-level project files and absence of a pre-existing library package are recorded.
- [x] Every source family named in the charter has at least one source record, including `dss-python-backend`.
- [x] Source publisher, URL/path, version state, review date, topic coverage, and important gaps are represented.
- [x] Project evidence labels match the pinned framework template.
- [x] Project owner reviews the inventory and confirms scope priorities.
- [x] Independent audit (DeepSeek) compared documentation versions against current repository releases/tags and change logs, classified each mismatch (H1-H6), and reported evidence.
- [x] Version mismatches and source-release selection are reconciled: Primary target is Stable line; Beta line is tracked for future notes.
- [x] A single `docs ↔ release ↔ tag ↔ branch ↔ changelog` table exists with check dates.

Phase 1 foundation is **complete with findings**. The package includes the external audit, schemas, manifest, handoffs, and Line/LineCode starter catalog. Phase 2 covers catalog remediation and indexing examples and release notes for the selected tasks. Runtime checks follow in the validation phase.
