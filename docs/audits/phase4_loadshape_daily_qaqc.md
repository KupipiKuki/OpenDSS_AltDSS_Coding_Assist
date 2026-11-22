# Phase 4.3 LoadShape catalog and daily profile — Independent QA/QC Report

**Reviewed branch:** `wp/phase4` (tip `df897bc`, synced with `origin/wp/phase4`; the tip is docs-only — it pins the handoff's package-revision line, verified by `git diff 2e4d92b..df897bc`, one line in the QA/QC handoff). **Package revision under review:** `2e4d92b40b799280ed23429314b2ddddae75de7a` (per the pinned handoff at `df897bc`). **Inputs/baseline revision:** `5efeaf1a97f4a63b5f4ec828cc63df71ded4ee2e`. **Reviewed state:** `git status --porcelain` clean; `git diff --check 5efeaf1..df897bc` clean.
**Review date:** 2026-11-22. **Reviewer environment:** fresh venv built from `tools/requirements-validation.txt`, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine self-reports `DSS C-API Library version 0.14.5 revision 87d85c2622c8281b92255335bc7c09b11191b21d`), `jsonschema 4.26.0`; wrapper source = installed `altdss-0.2.4` wheel; engine sources = `src/General/LoadShape.pas` (2385 lines, matching the handoff's count) and `src/General/DSSObjectHelper.pas` at DSS C-API tag `0.14.5` (`87d85c2…`), fetched live from raw.githubusercontent.com.

**STATUS:** PASS (no blocking findings; no required corrections)

## Run verification (fresh runs on the pinned stack, `python -B` from the repo root)

- `tools/validate_catalogs.py` → exit 0, **18/18 schema pairs**, including `references/loadshapes/loadshape_properties.json` paired with the **existing** `element_properties.schema.json` (`validate_catalogs.py` gained exactly the one 3-line pair entry; no element schema changed).
- `tools/run_examples.py` → exit 0, **18/18 PASS**. Both new examples pair hours with powers as required: `loadshape-daily-steps-altdss` printed `Hour 1: 50.000 kW`, `Hour 2: 100.000 kW`, `Hour 3: 150.000 kW` (the example asserts `solution.Hour == hour` **and** the kW, so an off-by-one fails it); `loadshape-daily-monitor-dss` PASS with the monitor capture checked by the readback runner.
- `tools/run_fixtures.py` → exit 0, **3/3 PASS**: ieee13 snapshot (16 buses, 38 elements, 2 total / 1 control iterations, lowest 611 @ 0.960843 pu), ieee13 daily (24 hours, 73416.540 kWh, peak 4004.671 kW at hour 18, lowest 611 @ 0.952044 pu at hour 18), ieee34 snapshot (37 buses, 117 elements, 25/6 iterations, lowest 890 @ 0.923099 pu).
- `tools/readback_loadshape.py` → exit 0, stdout **byte-identical to the committed `phase4_loadshape_readback.json`** after newline normalization (in fact fully identical, capture date 2026-11-22 included). All sections populated: 22 defaults, `empty_shape_csvfile`, `length_contract`, `npts_growth`, `interval_units`, `actions_and_alias`, `stepping`, `use_actual`.
- Selector guards: `--fixture ieee34 --scenario daily` → FAIL "No daily scenario for the selected fixtures"; `--fixture bogus` → FAIL "Unknown fixture 'bogus'. Available: ieee13, ieee34".

## Surface correspondence (pinned sources, independent parse)

- Catalog: 1 record, `element_class: LoadShape`, **22 rows**; `required_properties` = `name`, with the `NPts`+array ordering requirement in `property_requirements.conditional` as the handoff specified.
- Wrapper (AST parse of installed `altdss/LoadShape.py` @0.2.4): `LoadShapeProperties` TypedDict has exactly the same **22 keys** as the catalog's `altdss_keyword` set (case-insensitive equality confirmed); the `LoadShape` class has 21 `property(...)` assignments — every catalog keyword except `Action` and `Like`, which are methods and are catalogued with `python_method` status instead (same pattern as 4.2).
- All **133** row `source_refs` are pinned-tag blob URLs (`/blob/0.2.4/` or `/blob/0.14.5/`); **28** wrapper refs and **105** C-API refs bounds-checked against the installed wheel and the fetched Pascal sources — zero past-EOF, zero mutable refs. Spot checks land on the claimed content: each row's first single-line wrapper ref points at its own TypedDict annotation (e.g. `NPts: int` at `LoadShape.py#L415`, `PMult: Float64Array` at L432).
- EPRI: the catalog cites only `LoadShape.html` (checked live, **200**) — no `Properties*` page is cited for LoadShape, matching the handoff's warning.
- Live default probe on a fresh shape matches every catalog `default_value`: `NPts` 0, `Interval` 1.0 / `SInterval` 3600.0 / `MInterval` 60.0, `Hour`/`PMult`/`QMult` empty, `Mean`/`StdDev` 0.0, `UseActual` False, `PMax` 1.0 / `QMax` 0.0, `PBase`/`QBase` 0.0, file properties empty, `MemoryMapping` False, `Interpolation` `Avg` (0).
- Traps independently reproduced on the pinned stack: `Npts` → `AttributeError`; `PMult` before `NPts` → `(#20200425) … Expected 0 elements, got 24.`; `SInterval=1800` moves `Interval` to 0.5 and `MInterval` to 30 (one field, three units); `Action("Normalize")` rescaled `[1,2,4]` → `[0.25,0.5,1.0]` in place; `Like` copied `NPts` and the arrays; DSS text `mult=(…)` alias round-trips; a fresh circuit iterates exactly `['default']`; reading `CSVFile` on an empty shape raises `(#61107) LoadShape has no data to be normalized. Check for previous errors.` (the deferred-statistics error the matrix records deliberately); `LoadShapeAction` = Normalize 0 / DblSave 1 / SngSave 2, `LoadShapeInterpolation` = Avg 0 / Edge 1, `LoadShapeClass` = none −1 / Daily 0 / Yearly 1 / Duty 2 — distinct from the `Load.Daily` object reference, and the workflow states that distinction.
- Readback matrix content matches the audit's narrative: both normalization paths (default peak-division → `[0.25,0.5,1.0]`, explicit `PBase`/`QBase` → peak 2 with `UseActual` cleared), actual values (50 kW / 10 kvar at hour 1 despite explicit 200/100 bases), the Python-vs-DSS `Hour` setter difference (`interval_after_hour_write`: AltDSS-Python 1.0 vs DSS text 0.0), `Number=24` advancing hour 0→24 in one solve vs `Number=1` per-step sampling at hours 1–3 = 50/100/150 kW in both interfaces, and `circuit_elements_before_and_after` = [2, 2] (a shape is not a circuit element).
- `sources.json` 110 → 119, `dss_capi.json` 134 → 144, `examples.json` 16 → 18 — **purely additive** (id-keyed comparison: zero removed, zero pre-existing records changed). The two new example records have resolving `source_ids`, full environment blocks, and `Observed-working` status.

## Golden numerical checks (independent of the harness code)

Parsed `examples/fixtures/ieee13/golden_daily.json` directly and recomputed:

- `scenario: "daily"`, `golden_revision: 1`, solver `mode: Daily`, `step_size_s: 3600.0`, `control_mode: Static`, `base_freq: 60.0`. The `shape` block is **identical** to `fixtures.json`'s `daily.shape` (name `daily24`, 24 points, pmult 0.60–1.16, `use_actual: false`, `assignment: "Load.daily"`).
- 24 step records, hours exactly 1–24, all converged. First step: hour 1, 2399.365304530277 kW.
- Energy: recorded `integrated` 73416.54014883187 kWh, recorded `from_steps` 73416.54014883189 kWh, my independent `math.fsum(load_kw * step_size_s/3600)` 73416.54014883189 kWh — all three agree within the recorded 1e-6 rel / 1e-6 kW tolerance.
- Peak: `max(steps, key=load_kw)` is hour 18 at 4004.670549958446 kW, equal to `peak_step.hour` (derived, not hand-picked). `peak_step` carries the full capture: **16 buses, 38 elements** (element classes Line/Transformer/Load/Capacitor/RegControl/Vsource — **no LoadShape** in `elements`).
- **15 `Load.*` elements** in `peak_step` — all 15 ieee13 loads shaped via `Load.daily`.
- Per-step `controls` carry all three regulators and both capacitor banks: `RegControl.reg1` taps {7,8,9,10,11}, `reg2` {6,7}, `reg3` {7,8,9,10,11}, and `Capacitor.cap1`/`cap2` fixed at states `[1]` all day (energised, not switched — no CapControl exists in the circuit, per decision 17).
- Lowest bus over the day: 611 @ 0.9520444393688189 pu at hour 18 (matches the audit's 0.952044439).
- Tolerance application (code review of `exact_or_close`/`compare`): `pu_vmag`/`pu_vangle_deg` compare absolute 1e-6 under `buses`/`lowest_bus` (with `peak_step`/`steps` path normalization), powers/totals/energy compare 1e-6 relative with 1e-6 kW floor, everything else exact, and `environment.python_version`/`platform` are report-only. Confirmed empirically: a +1e-3 pu edit to one step's `lowest_bus.pu_vmag` fails with diff `steps/5/lowest_bus/pu_vmag: value, expected 0.9925033…, actual 0.9915033…`.

## Regeneration and failure modes (disposable git worktree at `2e4d92b`)

- Reset the daily scenario to revision 0 with the recorded revision-1 approval pending and the golden file removed, committed, then ran `run_fixtures.py --fixture ieee13 --scenario daily --update-golden --reason "Initial IEEE 13 daily golden for Phase 4 package 4.3"` → PASS, and the regenerated `golden_daily.json` is **byte-identical** to the committed blob (SHA-256 `0f8d5400e4558223dcd19d16a0e9a6370bc07e2e6f7bed3d6bf5a284541012f2`); the rewritten `fixtures.json` is content-identical to `2e4d92b` with `daily.golden_revision` advanced 0 → 1.
- Failure modes all fail as designed: `--update-golden` without `--reason` → argparse error exit 2; wrong `--reason` → FAIL "Record owner approval for revision 2 with the exact --reason before updating"; revision 0 with no approval → FAIL "No recorded golden revision. Run an approved initial golden update."; corrupted `energy_kwh` → FAIL "Daily golden energy_kwh does not match its step integral"; wrong `peak_step.hour` (17) → FAIL "Daily golden peak_step does not match the highest load_kw"; +1e-3 pu step voltage → FAIL with the single-path diff above.
- Existing named snapshot update path checked separately: with a disposable revision-2 approval on the ieee13 snapshot record, `--fixture ieee13 --scenario snapshot --update-golden --reason "…"` advanced **only** `ieee13/golden.json` to revision 2 (differs from revision 1 solely in `/golden_revision` and `/update_reason`); `golden_daily.json` (`0f8d5400…`) and `ieee34/golden.json` (`b06282a6…`) stayed byte-identical, and a subsequent full compare passed 3/3.

## Baseline preservation and scope

- Snapshot goldens hashed against the baseline blobs and the working tree — all identical: ieee13 `golden.json` = `f72d59d84abae341f1525d190bed54ce885c4a89e0a26c01944bf85c49eef5f4`, ieee34 `golden.json` = `b06282a66308a44c248f07e32211b77b0ae3b678737ecee2b496032e89b2709f` at `5efeaf1`, at `df897bc`, and on disk (decision 16 freeze holds; the daily golden is a separate file, absent at baseline).
- All 8 upstream fixture input files plus `License.txt` match the bytes and SHA-256 recorded in `fixtures.json` and `PROVENANCE.md` (verified from disk: e.g. `IEEE13Nodeckt.dss` 8354 B `033ccd40…`, `License.txt` 1816 B `f1354327…`).
- `git diff 5efeaf1..2e4d92b` touches exactly 18 files, all inside `docs/`, `references/`, `examples/`, `tools/` — the expected package set. Path-filtered diffs confirm: no Phase 3/4.1 catalog changed except the additive index records; no 4.1 fixture input changed; the 4.2 readback matrix and QA/QC report are untouched; the RegControl changes are confined to the **F-1 rider** — one clause in the `ptphase` row of `references/regcontrols/regcontrol_properties.json` ("an out-of-range positive index reading back as 1 in local sensing") and one sentence in `docs/workflows/regcontrol.md`; among schemas only `fixtures.schema.json` changed (the `dailyScenario` `$def` plus a `goldenUpdates` refactor, which the daily scenario genuinely needs); `manifest.json`, `docs/implementation_plan.md`, and `docs/phase_4/README.md` are unchanged (plan/manifest reconciliation stays with package 4.5).
- The handoff pin commit `df897bc` changes only the package-revision line of the QA/QC handoff.

## Limitations (as documented, confirmed)

- `npts_growth` is labelled source-only for the unsafe resize path (NPts changes the count without reallocating populated buffers); the matrix demonstrates the supported replacement-and-rebind workflow instead. Runtime validation covers the standard in-memory shape paths; file reads, memory mapping, binary saves and nondefault interpolation are pinned-source coverage.
- The daily golden exercises `UseActual=False` with per-unit multipliers; the `UseActual=True` path is validated by the readback section, not by the golden.
- Plan and manifest reconciliation remains scheduled for package 4.5.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
