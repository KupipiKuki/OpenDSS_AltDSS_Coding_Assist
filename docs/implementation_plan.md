# Implementation Plan — OpenDSS and AltDSS Reference Library

**Plan version** 0.27 (Phase 3B package 6 audited, awaiting owner disposition; Phase 3 exit gate pending)
**Plan date:** 2026-11-22
**Current phase** Phase 3B package 6 (Generator). The owner accepted packages 1 through 5. Package 6 passed coder validation, independent QA/QC (PASS, no required corrections), and the architect review (PASS WITH FINDINGS, nothing blocking), and awaits the owner's disposition. That disposition closes the Phase 3 exit gate and releases Phase 4.
**Target stack:** AltDSS-Python `0.2.4`, DSS-Python `0.15.7`, DSS C-API backend `0.14.5` (beta line documented as future compatibility only)
**Controlling documents:** [Project charter](phase_1/OpenDSS_AltDSS_Library_Charter.md) (build sequence and stop gate) · [Package manifest](../opendss_altdss_library/manifest.json) (machine-readable state) · this plan (work sequencing and gates)

This plan supersedes the phase prose in [Phase 1 README](phase_1/README.md) and the package READMEs where they describe future work. The charter's seven-step build sequence and its stop gate remain in force. Where this plan and the manifest disagree, the manifest carries state and this plan carries intent; both are updated together.

## 1. Where the project stands

| Area | State at this review | Evidence |
|---|---|---|
| Phase 1 foundation | Complete, committed at `3263daa` | Charter, source inventory, external audit, schemas |
| Line/LineCode catalog | Remediated, source-reviewed, independently QA'd, findings resolved | [Audit](audits/line_linecode_schema_audit.md) · [QA/QC report](audits/line_linecode_phase2_qaqc.md) |
| Source index | 99 schema-valid records with versioned source pins where available | [sources.json](../opendss_altdss_library/references/sources.json) |
| Examples | 14 files and 14 records, all `Observed-working` with a recorded environment | [Examples](../opendss_altdss_library/references/examples.json) |
| Schema validation | `tools/validate_catalogs.py` passed 15 of 15 manifest and catalog pairs with Draft 2020-12 format checking | [validate_catalogs.py](../opendss_altdss_library/tools/validate_catalogs.py) |
| Runtime evidence | 14 catalogued examples passed on the pinned stack. Packages 1–6 have readback matrices. | [run_examples.py](../opendss_altdss_library/tools/run_examples.py) · [Generator readback](audits/phase3b_generator_readback.json) |
| API and engine catalogs | 99 generated AltDSS-Python class records and 119 curated DSS C-API engine records | [altdss_python_api.json](../opendss_altdss_library/references/altdss_python_api.json) · [dss_capi.json](../opendss_altdss_library/references/dss_capi.json) · [3A audit](audits/phase3a_api_catalogs_audit.md) |
| Remaining catalogs | Three empty: `opendss_objects`, `python_interface_comparison`, `troubleshooting` | [references/](../opendss_altdss_library/references/) |
| Validation tooling | Committed: `tools/requirements-validation.txt`, `tools/validate_catalogs.py`, `tools/run_examples.py`, `tools/build_altdss_api_catalog.py` | [tools/](../opendss_altdss_library/tools/) |
| Phase 2 commit | Committed as the Phase 2 milestone and merged to `main` on owner approval (2026-11-21) | `git log` |

## 2. Phase map

| Project phase | Charter steps | Objective | State |
|---|---|---|---|
| Phase 1 Foundation | 1–2 Inventory, Normalize | Scope, sources, schemas, package structure, starter catalogs | Complete (`3263daa`) |
| Phase 2 Pilot | 3–4 Extract, Curate | Remediate Line/LineCode; prove the record pattern end to end (catalog, source index, workflow, examples, audit) | Complete and merged (`1d4088f`) |
| Phase 3 Scale-out | 3–4 | API and engine catalogs, then dependency-ordered element packages using the proven pattern | 3A complete; 3B packages 1–3 accepted; package 4 (Load) issued |
| Phase 4 Validation | 6 Validate | Fixture circuits (IEEE 13 and 34 per charter), solved-model checks, property-readback matrices, example upgrade to `Observed-working` | Planned (Section 6) |
| Phase 5 Retrieve and Release | 5, 7 | Search and retrieval over the catalogs; skill packaging; release record | Planned (Section 7) |

## 3. Architect verification performed for this plan

These checks were run during this review to ground the plan. They do not replace the project's recorded evidence; Section 4.2 schedules the recorded run.

- **All catalogs and the manifest validate** against their schemas (`jsonschema` Draft 2020-12, format checker): 9/9 pass, 0 errors.
- **Both workflow examples execute on the pinned stack**: Windows 11 (10.0.26300) AMD64, Python 3.14.6, `altdss==0.2.4`, `dss-python==0.15.7`, `dss-python-backend==0.14.5`.
  - `examples/line_linecode/altdss_lines.py` → `C1/C0 = 3.4 / 1.6`, main length `1.0`, lateral lengths `[0.25, 0.40]`.
  - `examples/line_linecode/lines.dss` via `ctx.Commands(...)` → lengths `1.0 / 0.25 / 0.4`, `C1/C0 = 3.4 / 1.6`, `Units` readback `3` (`km`).
- **QA/QC findings E-1 and E-2 are resolved in the catalog**, E-3 is deferred with a documented fallback. The `epsrmedium` row remains excluded from the target.

## 4. Phase 2 closure (closed 2026-11-21)

**Status:** closed. Owner approved the merge; the milestone commit carries the closure work.

| # | Action | Owner | Result |
|---|---|---|---|
| 4.1 | Owner reads the [QA/QC report](audits/line_linecode_phase2_qaqc.md) and [audit disposition](audits/line_linecode_schema_audit.md); decides merge readiness | Owner | Approved 2026-11-21 |
| 4.2 | Add `tools/requirements-validation.txt` and `tools/run_examples.py`; execute both workflow examples; record `Observed-working` plus the `environment` block in `examples.json` and update the workflow page | Coder | Done: both examples PASS (Windows 11 AMD64, Python 3.14.6, altdss 0.2.4, dss-python 0.15.7, backend 0.14.5) |
| 4.3 | Add `tools/validate_catalogs.py`; replace the manual `Test-Json` step in `skill.md` | Coder | Done: 9/9 schema pairs pass |
| 4.4 | Reconcile `manifest.json`: status, validation text, gaps, and next actions | Coder | Done: status `phase-2-complete`, schema-valid |
| 4.5 | Commit Phase 2 as one milestone commit on the Phase 2 branch (`wp/phase2`); owner merges to `main` | Coder / Owner | Done: milestone commit, fast-forward merge to `main` |
| 4.6 | Mark the Line/LineCode coder and QA/QC handoffs complete; retain them as the pattern reference | Coder | Done |

**Exit criteria — all met**

1. ✅ `tools/validate_catalogs.py` passes for the manifest and all catalogs in one command (9/9).
2. ✅ Both examples carry `Observed-working` with a recorded environment block.
3. ✅ Manifest status reflects closure; no catalog claims an unearned validation level.
4. ✅ Owner approved the merge; the audit trail names the reviewed commit.
5. ✅ No uncommitted Phase 2 work remains.

The Line/LineCode package is now the reference implementation of the element package template in Section 5.4.

## 5. Phase 3 — Scale-out extraction (planned)

### 5.1 Sequencing decisions

- **Infrastructure before breadth.** The empty `altdss_python_api` and `dss_capi` catalogs are the machine-readable ground truth every element package cites. Filling them once removes repeated per-element wrapper and engine research and reduces QA variance.
- **Dependencies before convenience.** `Line.wires` already showed cross-element coupling: conductor and geometry objects gate a documented Line path. Element packages land in dependency order.
- **One shared source index.** Phase 3A migrated the 15 Line/LineCode source records into `references/sources.json` with the same IDs and removed the superseded index and schema. Use source IDs for shared index references and keep claim-level citations where the record schema calls for them.
- **One general element schema.** Add `schemas/catalogs/element_properties.schema.json` (generalized `element_class`, property-level `source_refs` required) for new elements. The Line/LineCode schema stays as published; it is not retrofitted.
- **Scope cap.** Phase 3 covers the elements named in 5.3 only. Adding elements is an owner decision.

### 5.2 Workstream 3A — API and engine catalogs

| Catalog | Method | Acceptance |
|---|---|---|
| `altdss_python_api.json` | Extract from the pinned wrappers: classes and `module_path`, `new`/`batch_new` signatures, property names and type hints from the `TypedDicts` and property blocks, batch behavior, docstring-derived descriptions | Every record `Official-versioned` at 0.2.4; casing matches source exactly (`pctPerm` vs `PctPerm`, `rho`, `Conductors`); schema-valid |
| `dss_capi.json` | `records/api.schema.json` records for engine identity, property enums, specification sets, scaling functions, constructor defaults, and documented DBS/extension behaviors, each tied to 0.14.5 file and line range | Every record version-scoped; no mutable `master` citations; schema-valid |
| `references/sources.json` | Single index; migrate existing 15 records, add the Phase 3A source entries | Unique ids; every `version_or_ref` set for DSS-Extensions sources, `null` for undated EPRI pages with scope note |

**Status 2026-11-21:** Independent QA/QC passed with findings. It reproduced the generated catalog from the pinned wheel and checked the 26 curated engine records and shared source index. The coder corrected the citation ranges and documentation findings. [Review report](audits/phase3a_api_catalogs_qaqc.md) · [Finding disposition](audits/phase3a_api_catalogs_audit.md#independent-qaqc-disposition)

### 5.3 Workstream 3B — Element packages, in order

| Order | Element package | Why now |
|---|---|---|
| 1 | `LineGeometry`, `LineSpacing`, `WireData` (with `CNData`, `TSData` aliases) | Unblocks the Line geometry and `wires`/`Conductors` workflows already documented |
| 2 | `Circuit`, `Vsource` | Prerequisite for every executable example and fixture |
| 3 | `Transformer` | Largest and most-used power-delivery element; high modeling risk |
| 4 | `Load` | Load model and shape interaction |
| 5 | `Capacitor` | Shunt compensation and control coupling |
| 6 | `Generator` | Source element with control coupling |

Each package follows the template and definition of done in 5.4. Package 1 has its catalog, workflow, two executed examples, and five-class readback matrix. Independent QA/QC found no blocking issues and the architect/auditor review applied one optional citation correction. The owner accepted package 1 on 2026-11-21 and directed package 2, whose coder handoff is issued: [Circuit and Vsource coder handoff](handoffs/Phase_3B_Circuit_Vsource_Coder_handoff.md). [Coder handoff](handoffs/Phase_3B_LineGeometry_WireData_Coder_handoff.md) · [Build audit](audits/phase3b_line_geometry_wires_audit.md) · [QA/QC report](audits/phase3b_line_geometry_wires_qaqc.md) · [Architect/auditor review](audits/phase3b_line_geometry_wires_architect_audit.md)

Package 2 has its Circuit command and Vsource catalog, two executed examples, and a matrix of constructor readbacks and focused probes. Independent QA/QC found no blocking issues and the architect/auditor review required no corrections; two non-blocking observations are recorded. The owner accepted package 2 on 2026-11-21 and directed package 3, whose coder handoff is issued: [Transformer and XfmrCode coder handoff](handoffs/Phase_3B_Transformer_Coder_handoff.md). [Build audit](audits/phase3b_circuit_vsource_audit.md) · [QA/QC report](audits/phase3b_circuit_vsource_qaqc.md) · [Architect/auditor review](audits/phase3b_circuit_vsource_architect_audit.md)

Package 3 adds Transformer and XfmrCode for two- and three-winding models, two executed examples, and a runtime matrix. Independent QA/QC and the architect review passed; the review found and corrected one citation that ran past the end of `PDClass.pas` (E-1) and recorded one harness attribution issue (E-2). The owner accepted package 3 on 2026-11-21 and directed package 4, whose coder handoff is issued: [Load coder handoff](handoffs/Phase_3B_Load_Coder_handoff.md). Package 4 covers the `Load` element with the five engine load-specification families as its centerpiece; the `LoadShape` and `GrowthShape` property catalogs are recorded as deferred class catalogs. [Build audit](audits/phase3b_transformer_audit.md) · [QA/QC report](audits/phase3b_transformer_qaqc.md) · [Architect/auditor review](audits/phase3b_transformer_architect_audit.md)

Package 4 adds the 43-row Load catalog, Python and DSS examples, and a readback matrix covering all five load-specification families and assignment effects. Independent QA/QC and the architect review both passed with no required corrections to the package; the review re-derived the coverage, citations, defaults, and traps, corrected one architect-owned handoff statement (A-1, the edit-context dependency of attribute writes), and recorded two schema and labelling observations (O-1, O-3). The owner accepted package 4 on 2026-11-21 and released package 5. [Build audit](audits/phase3b_load_audit.md) · [QA/QC report](audits/phase3b_load_qaqc.md) · [Architect/auditor review](audits/phase3b_load_architect_audit.md)

Package 5 adds the 22-row Capacitor catalog, Python and DSS examples, and a readback matrix for three capacitance families, step arrays, topology, and solved switching. CapControl remains a deferred controller catalog. Independent QA/QC reproduced the whole matrix and reported PASS with no required corrections. The architect review also passed: it re-derived the 21 wrapper keywords and 13 engine members, checked all 114 property-level citations (tag-pinned, in bounds), reproduced the 135%/180% rating arithmetic and every stated trap, and recorded two minor non-blocking findings — E-1, the `states` row describes Python edit writes as "edit writes" where the DSS `Edit` command actually works; E-2, the `kvar` and `emergamps` rows do not disclose EPRI's divergent 600 kvar default and 135%-of-`NormAmps` statement — plus two corrections to architect-owned handoff traps (A-1, `Like` is also a callable Python method; A-2, `State` is accepted as a text abbreviation rather than being a removed v6 property) and one carried-forward schema observation (O-1, eight unvalidated row fields). At owner direction both findings were applied before acceptance: the `states` row now names the Python write paths, and the `kvar` and `emergamps` rows disclose the EPRI divergences. [Coder handoff](handoffs/Phase_3B_Capacitor_Coder_handoff.md) · [Build audit](audits/phase3b_capacitor_audit.md) · [QA/QC report](audits/phase3b_capacitor_qaqc.md) · [Architect/auditor review](audits/phase3b_capacitor_architect_audit.md)

Package 6 adds the 49-row Generator catalog, two executed examples, and a readback matrix that distinguishes machine ratings, scheduled power, and solved injection. It covers Model 3 voltage targets and reactive limits. The separate GenDispatcher catalog is deferred. This delivers the final element package in the sequence. Independent QA/QC reproduced the whole matrix and reported PASS with no required corrections. The architect review also passed: it re-derived the 47 wrapper keywords and 44 engine members, checked all 252 citations (tag-pinned, in bounds, none reversed), reproduced the constructor defaults from `generator.pas`, and independently re-ran the guards, the `MVA` alias, the `Like` copy, the `Refuel` paths and the committed DSS example. It recorded two minor non-blocking findings — E-1, numeric enum text writes are silently discarded for `DispMode` and `Status` while the package documents only the Python half; E-2, the `vminpu`/`vmaxpu`/`xdp` rows do not disclose EPRI's 0.95/1.05/0.27 — five corrections to architect-owned handoff traps (A-1 `DispMode` read-versus-write, A-2 `Like` method, A-3 `Maxkvar` sign, A-4 implied PF 0.9982, A-5 `#567` versus `#570`), and narrowed the schema observation O-1 to Capacitor only. [Build audit](audits/phase3b_generator_audit.md) · [QA/QC report](audits/phase3b_generator_qaqc.md) · [Architect/auditor review](audits/phase3b_generator_architect_audit.md)

### 5.4 Element package template (definition of done)

1. **Catalog** — `references/<area>/<element>_properties.json` validated against `element_properties.schema.json`; engine specification sets distinguished from minimum constructor inputs; unsupported target properties marked `supported_in_target: false` and excluded from generation; per-row `source_refs`.
2. **Source index** — `references/sources.json` entries for each cited page, tag, and file range.
3. **Workflow** — `docs/workflows/<element>.md` with creation order, side effects, unit rules, and expected readback.
4. **Examples** — runnable file under `opendss_altdss_library/examples/<area>/` and an `examples.json` record with expected result, source ids, and evidence label.
5. **Audit** — `docs/audits/<element>_schema_audit.md` with findings and disposition.
6. **Validation record** — property-readback matrix executed on the pinned stack (defaults and side effects), recorded with environment; examples `Observed-working` when run.
7. **Independent QA/QC** — separate reviewer, same checklist shape as the Line/LineCode handoff; owner dispositions findings before merge.

### 5.5 Workstream 3C — Roll-up and comparison

- `opendss_objects.json` becomes the element index that links each element class to its package, EPRI page, and catalog.
- `python_interface_comparison.json` records `altdss` / `dss` / `opendssdirect` equivalents per task, comparison-only, never as the primary target.
- `troubleshooting.json` is seeded from Phase 3 QA findings and populated mainly in Phase 4.

**Phase 3 exit criteria:** the two API catalogs and the single source index are complete and schema-valid; the six element packages pass independent QA/QC; every published record is version-scoped with a resolvable source; the catalog set validates in one command.

## 6. Phase 4 — Validation with golden fixtures (planned)

**Objective:** move from property-level evidence to solved-model evidence and satisfy the charter stop gate.

**Owner decision (2026-11-21):** the Phase 4 stop gate requires recorded golden fixture results. Cross-interface consistency alone is not sufficient.

### 6.1 Fixture set

| Fixture | Source | Notes |
|---|---|---|
| IEEE 13-node | DSS-Extensions test repository at a pinned commit, or the EPRI OpenDSS installation test cases | Distribution feeder with regulator, transformer, and capacitor models; single source of record |
| IEEE 34-node | Same source family as IEEE 13 | Longer feeder with laterals; exercises more element classes |

- Copy fixture files unmodified into `opendss_altdss_library/examples/fixtures/ieee13/` and `.../ieee34/`; do not hand-edit circuits. Any required edit is an overlay file plus a rationale.
- Each fixture directory carries `PROVENANCE.md`: upstream repository and commit or installer version, file list, license/attribution, retrieval date, and SHA-256 checksums of the circuit files.
- Add `references/fixtures.json` plus `schemas/catalogs/fixtures.schema.json` with fixture id, file list and checksums, `source_ids`, golden file path, tolerances, engine versions, and `golden_revision`.

### 6.2 Golden result format

`examples/fixtures/<name>/golden.json`, generated by the harness — never hand-typed:

```json
{
  "fixture": "ieee13",
  "golden_revision": 1,
  "generated": "2026-11-21",
  "engine": {"altdss": "0.2.4", "dss_python": "0.15.7", "backend": "0.14.5", "python": "3.14.6"},
  "solve": {"mode": "snapshot", "basefreq": 60.0, "converged": true, "iterations": 3},
  "buses": [{"name": "650", "vmag_pu": 1.0, "vang_deg": 0.0}],
  "elements": [{"class": "Line", "name": "650632", "p_kw": 0.0, "q_kvar": 0.0, "losses_kw": 0.0}],
  "summary": {"total_losses_kw": 0.0, "total_load_kw": 0.0},
  "tolerances": {"vmag_pu_abs": 1e-6, "vang_deg_abs": 1e-6, "power_kw_rel": 1e-6}
}
```

- **Tolerances:** same engine on the same platform should reproduce to 1e-9; compare with 1e-6 (absolute for per-unit voltage and degrees, relative for power). Any wider tolerance requires a documented reason in the fixture record.
- **Scope:** snapshot solve for both fixtures; add a daily or QSTS run for one fixture once snapshot is stable. Regulator, capacitor, and transformer controls must be exercised, not bypassed.
- **Stability:** record solver options (mode, tolerance, max iterations) and `basefreq` in the golden file; a change to any of them is a new `golden_revision`.

### 6.3 Harness and comparison tooling

| Tool | Purpose | Contract |
|---|---|---|
| `tools/run_fixtures.py` | Compile, solve, export results in the golden format, and diff against `golden.json` | Exit 0 when every fixture matches within tolerance; `--update-golden` writes a new revision and requires owner approval recorded in `references/fixtures.json` |
| `tools/compare_interfaces.py` | Run the same fixture through `altdss`, `dss`, and `opendssdirect` on the pinned versions | Report per-quantity deltas; exit 0 when deltas are within tolerance or explicitly dispositioned |
| `tools/validate_catalogs.py` | Existing schema validation, extended to `fixtures.json` | Unchanged contract |

Both new tools read the pinned environment and refuse to run when installed versions differ from the manifest targets unless `--allow-version-drift` is passed, and they record the environment with every result.

### 6.4 Coverage matrix

| Dimension | Phase 4 coverage |
|---|---|
| Element classes | Those delivered in Phase 3 plus regulator, transformer, capacitor, and load controls exercised by the fixtures |
| Operation modes | Snapshot (both fixtures); daily or QSTS (one fixture) |
| Behavior | Batch creation, edit contexts, property side effects (for example `Switch`), unit conversions, error paths |
| Interfaces | `altdss` primary; `dss` and `opendssdirect` comparison only |
| Evidence | Every example `Observed-working` with environment; `troubleshooting.json` populated from observed failures |

### 6.5 Acceptance (stop gate)

1. Both fixtures compile, converge, and match `golden.json` within tolerance from a clean environment built from `tools/requirements-validation.txt`.
2. Cross-interface deltas are within tolerance or individually dispositioned with a recorded explanation.
3. Golden metadata records upstream source, checksums, license, engine versions, solver options, date, and `golden_revision`.
4. `troubleshooting.json` holds the observed failure modes with resolutions.
5. Independent QA/QC signs off; the manifest's `validation.runtime` states scope, environment, and residual gaps.
6. Golden regeneration happens only through `--update-golden` with an owner-approved reason and a new revision number.

### 6.6 Risks specific to golden fixtures

| Risk | Mitigation |
|---|---|
| Fixture licensing or attribution unclear | Record source, license, and checksums per fixture; prefer the DSS-Extensions test repository with its stated terms |
| Floating-point or platform drift | Tolerance policy in 6.2; record platform in the golden metadata; CI-style rerun on a clean environment |
| Golden rot after upstream changes | Fixtures are copied and checksummed; upstream changes do not silently propagate |
| Solver-option drift | Options are part of the golden metadata and a change is a new revision |
| Fixtures bypass controls | Coverage matrix requires control elements to operate; compare against documented feeder behavior |

## 7. Phase 5 — Retrieval and release (planned)

- **Retrieve:** a search index over catalogs supporting exact-symbol and concept queries with filters for version and evidence label, returning the source URL, tag, and access date.
- **Release:** package the skill with the manifest, validation levels, known gaps, and supported tasks per the charter's release step; publish a changelog and a version tag decision.

## 8. Governance

- **Roles.** Architect and auditor: DeepSeek. Coder: GPT-6.2 Sol. Independent QA/QC: Mistral 4. The project owner decides which findings block merge and approves scope changes. The assignment is recorded in Section 11.
- **Branches:** phase branches (`wp/phaseN`) created from `main`, with one milestone commit per phase; QA reports name the reviewed branch and commit or working-tree state.
- **Evidence policy:**
  - `Observed-working` requires a committed example file, a harness run, an environment block, and a date.
  - `Example-only` means inspected but not executed by the project harness.
  - `Official-versioned` requires a tag or page plus access date; undated EPRI pages are cited for what they state, with pinned sources for version-sensitive behavior.
  - Unresolved items stay `Unverified` or open questions; no inferred defaults, names, or equivalence.
- **Change control:** plan changes are recorded in Section 10 and mirrored in the manifest.

## 9. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Phase 2 work stays uncommitted | Loss, review ambiguity | Close 4.1–4.5 promptly; one milestone commit |
| Manual validation drifts | Unreproducible evidence | Committed harness (4.2, 4.3); validation required before merge |
| EPRI pages undated and mixed-version | Over-claimed behavior | Pin engine claims to 0.14.5; page-qualified EPRI claims; source index scope notes |
| Wrapper keyword casing differences (`pctPerm` / `PctPerm`, `rho`) | Generated code fails | Generate from pinned `TypedDicts`; test every keyword in the readback matrix |
| Namespace conflation (`altdss` / `dss` / `opendssdirect`) | Wrong API guidance | Separate catalogs; comparison catalog only; skill instructions |
| Element scope creep | Quality dilution | Phase 3 cap in 5.3; owner approves additions |
| QA capacity becomes the bottleneck | Schedule slip | Template plus generated API catalogs reduce per-element review surface |
| Schema/catalog drift | Invalid records | Single validation command; schema changes reviewed with the catalog |

## 10. Plan change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11 (implicit) | Phase 1 plan lived in the charter and Phase 1 README; Phase 2 described as catalog remediation plus example indexing |
| 0.2 | 2026-11-21 | Architect review. Added Phase 2 closure checklist and exit criteria; adopted the six-artifact element package template; reprioritized Phase 3 to API/engine catalogs first, then dependency-ordered element packages with a scope cap; consolidated the source index and generalized the element schema; added committed validation tooling and the `Observed-working` evidence rule; defined Phase 4 fixtures and Phase 5 retrieval and release; recorded the owner decisions below |
| 0.3 | 2026-11-21 | Phase 2 closed: validation harness committed, both examples recorded `Observed-working`, manifest reconciled, milestone merged. Owner decided the Phase 4 stop gate requires golden fixture results; added the golden fixture design (6.1–6.6) with source/provenance rules, golden format, tolerances, harness contracts, coverage matrix, acceptance, and risks |
| 0.4 | 2026-11-21 | Phase 3A delivered: generated the AltDSS-Python API catalog from the pinned wheel, added 26 DSS C-API engine records, consolidated the source index into `references/sources.json` (18 records), and extended the validation harness for the record schemas. Owner confirmed the Phase 3 element scope and order |
| 0.5 | 2026-11-21 | Recorded the Phase 3A QA/QC disposition, clarified the source-index migration, and corrected the Line/LineCode citation spans after the follow-up review. |
| 0.6 | 2026-11-21 | Recorded the owner role assignment (DeepSeek architect/auditor, GPT-6.2 Sol coder, Mistral 4 QA/QC) as a Section 11 decision, and prepared the Phase 3B package-1 coder handoff |
| 0.7 | 2026-11-21 | Added the generalized element schema and the first Phase 3B element package. Recorded schema and runtime results and prepared independent QA/QC. |
| 0.8 | 2026-11-21 | Recorded the Phase 3B package-1 dispositions: independent QA/QC passed with no blocking findings, the architect/auditor review re-verified coverage, citations, and runtime on a clean environment, and optional correction A-1 was applied to two enum citation spans. |
| 0.9 | 2026-11-21 | Recorded the owner's acceptance of Phase 3B package 1 and issued the package-2 (Circuit and Vsource) coder handoff with the verified scope decision, evidence pins, and behavior traps. |
| 0.10 | 2026-11-21 | Added the Circuit and Vsource package, recorded coder validation, and prepared independent QA/QC. |
| 0.11 | 2026-11-21 | Recorded the Phase 3B package-2 dispositions: independent QA/QC passed with no blocking findings, and the architect/auditor review re-derived coverage, defaults, family precedence, and runtime on a clean environment with no required corrections. |
| 0.12 | 2026-11-21 | Recorded the owner's acceptance of Phase 3B package 2 and issued the package-3 (Transformer and XfmrCode) coder handoff with the winding-model scope, pinned evidence, and the engine hazards found while preparing it. |
| 0.13 | 2026-11-21 | Added Transformer and XfmrCode for two- and three-winding models, recorded pinned runtime validation, and prepared independent QA/QC. |
| 0.14 | 2026-11-21 | Recorded the Phase 3B package-3 dispositions: independent QA/QC passed with no blocking findings, and the architect/auditor review re-derived the winding model, defaults, and runtime on a clean environment, found and corrected one out-of-range citation (E-1), and recorded one non-blocking harness observation (E-2). |
| 0.15 | 2026-11-21 | Recorded the owner's acceptance of Phase 3B package 3 and issued the package-4 (Load) coder handoff with the five load-specification families as the centerpiece, the pinned default and precedence facts, and the deferral of the LoadShape and GrowthShape class catalogs. |
| 0.16 | 2026-11-21 | Re-verified the issued package-4 handoff against the pinned sources before coding started and corrected three statements: the enum readback types (`Model`, `Conn`, and `Status` all return altdss enum members, not integers), the `SpecSetNames` display order versus the `TSpecSets` member order for the kWh family, and the trap-2 provenance. Added trap 15, which records that successive attribute writes leave the derived `kvar` and `kVA` stale where a single `new(...)` call or text command recomputes them. |
| 0.17 | 2026-11-21 | Added the Load catalog, workflow, examples, and pinned readback matrix. Recorded coder validation and prepared independent QA/QC. |
| 0.18 | 2026-11-21 | Prepared the package-5 (Capacitor) coder handoff at owner direction, ahead of package 4 acceptance, from an independent read of `src/PDElements/Capacitor.pas` and `altdss/Capacitor.py`. Records the 21-key wrapper surface against the 13-member engine enum, the three capacitance families, the array-over-`NumSteps` properties, and the verified traps (deleted v6 property set, `Cuf`-family rating anomaly, `States` write path, `Like` read-only, `NormAmps` stickiness). |
| 0.19 | 2026-11-21 | Corrected the Load handoff's property-vocabulary citation: `Properties17.html` is the Fault page, and the Load vocabulary page is `Properties7.html` (`ZIPV`, `kWhDays`, 13 `Load` mentions in the raw HTML), as the package-4 reviewer flagged. Identified `Properties12.html` as the Capacitor vocabulary page by a token scan of `Properties1..40.html` and added it to the Capacitor handoff. |
| 0.20 | 2026-11-21 | Recorded the Phase 3B package-4 dispositions: independent QA/QC passed with no blocking findings and no required corrections, and the architect review re-derived the wrapper and engine coverage, all 209 citations, the defaults, and the trap set on a clean environment, then corrected one architect-owned handoff statement about the attribute-write behaviour (A-1) and recorded two observations (O-1 unvalidated row fields, O-3 correct use of not-run). |
| 0.21 | 2026-11-21 | Recorded the owner's acceptance of Phase 3B package 4 (Load) after coder validation, independent QA/QC (PASS, no blocking findings), and the architect review (PASS, A-1 applied, O-1/O-2/O-3 recorded), and released package 5 (Capacitor) to the coder per the issued handoff. |
| 0.22 | 2026-11-21 | Added the Capacitor catalog, workflow, examples, and solved readbacks. Recorded coder validation and prepared independent QA/QC. |
| 0.23 | 2026-11-21 | Prepared the package-6 (Generator) coder handoff at owner direction, ahead of package 5 review, from an independent read of `src/PCElements/generator.pas` and `altdss/Generator.py`. Records the 47-key wrapper surface against the 44-member engine enum (the wrapper omits the text-only `MVA`), the rating-versus-specification distinction, the scheduled-versus-solved reactive behavior, and 21 verified traps, including the inverted EPRI page naming and the `Model` 6 DLL requirement. |
| 0.24 | 2026-11-22 | Recorded the Phase 3B package-5 (Capacitor) review outcomes: independent QA/QC reproduced the matrix and reported PASS with no required corrections, and the architect review reported PASS WITH FINDINGS after re-deriving the wrapper and engine surfaces, all 114 property-level citations against real file lengths, the default readbacks, the 135%/180% rating arithmetic, and an 8-path `States` write probe. Findings: E-1 (`states` row wording, "edit writes" is ambiguous because the DSS `Edit` command works), E-2 (the catalog does not disclose EPRI's 600 kvar default or its 135%-of-`NormAmps` statement), A-1 and A-2 (two architect-owned handoff traps corrected: `Like` is also a Python method; `State` is an accepted text abbreviation), and O-1 (eight undeclared row fields, 27 uses, carried forward from package 4). |
| 0.25 | 2026-11-22 | Recorded the owner's acceptance of Phase 3B package 5 (Capacitor) and applied its two non-blocking findings: E-1 reworded the `states` description so it names the Python creation keyword, attribute assignment, and `bank.edit(States=...)` call instead of the ambiguous "edit writes" (the DSS `Edit` command does work), and E-2 appended the EPRI divergence to `kvar` (600 kvar default stated by EPRI against the pinned 1200) and `emergamps` (135% of Normamps stated by EPRI against the pinned 180% of rated current). No value, type, default, or citation changed; schema validation re-passed 14/14. Released package 6 (Generator) to the coder. |
| 0.26 | 2026-11-21 (local runtime date) | Added the Generator package and completed the six-package implementation sequence. Recorded coder validation, declared the Generator metadata fields in the shared row schema, and prepared independent QA/QC. |
| 0.27 | 2026-11-21 (local) | Recorded the Phase 3B package-6 (Generator) review outcomes: independent QA/QC reproduced the matrix and reported PASS with no required corrections, and the architect review reported PASS WITH FINDINGS after re-deriving the wrapper and engine surfaces, all 252 citations against real file lengths, the constructor defaults, and independent probes of the guards, the `MVA` alias, the `Like` copy, `Refuel`, and an eight-cell `DispMode`/`Status` path matrix. Findings: E-1 (numeric enum text writes silently discarded for `DispMode` and `Status`, documented nowhere), E-2 (EPRI's 0.95/1.05/0.27 not disclosed in the rows), A-1 to A-5 (architect handoff traps corrected, including the same `Like` error previously corrected for Capacitor), and O-1 narrowed to Capacitor (Load and Generator now fully declared). |

## 11. Owner decisions

1. **Merge approval — resolved 2026-11-21.** Owner approved; Phase 2 milestone committed and merged to `main`.
2. **Phase 3 scope confirmation — resolved 2026-11-21.** Owner confirmed the six element packages in 5.3 and their order; additional elements are a new owner decision.
3. **Phase 4 stop gate — resolved 2026-11-21.** Recorded golden fixture results are required; cross-interface consistency alone is not sufficient. Design in Section 6.
4. **Role assignment — resolved 2026-11-21.** Architect/auditor: DeepSeek. Coder: GPT-6.2 Sol. Independent QA/QC: Mistral 4. The owner decides merge and scope. This supersedes the coder name used in earlier phase documents; Phase 1 records DeepSeek only as the owner-selected external auditor, so this decision is the record of the later architect/auditor role.
5. **Phase 3B package 1 acceptance — resolved 2026-11-21.** Owner accepted package 1 after independent QA/QC (PASS, no blocking findings) and the architect/auditor review (PASS, optional correction A-1 applied), and directed package 2 (Circuit and Vsource).
6. **Phase 3B package 2 acceptance — resolved 2026-11-21.** Owner accepted package 2 after independent QA/QC (PASS, no blocking findings) and the architect/auditor review (PASS, no required corrections), and directed package 3 (Transformer and XfmrCode, including the shared XfmrCode object; `AutoTrans` remains deferred to a later owner decision).
7. **Phase 3B package 3 acceptance — resolved 2026-11-21.** Owner accepted package 3 after independent QA/QC (PASS, no blocking findings) and the architect/auditor review (PASS, correction E-1 applied, observation E-2 recorded), and directed package 4 (Load). `LoadShape` and `GrowthShape` property catalogs are deferred; the package-4 catalog covers the `Load` element and its shape-assignment behavior only.
8. **Phase 3B package 5 preparation — resolved 2026-11-21.** Owner directed the Capacitor package to be prepared while package 4 awaited review. The coder handoff is issued, but coding remains gated on the owner's disposition of package 4; `CapControl` remains a deferred controller catalog.
9. **Phase 3B package 4 acceptance — resolved 2026-11-21.** Owner accepted package 4 after coder validation, independent QA/QC (PASS, no blocking findings, no required corrections), and the architect review (PASS, correction A-1 applied to the architect-owned handoff, observations O-1 to O-3 recorded), and released package 5 (Capacitor). The schema declaration of `enum_type` and `reference_class` (O-1) remains an open follow-up.
10. **Phase 3B package 6 preparation — resolved 2026-11-21.** Owner directed the Generator package to be prepared while package 5 was in progress. The coder handoff is issued, but coding remains gated on the owner's disposition of package 5. `GenDispatcher` and the other controller catalogs, `PVSystem`, and `Storage` remain deferred.

11. **Phase 3B package 5 acceptance — resolved 2026-11-22.** Owner accepted package 5 after coder validation, independent QA/QC (PASS, no required corrections), and the architect review (PASS WITH FINDINGS), and directed findings E-1 and E-2 to be applied before acceptance; both are applied in the catalog with no value or citation change. The architect-owned handoff traps A-1 (`Like` is also a callable Python method) and A-2 (`State` is an accepted DSS text abbreviation) were corrected during the review. O-1, the undeclared element row fields, remains an open schema follow-up. Package 6 (Generator) is released to the coder.
