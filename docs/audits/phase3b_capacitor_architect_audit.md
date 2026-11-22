# Phase 3B Package 5 (Capacitor) — Architect/Auditor Review

**STATUS: PASS WITH FINDINGS** — no required correction to the package blocked the owner's disposition, and the owner accepted package 5 on 2026-11-22 directing E-1 and E-2 to be applied first. **Both findings are applied** (resolution recorded below and in plan v0.25); A-1 and A-2 are applied to the handoff; O-1 stays open as a schema follow-up. Two evidence/precision findings are recorded (E-1, E-2, both minor and non-blocking), two architect-owned handoff statements are corrected (A-1 `Like`, A-2 `State`), and one schema follow-up is carried forward (O-1).

- **Reviewed revision:** `d7fc55c5de6ae6533af69aa17ce16bdf22e90026` (Phase 3B: Capacitor package), plus `3558fbf` (re-pins the QA handoff) and `38d16e6` (the independent QA/QC report). **Baseline:** `6663beaa2578748bd39749f42905341733bdfe5c` (package-4 acceptance). **Audit performed at:** `38d16e6` on `wp/phase3`, working tree clean apart from an untracked `tools/__pycache__/` directory created by the harness run.
- **Scope boundary:** `git diff --stat d7fc55c..HEAD -- opendss_altdss_library/` returns only `README.md` and `manifest.json`, so every catalog, tool, schema, and example file reviewed is byte-identical to `d7fc55c`. Later commits add only the QA report and this review's own documents.
- **Review date:** 2026-11-22. **Environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss` 0.2.4, `dss-python` 0.15.7, backend 0.14.5. Pinned sources: wrapper `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee` (0.2.4), engine `87d85c2622c8281b92255335bc7c09b11191b21d` (0.14.5). EPRI pages re-checked live on the review date.

## Method

Independent re-derivation, not a re-reading of the coder's or the reviewer's conclusions:

1. Re-ran every harness tool and diffed the readback matrix against the committed file.
2. Parsed `TCapacitorProp` and the property registration from the pinned `Capacitor.pas`, and `CapacitorProperties` from the installed 0.2.4 wheel by AST, then compared both against the 22 catalog rows.
3. Machine-checked all property-level citations for tag pinning and line ranges against the real length of each cited file, fetching any pinned file missing from the local cache rather than trusting an earlier count.
4. Re-derived the headline behavioral claims from source and reproduced the headline numbers on the pinned stack, including the three traps the package states as traps.
5. Ran a dedicated 8-path `States` probe, a `Like` copy probe, and a class-correct `NumSteps`/`Connection` enumeration check, because those rows carry the package's strongest claims.
6. Re-read every cited EPRI page over HTTP and compared its stated defaults with the pinned engine.

## Results

**SCHEMA RESULT: PASS.** `tools/validate_catalogs.py` exits 0 with 14/14 manifest and catalog schema pairs (`Draft 2020-12`, format checking on), including `references/capacitors/capacitor_properties.json` under the generalized element schema. Counts: `dss_capi.json` 102 records, `sources.json` 88, `examples.json` 12.

**RUNTIME RESULT: PASS.** `tools/run_examples.py` exits 0, 12/12 examples; both new examples (`capacitor-wye-shunt-altdss`, `capacitor-stepped-shunt-dss`) pass and are recorded `Observed-working`. `tools/readback_capacitor.py` exits 0 and its output is **identical to the committed `phase3b_capacitor_readback.json` except the `environment` block**. All eleven matrix sections reproduce: 22 default cells, three specification families, resize, filter edits, topology, series and delta power, step switching, unequal steps, ratings, and copy behavior.

## Coverage verification

| Check | Result |
|---|---|
| Catalog rows | 22 = 21 wrapper creation keywords + 1 identifier row; `Like` appears once as an action entry inside the 21 |
| Keyword fidelity | `CapacitorProperties` keys parsed from the installed wheel: 21/21, case-exact, no missing, no extras (`kvar`, `CMatrix`, `Cuf`, `NumSteps`, `States`, `NormAmps`, `EmergAmps`, …) |
| Engine coverage | `TCapacitorProp` declares 13 own members, all cataloged. The remaining eight rows are inherited `PDElement`/`CktElement` fields (`NormAmps`, `EmergAmps`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, `Enabled`) plus the `Like` action; attribution is correct |
| Required inputs | `required_properties` = `name`, `bus1`. Conditional in declared engine order: `(kvar, kV)`, `(cmatrix)`, `(cuf, kV)` |
| Citations | 110 row-level `source_refs` + 4 conditional = 114, 72 unique at row level; **all pinned** to `0.2.4`/`0.14.5`, none mutable |
| Range safety | **Zero ranges beyond EOF** against the real file lengths: `Capacitor.pas` 1111 (max cited L1055), `Capacitor.py` 834 (L817), `CAPI_Obj.pas` 2985 (L614), `PDElement.pas` 317 (L198), `PDClass.pas` 110 (L108), `CktElement.pas` 1206 (L205), `CktElementClass.pas` 144 (L99), `DSSObj.py` 471 (L425), `enums.py` 525 (L96), `CapControl.pas` 1244 |
| Landing spot-check | `enums.py#L90-L96` lands on `class Connection(IntEnum)` with `wye = 0`/`delta = 1`; `Capacitor.pas#L576` lands on `InitDblArray(FNumSteps, Fkvarrating, 1200.0)`; `Capacitor.pas#L68-L83` is the property enum |
| Engine records | 88 → 102; 14 added, all pinned to `0.14.5`, spans in bounds; 13 `pass`, 1 honestly `not-run` (`capi-capacitor-capcontrol-hook`, with null environment) |
| Source index | 77 → 88; 11 added, ids unique, EPRI entries undated with scope notes |
| Version metadata | `target_versions` records the wrapper, DSS-Python, backend, and DSS C-API pins **and** `opendss_documentation: "EPRI online documentation is mixed-version"`, so no reader can read the record as an unpinned current EPRI release |
| EPRI pages | All four cited pages return 200: `Capacitor1.html` (element), `Properties12.html` (vocabulary), `Capacitor.html` (legacy interface page), `CapControl1.html` (controller). `CapControl.html` returns 404 and is correctly not cited |
| Deferral markers | CapControl property coverage is deferred in three scope notes, and the one controller hook record is `not-run` |

**Defaults reproduced exactly:** `Phases` 3, `Bus1` generated, `Bus2` generated `<bus>.0.0.0`, `kV` 12.47, `kvar` `[1200.0]`, `Cuf` ≈20.46997 µF (derived), `R`/`XL`/`Harm` `[0.0]`, `CMatrix` `[]`, `NumSteps` 1, `States` `[1]` `int32`, `Conn` `Connection.wye` (0), `NormAmps` 75.00460594, `EmergAmps` 100.00614125, `FaultRate` 0.0005, `pctPerm` 100, `Repair` 3, `BaseFreq` 60, `Enabled` True, two terminals, three conductors, shunt.

**Ratings arithmetic re-derived:** 1200 kvar at 12.47 kV gives 1200/(√3 · 12.47) = 55.559 A; ×1.35 = 75.0046 and ×1.8 = 100.0061, exactly the recorded readbacks. The package's "135% and 180% of rated phase current" statement is therefore reproducible, and its claim that the wrapper docstring's 180% normal factor is wrong is correct.

**Traps re-verified in source and at runtime:** the Cuf-family accumulator gives ≈586.558 kvar solved output with automatic ratings of ≈1.2214e-05/1.6285e-05 A after `Cuf=[10]`; `CMatrix` accepts 6 lower-triangle and 9 full values and raises `#2020036` for 8 (`Capacitor.pas` L219-L224, L666-L670); a short `kvar` or `Cuf` array raises `#20200425` with the expected element counts; a one-to-many kvar resize divides 1200 kvar into four 300 kvar steps with all states on, and a Cuf-mode resize replicates the original Cuf; JSON export omits `NumSteps` while retaining the arrays; explicit `NormAmps` or `EmergAmps` stays frozen across kvar edits without setting the other rating (verified in all four combinations); `kvar=[100,200]` supplies ≈100.0097 kvar from either step while `Cuf=[7,14]` supplies ≈410.52 and ≈821.37 kvar.

## Findings

### E-1 — `states` description: "edit writes" is ambiguous and contradicts the row's own advice (minor, non-blocking)

The row reads: *"The pinned keyword, attribute, and edit writes tested silently kept the prior states. Write States using an explicit DSS text command and read it back."*

In DSS parlance the capitalised `Edit` command **is** the text command that works, so "edit writes" reads as working text writes in the same sentence that tells the reader to use text writes. My independent 8-path probe on the pinned stack separates the cases cleanly:

| # | Write path | Result |
|---|---|---|
| 1 | `Edit Capacitor.a States=(1,0,1,0)` (text, tuple) | **applied** → `[1,0,1,0]` |
| 2 | `Edit Capacitor.b States=[0,1,0,1]` (text, bracket) | **applied** → `[0,1,0,1]` |
| 3 | `Edit Capacitor.c State=(0,1,0,0)` (text, singular) | **applied** → `[0,1,0,0]` |
| 4 | `bank.States = np.array([0,1,1,0], dtype=np.int32)` | silent no-op → `[1,1,1,1]` |
| 5 | `bank.States = [0,0,1,1]` | silent no-op → `[1,1,1,1]` |
| 6 | `begin_edit()` → `States` assignment → `end_edit()` | silent no-op → `[1,1,1,1]` |
| 7 | `Capacitor.new(..., States=[0,0,0,1])` | silent no-op → `[1,1,1,1]` |
| 8 | `New Capacitor.h ... States=(1,0,0,0)` (text) | **applied** → `[1,0,0,0]` |

The matrix row `step_switching` agrees: `states_after_python_attribute` and `states_after_python_edit` both stay at the pre-write `[1,0,0,1]`, while `states_after_text_abbreviation` changes.

**Requested correction (E-1). APPLIED 2026-11-22 at owner direction** — the `states` description now reads "The pinned Python creation keyword, attribute assignment, and `bank.edit(States=...)` call tested silently kept the prior states; DSS text writes do change them." The specification was: In `references/capacitors/capacitor_properties.json`, `states` → `description`, replace *"The pinned keyword, attribute, and edit writes"* with *"The pinned Python creation keyword, attribute assignment, and `bank.edit(States=...)` call"*. The coder's build audit already words this correctly ("through Python creation kwargs, assignment, and `edit`"), and `docs/workflows/capacitor.md` already says "The pinned Python constructor keyword, attribute assignment, and `edit(States=...)` calls", so this aligns the machine-readable row with the prose that already ships. Non-blocking: the adjacent `dss_text_write: true` field and `notes[1]` carry the same information, and no runtime claim is wrong.

- [Wrapper States accessor](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Capacitor.py#L263-L274) · [Engine States write](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L472-L498) · [Matrix](../audits/phase3b_capacitor_readback.json)

### E-2 — the catalog rows do not disclose the EPRI default divergences the audit prose relies on (minor, non-blocking)

The build audit states that "EPRI's stated default kvar differs from the pinned engine's 1200 kvar constructor". I confirmed both halves independently: `Properties12.html` says **"Default is 600.0 kvar"** for `Kvar`, while the pinned constructor is `InitDblArray(FNumSteps, Fkvarrating, 1200.0)` (`Capacitor.pas#L576`), and the runtime default reads `[1200.0]`. The same page says `Emergamps` **"Defaults to 135% of Normamps"**, whereas the pinned engine derives `EmergAmps` at 180% of rated current (≈133.3% of `NormAmps`), which I reproduced above.

The catalog's `kvar` and `emergamps` rows state the correct pinned behavior but cite no EPRI divergence, and the record carries no note about it, so a reader who opens the catalog next to the EPRI page sees an unexplained contradiction. Every cited field is still supported by a pinned source, so this is a disclosure gap rather than an unsupported claim.

**Requested correction (E-2). APPLIED 2026-11-22 at owner direction** — `kvar` now ends "EPRI's vocabulary page states a 600 kvar default; the pinned constructor and this readback use 1200." and `emergamps` now ends "EPRI describes the emergency default as 135% of Normamps; the pinned engine derives it at 180% of rated current." The specification was: Append one clause each, without changing any value: `kvar` → "EPRI's vocabulary page states a 600 kvar default; the pinned constructor and this readback use 1200." and `emergamps` → "EPRI describes the emergency default as 135% of Normamps; the pinned engine derives it at 180% of rated current." Alternatively add a record-level `notes` entry. Either form keeps the row's single-source-per-field discipline visible.

- [EPRI properties vocabulary](https://opendss.epri.com/Properties12.html) · [Engine defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L546-L598) · [Engine rating factors](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L684-L692) · [Catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json)

### A-1 — Architect-owned correction applied: `Like` is both a DSS text keyword and a Python method (my handoff, not the package)

My coder handoff trap 14 said `Like` is "read-only on the object" and instructed "Catalog it as a creation keyword only". That is wrong in one direction and the coder was right: the wrapper exposes a callable `Like(name)` action method, so the catalog's `python_method: "Like"` plus `python_creation_status: "Raises AttributeError on the pinned wrapper"` is the accurate pairing. My probe confirms the matrix: `bank.Like("base")` returns `None`, copies the source's `kvar`, `kV`, `Conn`, `NumSteps`, and `States`, keeps the target's own `Bus1`/`Bus2`, and a delta source copies `Conn=delta` without recomputing terminals (the copy read two terminals, `Bus2` = `<target>.0.0.0`). Only the **creation keyword** is read-only (`'Capacitor' object attribute 'Like' is read-only`). Trap 14 of the handoff is rewritten accordingly. The package needed no change, and `docs/workflows/capacitor.md` already documents both paths.

- [Wrapper copy method](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Capacitor.py#L367-L375) · [Engine copy routine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L503-L544) · [Corrected handoff](../handoffs/Phase_3B_Capacitor_Coder_handoff.md)

### A-2 — Architect-owned correction applied: `State` is an accepted text abbreviation, not a removed v6 property (my handoff, not the package)

My coder handoff trap 9 listed `State` unqualified among the "v6-era properties that are gone", next to `Model`, `Vmin`, `Vmax`, `StepSize`, `Vharmonics`, `PctLead`, `PctLag`, `PtPhase`, `Userated`, and `Spectrum`. Three distinct facts were collapsed into one list:

- the plural **`States`** is the property and the only wrapper keyword;
- there is **no singular `State` property in the wrapper** (it is absent from `CapacitorProperties`, and `absent_python_properties` in the matrix records that);
- the **DSS text parser accepts `State` as an abbreviation** of `States` with array semantics — my probe 3 above (`Edit Capacitor.c State=(0,1,0,0)`) applied cleanly, and the matrix's `states_after_text_abbreviation` (`[0,0,1,1]`) shows the same.

Only the ten genuinely unknown names raised `#110`; `State` is not among them in the matrix's `unknown_dss_parameters` block. The package got this right — `notes[1]` states the abbreviation rule and `docs/workflows/capacitor.md` repeats it — so trap 9 is rewritten to separate wrapper absence from parser acceptance. The package needed no change.

- [Matrix](../audits/phase3b_capacitor_readback.json) · [Engine States write](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L472-L498) · [Corrected handoff](../handoffs/Phase_3B_Capacitor_Coder_handoff.md)

### O-1 — Eight row fields are still unvalidated (carried forward from package 4, non-blocking)

This package adds far more undeclared row fields than package 4, and the row subschema in `schemas/catalogs/element_properties.schema.json` still sets `additionalProperties: true`, so none of them is checked. Present uses in `capacitor_properties.json`: `array_element_type` (7 rows), `readback_type` (7), `array_length` (7), `dss_text_write` (2), `enum_type` (1), `python_write_status` (1), `python_creation_status` (1), `python_method` (1) — **8 fields, 27 uses**, none declared. They carry exactly the information a generator needs (dtype, shape source, write-path status, method name), and E-1 shows the risk: when a write path is described only in prose it drifts, while `python_write_status` states it unambiguously and is silently unvalidated. Recommended follow-up, not a package-5 defect: declare all eight in the shared row definition, with `enum_type`, `array_element_type`, and `readback_type` as enumerations, then adopt them in earlier elements during a later pass.

- [Shared schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json) · [Catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json)

### O-2 — QA's citation count is a different counting base, not a discrepancy (no action)

The QA/QC report counts "118 blob refs" where I measure 110 row-level refs. The difference is defined, not contradictory: 110 row `source_refs` + 4 `property_requirements.conditional` refs = 114 property-level citations, plus the 4 record-level `sources` entries = 118. I verified all 114 property-level and all 4 record-level URLs: every one is pinned, parseable, and in bounds. Recorded so a later reader does not treat the two numbers as a conflict.

### O-3 — `not-run` used correctly (no action)

`capi-capacitor-capcontrol-hook` records static controller-coupling facts as `tested.result = not-run` with a null environment, matching the build audit's scope statement that CapControl operation is deferred. This is the correct use of the label, and it is the only non-`pass` addition in the 14 new engine records.

## Limitations

- CapControl property coverage and controller operation remain deferred by owner scope; the coupling record is source-reviewed only.
- Runtime evidence covers the recorded assignment, snapshot, and solve cases. Harmonic-analysis solves, reliability studies, and feeder fixtures remain out of scope, and the project owner should not read the Cuf-family anomaly as a general statement about harmonic studies.
- Both examples are single-bank circuits against a source bus; bank interaction on a real feeder belongs to the Phase 4 fixtures.
- This review re-derived facts from pinned sources and re-ran the recorded tools. It did not re-validate packages 1–4 beyond confirming that their catalogs are untouched in `6663bea..d7fc55c`.

## Disposition

**PASS WITH FINDINGS.** The package is internally consistent, exactly cited, honestly labelled, correctly scoped against CapControl, and it reproduces on the pinned stack — including every trap it claims. The two package findings are wording/disclosure precision fixes that no runtime behavior depends on, and both can be applied in a single small commit at the owner's discretion. Two architect handoff statements were corrected (A-1, A-2); the schema declaration gap (O-1) is carried forward as a follow-up rather than a blocker. In both architect corrections the package was more accurate than my handoff, which is the second package in a row where that held.

With independent QA/QC reporting PASS and no blocking findings, nothing technical stood between package 5 and owner acceptance. **Resolved 2026-11-22:** the owner accepted package 5, E-1 and E-2 were applied to the catalog with no value, type, default, or citation changed, schema validation re-passed 14/14 and the examples re-passed 12/12 after the edit, and package 6 (Generator) is released to the coder.
