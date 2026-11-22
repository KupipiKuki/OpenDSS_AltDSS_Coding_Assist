# Phase 3B Package 4 (Load) — Architect/Auditor Review

**STATUS: PASS** — no required corrections to the package; one architect-owned document correction applied; three non-blocking observations recorded.

- **Reviewed revision:** `37854f664369e61c9c2a7f22ee05a7295152685c` (Phase 3B: Load package), plus `ea04f3a` which only re-pins the QA handoff. **Baseline:** `b896db8`. **Audit performed at:** `a1e4665` on `wp/phase3`, working tree clean.
- **Scope boundary:** `git diff 37854f6..HEAD -- opendss_altdss_library/` returns only `README.md` and `manifest.json`, and every catalog, tool, and example file reviewed is byte-identical to `37854f6`. Later commits add only package-5 preparation, this review's documents, and the independent QA/QC report; none touch the package under review.
- **Review date:** 2026-11-21. **Environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss` 0.2.4, `dss-python` 0.15.7, backend 0.14.5. Pinned sources: wrapper `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee` (0.2.4), engine `87d85c2622c8281b92255335bc7c09b11191b21d` (0.14.5). EPRI pages re-checked live.

## Method

Independent re-derivation, not a re-reading of the coder's or the reviewer's conclusions:

1. Parsed `TLoadProp` and the property registration directly from the pinned `Load.pas`, and `LoadProperties` from the installed 0.2.4 wheel by AST, then compared both against the catalog.
2. Re-ran every harness tool and diffed the readback matrix against the committed file.
3. Machine-checked all `source_refs`: tag pinning, path existence at that tag, and every line range against the real file length of each cited file.
4. Re-derived the behavioral claims from source and reproduced the headline numbers on the pinned stack, including the cases the package states as traps.
5. Spot-verified the cited span for each engine record and each semantic claim that a reader would act on.

## Results

**SCHEMA: PASS.** `tools/validate_catalogs.py` exits 0 with 13/13 pairs, including `references/loads/load_properties.json` under the generalized element schema.

**RUNTIME: PASS.** `tools/run_examples.py` exits 0, 10/10 examples; both Load examples recorded `Observed-working`. `tools/readback_load.py` exits 0 and its output is **identical to the committed `phase3b_load_readback.json` except the `environment` block**. All nine matrix sections reproduce: 43 default cells, five families, family switching, allocation order, edit finalization, connections, shape assignment, scaled percents, ZIPV solve.

## Coverage verification

| Check | Result |
|---|---|
| Catalog rows | 43 = 42 wrapper creation keywords + 1 identifier row |
| Keyword fidelity | `LoadProperties` keys parsed from the installed wheel: **42/42, case-exact, no missing, no extras** |
| Engine coverage | `TLoadProp` has 38 members excluding `INVALID`; every one has a row. The five non-engine rows are `name`, `like` (identifier/action) and `spectrum`, `basefreq`, `enabled` (inherited), each marked as inherited |
| Required inputs | `required_properties` = `name`, `bus1`, `kv`; the five families are conditional, in `TSpecSets` order `(kW,PF) (kW,kvar) (kVA,PF) (xfkVA,AllocationFactor,PF) (kWh,PF,kWhDays,CFactor)` — the kWh set's second member is `PF`, matching the engine rather than the display name |
| Citations | 209 `source_refs`, 127 unique; all pinned to `0.2.4`/`0.14.5`; **zero ranges beyond EOF** against the real lengths (`Load.pas` 2257, `Load.py` 1725, `enums.py` 525, `DSSObj.py` 471, `CircuitElement.py` 562, `CktElement.pas` 1206, `PCElement.pas` 295, `PCClass.pas` 103, `CktElementClass.pas` 144, `Spectrum.pas` 412) |
| Row-to-source landing | Every row has at least one cited span that actually mentions the construct, and every keyword row cites `Load.py` |
| Engine records | 75 → 88; 13 added, all pinned to `0.14.5` with in-bounds spans; 10 `pass`, 3 honestly `not-run` |
| Source index | 67 → 77; 10 added, ids unique, pinned `version_or_ref`, EPRI pages undated with scope notes |
| Examples | Two added, `source_ids` all resolve, expected results specific and reproduced |

**Defaults reproduced exactly:** `Phases` 3, `Bus1` generated `l1_1`, `kV` 12.47, `kW` 10, `PF` 0.88, `kvar` 5.397428221380872, `kVA` 11.363636363636365, `Model` `ConstantPQ`, `Conn` `wye`, `Status` `Variable`, `Class` 1, `VMinpu` 0.95, `VMaxpu` 1.05, `RNeut` −1, `AllocationFactor` 0.5, `pctMean`/`pctStdDev`/`pctSeriesRL` 50/10/50, `CVRWatts` 1, `CVRVars` 2, `kWhDays` 30, `CFactor` 4, `NumCust` 1, `ZIPV` seven zeros, `VLowpu` 0.5, `XRHarm` 6, `Spectrum` `defaultload`, `BaseFreq` 60, `Enabled` True, four conductors, one terminal.

**Semantic claims re-verified in source:** `Duty` unset falls back to `Daily` (`CalcDutyMult`, L934-L942; unit header L14 "Dutycycle: Defaults to Daily shape"); `Daily` fills an unset `Yearly` (L636-L637); `Status=Fixed` applies only the growth factor and skips shape and global multipliers (L1026-L1029); `Exempt` skips the global multiplier only (L1035-L1093); conductor counts (L479-L492); voltage-base handling for wye and delta (L516-L560); ZIPV registration, `NoDefault` and the explicit-set flag (L396-L400, L719-L720); percent scales 0.01 (L407-L413); constructor derived values and the `defaultload` spectrum override (L873-L884).

**Spot-verified engine spans:** `L396-L400` ZIPV property, `L407-L413` percent scales, `L425-L433` object references with four `LoadShapeClass` entries and one `GrowthShapeClass` (matching the catalog's `reference_class` rows), `L449-L455` required/PF flags, `L479-L492` conductor counts, `L719-L737` ZIPV flag and `EndEdit`, `L873-L884` `puMean`/`puStdDev`/`puSeriesRL` and the spectrum override. Wrapper spans: `TotalPowers` L296-L303 and the `LoadModel`/`LoadStatus` members L252-L267 both match the catalog's enum values.

## Findings

### A-1 — Architect-owned correction applied (my handoff, not the package)

The Load coder handoff stated trap 15 unconditionally: that attribute writes leave `kvar`/`kVA` stale. That is imprecise, and the package's workflow and audit are more accurate than my handoff. Re-measured:

| Construction | Then `kW = 50.0`, `PF = 0.9` | Derived values |
|---|---|---|
| `Load.new("a")` (edit left open) | attribute writes | kvar 5.3974, kVA 11.3636 — **stale** |
| `Load.new("a"); end_edit()` | attribute writes | kvar 26.9871 → 24.2161, kVA 55.5556 — **recomputed** |
| `Load.new("a", begin_edit=False)` | attribute writes | kvar 5.3974 — **stale with no later recovery** |
| `Load.new("b", kW=12, PF=0.9)` | attribute writes | kvar 24.2161, kVA 55.5556 — **recomputed** |

The effect is an **edit-context** effect. The handoff's trap 15 has been rewritten with the three measured cases and the `begin_edit=False` hazard; the package needed no change. [Corrected handoff](../handoffs/Phase_3B_Load_Coder_handoff.md) · [Engine EndEdit](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L725-L737)

### O-1 — Two new row fields are unvalidated (non-blocking, schema follow-up)

`load_properties.json` adds two row fields that no earlier element catalog uses and that `element_properties.schema.json` does not declare: `enum_type` on `model`, `conn`, `status`, and `reference_class` on the five shape rows plus `spectrum`. The row subschema sets `additionalProperties: true`, so both pass validation without being checked. They carry real information — the wrapper enum name and the referenced object class are exactly what a reader needs — but an undeclared field can drift silently. Recommended follow-up, not a package-4 defect: declare both in the shared schema's row definition and adopt them in packages 1–3 during a later pass. [Schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json) · [Catalog](../../opendss_altdss_library/references/loads/load_properties.json)

### O-2 — Citation mismatch closed, coder credited

The coder's build audit independently found that `Properties17.html` is the Fault property page and used `Properties7.html` for Load. My handoff had them backwards; I confirmed the correction myself (`Properties7.html` contains `ZIPV`, `kWhDays`, and 13 `Load` mentions; `Properties17.html` contains 11 `Fault` mentions and none of the Load tokens) and fixed the handoff in `a1e4665`. The coder's `sources.json` was right from the start. No package action.

### O-3 — `not-run` labels are used correctly (no action)

Three engine records — `capi-load-shape-runtime`, `capi-load-zipv-low-voltage`, `capi-load-voltage-limits` — record static source facts as `tested.result = not-run` with a null environment, and the build audit says the same. This is the correct use of the label and the opposite of over-claiming; recorded here so a later reader does not mistake it for missing coverage. Time-series shape dispatch, ZIPV low-voltage sweeps, and voltage-limit service evaluation remain source-reviewed only.

## Limitations

- LoadShape and GrowthShape property catalogs stay deferred; their pages are cited for vocabulary only, consistent with the owner's scope decision.
- Runtime evidence covers assignment and snapshot behavior, not time-series dispatch or low-voltage ZIPV sweeps.
- The examples are single-load circuits; feeder-scale behavior belongs to the Phase 4 fixtures.
- This review re-derived facts from pinned sources and re-ran the recorded tools; it did not re-validate packages 1–3 beyond confirming that their catalogs are untouched in `b896db8..37854f6`.

## Disposition

**PASS.** The package is internally consistent, correctly cited, honestly labelled, and reproduces on the pinned stack. One architect document was corrected (A-1); the package itself needs no correction before the owner's disposition. Two follow-ups are recorded for later work (O-1 schema declaration) or for the record (O-2, O-3).

With independent QA/QC reporting PASS and no required corrections, nothing technical stands between package 4 and owner acceptance, and the package-5 (Capacitor) gate can be lifted.
