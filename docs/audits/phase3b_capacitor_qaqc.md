# Phase 3B Package 5 (Capacitor) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3` (synced with `origin/wp/phase3`). **Package revision under review:** `d7fc55c5de6ae6533af69aa17ce16bdf22e90026` (per the pinned handoff; tip `3558fbf` only re-pins the handoff). **Baseline for comparison:** `6663beaa2578748bd39749f42905341733bdfe5c`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; wheel `altdss-0.2.4-py3-none-any.whl`; engine `Capacitor.pas`, `CapControl.pas`, `CAPI_Obj.pas`, `PDElement.pas`, `PDClass.pas` at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`; EPRI pages checked live over HTTP.

**STATUS:** PASS (no blocking findings; no required corrections)

## Schema and runtime results

- **Schema: PASS, 14/14 pairs.** `tools/validate_catalogs.py` at `d7fc55c` exits 0, including the new `references/capacitors/capacitor_properties.json` under the generalized element schema; `dss_capi.json` 102 records, sources 88, examples 12.
- **Examples: PASS, 12/12.** `tools/run_examples.py` exits 0; both new examples (`capacitor-wye-shunt-altdss`, `capacitor-stepped-shunt-dss`) pass as recorded `Observed-working`; no version drift.
- **Readback matrix: PASS, reproduced.** `tools/readback_capacitor.py` exits 0 and its stdout is **identical to the committed `phase3b_capacitor_readback.json`** except `environment`/`date` (matching the pinned stack). All 22 rows are covered, with NumPy dtypes/shapes checked.

## Coverage findings

- Catalog shape matches the audit: one Capacitor record, 22 rows = 21 Python creation keywords + 1 identifier (+ `Like` as an action entry within the 21); every row has non-empty versioned `source_refs`; all 118 blob refs are pinned-tag, in-range, known files — no mutable refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** `CapacitorProperties` = 21 keys = the 21 catalog keywords exactly; all 20 wrapper `property()` names (excl. `_str`) cataloged. Casing verified (`kvar`, `CMatrix`, `Cuf`, `NumSteps`, `States`, `NormAmps`, …).
- **Engine correspondence (0.14.5):** `TCapacitorProp` at Capacitor.pas L68-L83 = 13 own members, all cataloged; the remaining catalog rows are inherited PDElement/CktElement fields (`NormAmps`, `EmergAmps`, `FaultRate`, `pctPerm`, `Repair`, `BaseFreq`, `Enabled`) plus the `Like` action — attribution correct.
- **Baseline preservation:** diff `6663bea..d7fc55c` shows zero deletions/modifications in `dss_capi.json` (88→102, +14), `sources.json` (77→88, +11), `examples.json` (+2); packages 1–4 catalogs and `altdss_python_api.json` untouched. All example `source_ids` resolve; no duplicate ids.
- **EPRI page distinction verified live:** `Capacitor1.html` 200 (element page, used as `epri_doc_url`), `Capacitor.html` 200 (legacy interface page documenting the CapControl reference to a capacitor — kept as `epri-capcontrol-capacitor-reference`), `Properties12.html` 200 (vocabulary), `CapControl1.html` 200 (`CapControl.html` is 404, correctly not cited). CapControl deferral is recorded in three scope notes; the audit's note that EPRI's stated default kvar differs from the pinned 1200 kvar constructor is consistent with the engine constructor (L546-L598).

## Source findings

- All 14 new `dss_capi.json` records cite `blob/0.14.5` files; every cited range was checked against the pinned sources and lands on the claimed construct: property enums L52-L86 + registration L200-L282, spec sets L208-L224 + required flags L260-L279 + family writes L375-L386 + RecalcElementData L614-L692, step arrays L226-L253 + resize L387-L459 + NumSteps flags L277-L279, kvar branch L625-L645, Cuf scale/formula L240-L244/L646-L665 + ratings L684-L692, CMatrix L219-L224/L666-L670/L963-L978, Bus1/Conn L303-L342 + Bus2 L343-L374, primitive selection L698-L748, States L250-L253/L472-L498/L721-L732/L861-L875, CapControl hook (CapControl.pas action handling L725-L788 with AddStep/SubtractStep at L745-L780), filter properties L232-L248/L462-L473, defaults L546-L598, MakeLike L503-L544. `tested` split of additions: 13 `pass` / 1 `not-run` (the CapControl hook, correctly source-only); all `pass` claims corroborated by the reproduced matrix.

## Runtime findings (probes reproduced on the pinned stack)

- **Three specification families** (kvar, Cuf, CMatrix) plus inactive readbacks in the switched family (kvar/Cuf intact, automatic ratings zero); CMatrix accepts the 6-value lower triangle and 9-value full array for three phases, and 8 values raised `#2020036`.
- **Unequal kvar steps:** `kvar=[100,200]` derived equal Cuf per step (first-entry reference in RecalcElementData) with each step alone supplying ≈100.0097 kvar; `Cuf=[7,14]` supplied ≈410.52 and ≈821.37 kvar — matches the audit.
- **Cuf rating anomaly:** after changing a 600 kvar bank to `Cuf=[10]`, stored kvar stayed 600, ratings read ≈1.221e-05 / 1.629e-05 A, and the solve supplied ≈586.56 kvar — the accumulator-scale discrepancy is real and documented.
- **States write divergence:** Python kwargs/attribute/`edit` writes left the old states in the probes while DSS text (incl. the `State=[0 0 1 1]` abbreviation) changed states and power; `Like` works via DSS text and the Python action method but raises `AttributeError` as a creation keyword; ten legacy probed names raised `#110`.
- **Topology/copy/ratings:** wye shunt (2 terminals, grounded Bus2 default), delta (1 terminal, Bus2 removed on wye→delta and regenerated on return), series wiring with a Load fixture, solved complex power per terminal, automatic ratings at 135%/180% of phase current in the kvar family, and explicit NormAmps/EmergAmps stickiness — all reproduced. Both examples converged (wye shunt −600 kvar; stepped DSS bank switching).
- Docs (README, plan v0.22, manifest) honestly state package 5 "awaits independent QA/QC"; manifest records 14/14 schema and 12/12 examples.

## Limitations (as documented, confirmed)

- CapControl property coverage and controller operation are deferred (scope notes in the source index; the hook record is `not-run`).
- Harmonic-analysis solves, reliability studies, and feeder fixtures remain out of scope; runtime evidence covers the recorded assignment/snapshot/solve cases.
- The wrapper docstring's normal-rating factor (180%) differs from the engine's kvar-family 135% — documented in the audit and consistent with the engine source (L684-L692).

## Required corrections

None.

No files were modified by this review; this report is the only file added.
