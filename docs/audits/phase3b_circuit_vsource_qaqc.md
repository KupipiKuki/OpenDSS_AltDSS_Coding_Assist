# Phase 3B Package 2 (Circuit and Vsource) — Independent QA/QC Report

**Reviewed branch:** `wp/phase3`. **Package revision under review:** `555f4f6f6cb86aef556bb61d7515f33a39780de8` (per the pinned handoff; tip `e37224c` only re-pins the handoff). **Baseline for comparison:** `861a6e6`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-21. **Reviewer environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5`; wheel `altdss-0.2.4-py3-none-any.whl` from PyPI; engine sources (`VSource.pas`, `Circuit.pas`, `DSSGlobals.pas`, `ExecHelper.pas`, `CktElement.pas`, `CktElementClass.pas`, `PCElement.pas`, `PCClass.pas`, `Spectrum.pas`, `Solution.pas`, `ExecOptions.pas`) at DSS C-API tag `0.14.5` = commit `87d85c2622c8281b92255335bc7c09b11191b21d`.

**STATUS:** PASS (no blocking findings; no required corrections)

## Schema and runtime results

- **Schema: PASS, 11/11 pairs.** `tools/validate_catalogs.py` at `555f4f6` exits 0 — including the new `references/circuit/vsource_properties.json` (2 records) paired with the generalized `element_properties.schema.json`, sources (51), examples (6), `dss_capi.json` (59).
- **Examples: PASS, 6/6.** `tools/run_examples.py` exits 0; both new `circuit-vsource-*` examples run clean with `Observed-working` records; environment block matches the pins, no drift warning.
- **Readback matrix: PASS, reproduced.** `tools/readback_circuit_vsource.py` exits 0 and its stdout is **identical to the committed `docs/audits/phase3b_circuit_vsource_readback.json`** except `environment`/`date` (which match the pinned stack). Matrix: 37 rows = 34 Python/context `read back` + 2 DSS-text `readback` (`z1`, `z0`) + 1 `action` (`like`) — exactly the audit's counts.

## Coverage findings

- Catalog shape matches the audit: Circuit = 1 identifier row (routing via `Commands("New Circuit.<name> …")`, readback via context `Name`); Vsource = 36 rows = 1 identifier + 33 creation keywords (incl. `Like`) + 2 DSS-text-only rows (`z1`, `z0`). Every row has non-empty `source_refs`; all 181 blob refs in the catalog (rows + conditionals + record sources) are pinned-tag (`0.2.4`/`0.14.5`), in-range, known files — no mutable `master` refs, none beyond EOF.
- **Wrapper correspondence (pinned 0.2.4 wheel, independent AST parse):** `VsourceProperties` TypedDict keys == the catalog's 33 `altdss_keyword` values exactly; wrapper `property()` set (32, excl. `_str`) == catalog keywords minus `Like`; `Z1`/`Z0` confirmed absent from the wrapper (the rows say so explicitly and carry no keyword, so no Python call is generated). Case-sensitive names verified (`MVASC3`, `puZ1`, `puZIdeal`, `BaseFreq`, …).
- **Engine correspondence (0.14.5):** `TVsourceProp` at VSource.pas L57-L90 has 31 members after `INVALID` through `puZIdeal` — matches the audit; catalog's 34 non-identifier/non-action rows = 31 own enum rows + inherited `spectrum`/`basefreq`/`enabled` (TPCElement/CktElement) — inherited attribution is exact.
- **Baseline preservation:** diff `861a6e6..555f4f6` shows zero deletions/modifications in `dss_capi.json` (45→59, +14), `sources.json` (34→51, +17), `examples.json` (+2 records only); package-1 catalogs, `altdss_python_api.json`, prior QA reports untouched. All `source_ids` in `examples.json` resolve; no duplicate source ids.

## Source findings

- All 14 new `dss_capi.json` records cite `blob/0.14.5` files; I checked every cited range against the pinned sources — all land on the claimed constructs: `TDSSCircuit` declaration/constructor (Circuit.pas L61-L118, L375-L395), `MakeNewCircuit` routing (DSSGlobals.pas L426-L449), `TVsourceProp` enum (VSource.pas L57-L90, exact), spec sets and property flags (L228-L352), PropertySideEffects/EndEdit/RecalcElementData (L395-L537, L710-L875), constructor (L607-L669), complex-ohmic rows and DSS access (L77-L83, L300-L311, L400-L418, L486-L507), grounded Bus2 (L369-L395, L497-L498, L613-L655), frequency init (L320-L321, L637-L647), inherited defaults (CktElement.pas L180-L204, PCElement.pas L78-L84), enum defaults (L251-L262, L644-L658), shapes/quasi-ideal (L264-L277, L436-L443, L656-L665, L903-L932). `tested` split of additions: 10 `pass` / 4 `not-run`; every `pass` claim is corroborated by the reproduced matrix (see below); `not-run` records are static source facts with null environment.
- One observation (non-blocking): the `z1`/`z0` rows carry `supported_in_target: true` while having no `altdss_keyword` — the description states the pinned Python wrapper has no `Z1`/`Z0` attribute, so the row is DSS-text-only in practice. Semantics are defensible (supported in the engine target); the description makes the Python gap explicit.

## Runtime findings (probes reproduced on the pinned stack)

- **Circuit routing:** `New Circuit.routed …` creates exactly one `Vsource.source`; Bus2 defaults to `src.0.0.0` (grounded) until explicitly set, and an explicit Bus2 survives a later Bus1 edit; 2 terminals; solved bus `src` reads nodes [1,2,3]; no `ctx.Circuit` member and no `altdss/Circuit.py` module in the pinned install — Circuit is command-routed, as the workflow states.
- **Base scaling:** 115 kV default-MVA source read back derived ohms [1.604, 6.415, 1.796, 5.388]; after `BasekV=12.47` the ohms scaled by the ZBase ratio (132.25 → 1.555 Ω) while `puZ1` was retained within 1e-9 — matches `capi-vsource-zbase-scaling` (VSource.pas L510-L523, L628-L635, L710-L727).
- **Five impedance families + precedence:** MVA, current (with X1R1=10 ratio edit applying to the active family), scalar ohms, complex ohms via DSS text (`Z1`/`Z0` query works in DSS text; Python attributes confirmed absent; `Z2` readable in Python), and explicit per-unit (converted at ZBase) all verified; `puZ1` stays active over later scalar edits and retains its stored value in the MVA branch — the documented precedence limit (VSource.pas L761-L875) is real and correctly disclosed in the workflow.
- **Frequency:** `DefaultBaseFrequency=50` initializes solution, source, and element base frequency to 50 Hz; later edits independently moved solution→55 Hz and element base→48 Hz while source stayed 50 Hz.
- **Scope honesty:** the two runnable examples solve single-source illustrative circuits; standalone default/scaling probes are labeled unsolved in the matrix; multi-source/harmonic/shape and Phase 4 fixtures are explicitly out of scope. No overclaiming found.

## Limitations (as documented, confirmed)

- `puZ1` can override later scalar ohmic edits within the impedance branch and retain its stored display value after returning to the MVA family; the workflow recommends separate source definitions for cross-family comparisons.
- Python wrapper exposes `Z2` but not `Z1`/`Z0`; DSS text covers those (verified by query readback).
- Examples are illustrative single-source solves; standalone probes unsolved by design.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
