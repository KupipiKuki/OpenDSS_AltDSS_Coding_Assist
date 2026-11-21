# Phase 3A API and Engine Catalogs — Independent QA/QC Report

**Reviewed branch:** `wp/phase3` — tip `35942f9` (docs-only: pins the handoff and touches the audit header); catalog commit under review `45a004d`, per the [QA/QC handoff](../handoffs/Phase_3A_API_Catalogs_QAQC_handoff.md). Baseline for the diff: `8053b67` on `main`.
**Reviewed state:** `git status --porcelain` clean at review start.
**Review date:** 2026-11-21. **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, fresh venv with `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (per `tools/requirements-validation.txt`); `altdss-0.2.4-py3-none-any.whl` from PyPI (SHA-256 `91d876f4…f0f`); DSS C-API sources fetched at tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d` and AltDSS-Python tag `0.2.4` = commit `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee` (both confirmed via the GitHub API — the pinned tags in the audit are correct).

**STATUS:** PASS WITH FINDINGS

## What was checked

- Re-ran `tools/validate_catalogs.py` (twice: system Python and the fresh venv).
- Re-ran `tools/build_altdss_api_catalog.py` against the extracted `altdss==0.2.4` wheel and compared byte-for-byte with the committed `references/altdss_python_api.json`.
- Independently re-parsed the wheel with `ast` (separate code from the generator) and compared every one of the 99 records: class set, property names and order, type hints (`# type:` comments / `*Properties` TypedDicts), method names and full signatures, plus casing spot checks. Result: 99/99 records match exactly, 0 discrepancies; casing `pctPerm` (Line) vs `PctPerm` (LineCode), `rho`, `Conductors` all match the source.
- Generator determinism: regenerated catalog is **byte-identical** to the committed file (SHA-256 `c5774e4347b79ab2afb1190a0c4d35136657a532d6e7d169964228acf544e027` for both). 99 classes / 1,094 properties / 180 methods confirmed.
- Downloaded `src/PDElements/Line.pas` (2,178 lines) and `src/General/LineCode.pas` (699 lines) at tag `0.14.5` and checked every file/line citation in all 26 `dss_capi.json` records against the cited content.
- Checked `sources.json` migration against the pre-3A `line_linecode_sources.json` at `8053b67`, and resolved every `source_ids` used anywhere under `references/`.
- Re-ran `tools/run_examples.py` in the fresh venv (runtime evidence) and additionally spot-checked `tested: pass` engine behaviors through the pinned stack.
- Reviewed the `45a004d` doc diffs (README, library README, `skill.md`, workflow, plan, manifest) for stale references.

## COVERAGE FINDINGS

- No missing or spurious records within the declared scope. The wheel at 0.2.4 contains exactly 49 `DSSObj` subclasses, 49 `I<Element>` collection interfaces (`IDSSObj`-based, `I`-prefixed), and the `AltDSS` context class; the catalog holds exactly those 99 records, no duplicates. Each collection record carries `new`/`batch_new` (verified against source); each object record carries `edit` plus its properties; the context record carries 6 properties + 33 public methods, matching the source.
- Declared scope boundaries verified accurate: batch classes (`LineBatch`, …) exist in the source and are correctly not separate records; `_str` proxies excluded (Line: 42 raw `property()` assignments → 35 cataloged); setter-only pseudo-properties not itemized (runtime-confirmed: `Kron=True` is a read-only action on the wrapper, not a settable property).
- **Documentation miscount (finding C-1):** `docs/audits/phase3a_api_catalogs_audit.md` states "46 object classes, 52 collection interfaces, 1 context class". The verified split is **49 / 49 / 1** (totals 99 / 1,094 / 180 are correct). The commit message, plan, READMEs, and manifest state only the correct totals.
- **Scope note (finding C-2, minor):** the non-element context-member interfaces (`IBuses`, `IControlQueue`, `IError`, `IObj`, `IReduceCkt`, `ISettings`, `ISolution`, `ITopology`, `IYMatrix`, `IZIP`) and the `Element`/`PCElement`/`PDElement` batch proxies exposed on the `AltDSS` instance have no records. This is consistent with the audit's stated scope (object classes, `I<Element>` collections, context class) but is not listed in the audit's "Known limitations" — worth one sentence there.

## SOURCE FINDINGS

- API catalog: all 99 records match the pinned 0.2.4 source exactly (independent AST re-parse, not the generator): names, order, signatures, type hints; descriptions are docstring-derived with the `DSS property name:` trailer removed (spot-checked, e.g. `Line.pctPerm` → "Percent of failures that become permanent. Default is 20."). No spurious or behavior-asserting descriptions found in the sample.
- Engine catalog: 23 of 26 records cite file/line ranges that land exactly on the claimed source content at tag `0.14.5` (spec sets, `GetZSeqScale`/`GetCSeqScale`/`GetC1C0Scale` and their wiring, Wires row + `PropertyNameJSON 'Conductors'`, `SetWires`, Switch flag + setter side effects, bus Required flags, phases setter, sequence/matrix branches, both constructors, ratings init, BaseFreq comment + `FetchLineCode`, `RequiresCircuit`, DynamicDefault flag, Neutral init, Kron reduction, Units none, repair row). All URLs are `blob/0.14.5/…` — no mutable `master` citations.
- **Citation errors (findings S-1…S-4, required corrections below):** the two `TLineProp` enum citations and the one `TLineCodeProp` enum citation are off; one B1/B0 range is off by one line at the start.
- **Minor wording (finding S-5):** `capi-line-prop-enum` note says the wrapper "exposes 35 of these rows as keywords"; precisely, the Line wrapper has 35 properties of which 28 map to enum rows (`Wires`→`Conductors`; `CNCables`/`TSCables` not exposed; the other 7 are inherited PDElement/CircuitElement rows: `NormAmps`, `EmergAmps`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, `Enabled`). Runtime-confirmed (`CNCables`/`TSCables`/`Wires`/`epsrmedium` absent from the wrapper; `Conductors` present).
- Source index: 15 pre-3A records migrated **unchanged** (byte-identical fields), 3 added (`altdss-python-024-tree`, `altdss-python-024-wheel`, `dss-capi-0145-tree`), none removed; 18 unique ids; every `source_ids` reference in `references/*.json` (examples.json et al.) resolves; no dangling references to the removed `line_linecode_sources.json` anywhere in code, schemas, or docs (only the audit's prose mentions the removal).
- **Minor doc inconsistency (finding S-6):** `docs/implementation_plan.md` §5.1 still says "keep the old file as a pointer stub", while the delivered state (and the §5.2 status note, commit message, and audit) removed the old index pair outright. The audit documents the deviation ("removed rather than stubbed"); the §5.1 design bullet was not updated.

## EVIDENCE FINDINGS

- `dss_capi.json`: 17 `pass` / 9 `not-run`, matching the audit. Every `pass` record carries an environment string; every `not-run` record has `environment: null` and is a static source fact — no `not-run` record is presented as verified. The `capi-engine-0145` note honestly records that the engine version string was not queried separately from package metadata.
- Runtime corroboration of the `pass` claims on the pinned stack (Windows 11 AMD64, Python 3.14.6, altdss 0.2.4, backend 0.14.5): new `Line` defaults R1=0.058, X1=0.1206, R0=0.1784, X0=0.4047, Length=1.0, NormAmps=400, EmergAmps=600, pctPerm=20, FaultRate=0.1, Repair=3.0, rho=100, Rg=0.01805, Xg=0.155081, Ratings=[400] — matches `capi-line-defaults`/`capi-line-initial-ratings`/`capi-line-length-units`; `Switch=True` yields R1=X1=R0=X0=1.0, C1=1.1, C0=1.0, Length=0.001 — matches `capi-line-switch-side-effects`; LineCode C1/C0 read back 3.4/1.6 nF/km — matches the C1/C0 scaling records; LineCode `BaseFreq` = 60.0 from the circuit fundamental (DynamicDefault), `Neutral`=3, `Repair`=0.0 (uninitialized) — matches `capi-linecode-basefreq-dynamic`/`capi-linecode-neutral-kron`/`capi-linecode-repair-uninitialized`; no `epsrmedium` attribute — matches `capi-line-no-epsrmedium`.
- `examples.json`: both records `Observed-working` with a recorded environment; re-execution reproduced PASS with the identical environment (see RUNTIME RESULT).
- Docs describe the catalogs at their real validation level: manifest `validation.source_review` says Phase 3A "await[s] independent QA/QC"; READMEs/skill say "pending independent QA/QC"; nothing claims runtime validation beyond the recorded `tested` entries.

## SCHEMA RESULT

**PASS** — `python opendss_altdss_library/tools/validate_catalogs.py` exits 0: 9/9 manifest-and-catalog schema pairs pass (Draft 2020-12 with format checking, `jsonschema` 4.26.0), including the new base-URI `$ref` resolution for `dss_capi.schema.json → ../records/api.schema.json`; all manifest-declared catalogs are schema-paired and present. Run twice (system Python 3.14.6 and the fresh venv), identical result. Per the handoff, this schema pass is **not** treated as runtime validation.

## RUNTIME RESULT

**PASS** — fresh venv, Windows 11 AMD64, Python 3.14.6, altdss 0.2.4, dss-python 0.15.7, dss-python-backend 0.14.5 (no version drift against `manifest.json` `support_targets`): `python opendss_altdss_library/tools/run_examples.py` exits 0; both `line-linecode-altdss` and `line-linecode-dss-text` PASS with readbacks matching their `expected_result` (C1/C0 = 3.4/1.6 nF/km; lengths 1.0/0.25/0.40 km in batch order), consistent with the recorded `Observed-working` status. Additional engine spot checks above also passed.

## REQUIRED CORRECTIONS

1. `references/dss_capi.json`, record `capi-line-prop-enum` — `source.section_or_record` "TLineProp enum, L55-L86" → **"TLineProp enum, L60-L91"**. Source: <https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas> (tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`): the enum is declared at L60 and closes at L91; L55-L59 are the tail of the preceding legacy enum and L87-L91 (B1…LineType) were outside the cited range.
2. `references/dss_capi.json`, record `capi-line-no-epsrmedium` — same citation "TLineProp enum, L55-L86" → **"TLineProp enum, L60-L91"** (same source file/tag).
3. `references/dss_capi.json`, record `capi-linecode-prop-enum` — `source.section_or_record` "TLineCodeProp enum, L98-L131" → **"TLineCodeProp enum, L60-L89"**. Source: <https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas> — the enum is L60-L89; L98-L131 is the `TLineCodeObj` class declaration.
4. `references/dss_capi.json`, record `capi-linecode-b1-b0` (minor) — "B1/B0 rows, L309-L315" → **"L308-L315"** (the B1 row starts at L308, `PropertyOffset[ord(TProp.B1)]`).
5. `docs/audits/phase3a_api_catalogs_audit.md`, Coverage table (finding C-1) — "46 object classes, 52 collection interfaces, 1 context class" → **"49 object classes, 49 collection interfaces, 1 context class"** (verified against the 0.2.4 wheel; totals 99 / 1,094 / 180 unchanged).
6. Optional wording/doc fixes: `capi-line-prop-enum` note "exposes 35 of these rows" → "exposes 35 properties, 28 of which map to enum rows" (finding S-5); add the non-element context interfaces to the audit's Known limitations (finding C-2); align `docs/implementation_plan.md` §5.1 "pointer stub" wording with the actual removal (finding S-6).

No changes were made to the catalogs under review; this report is the only file added, per the handoff.
