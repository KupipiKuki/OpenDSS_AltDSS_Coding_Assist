# Phase 4 Package 4.1 (Fixture Harness and Snapshot Goldens) — Architect/Auditor Review

**STATUS: PASS WITH FINDINGS** — nothing blocks the owner's disposition. One definition finding (E-1) is raised against my own Phase 4 design rather than the package, four observations are recorded, and one architect-owned clarification is applied.

- **Reviewed revision:** `d1acffc6d064418bf9f232ff2e779860ed395c2e` (package), with inputs vendored at `9736d46a3b30b7c3f7c10322bd3886f61fe78991`; `a55108c` re-pins the QA handoff and `345eca8` adds the QA report. **Baseline:** `f8fac0c` (Phase 4 preparation). **Branch:** `wp/phase4`. **Audit performed at:** `345eca8`, working tree clean.
- **Scope boundary:** `git diff --name-only f8fac0c..HEAD` lists 24 paths, all inside `docs/`, `opendss_altdss_library/examples/fixtures/`, `references/`, `schemas/catalogs/`, and `tools/`. No Phase 3 element catalog, example, schema, or manifest file changed; acceptance requirement 8 holds.
- **Review date:** 2026-11-21 local (2026-11-22 UTC). **Environment:** existing validation venv, Windows 11 AMD64, Python 3.14.6, `altdss` 0.2.4, `dss-python` 0.15.7, backend 0.14.5, `jsonschema` 4.26.0.

## Method

Re-execution and independent arithmetic, not a re-reading of the coder's or the reviewer's conclusions:

1. Hashed all nine vendored paths twice — working tree and `git cat-file -p HEAD:<path>` — and compared both to the values I recorded from the upstream commit during preparation, before the package existed.
2. Re-ran both harnesses and diffed the golden hashes against the recorded table.
3. Exercised every guard myself: tolerance boundary, exact-integer change, unapproved reason, missing reason, and a dirty fixture file, restoring the tree after each.
4. Checked golden physics rather than presence: circuit energy balance, reactive balance against the capacitor banks, and whether per-element losses sum to the circuit total.
5. Re-derived engine semantics for any number I doubted — `Vsource.NumTerminals()`, `Load.Losses()` units — before recording a finding. One suspicion (`Vsource` reporting two power entries for a one-terminal element) was disproved: a Vsource genuinely has two terminals.
6. Read the harness source for shortcuts before trusting its PASS: whether it re-solves or replays, and whether the update path can write without approval.

## Results

**SCHEMA RESULT: PASS.** `tools/validate_catalogs.py` exits 0 with **16/16** pairs, including `references/fixtures.json` (2 records) against `schemas/catalogs/fixtures.schema.json`. The new schema is strict — per-record `additionalProperties: false` with 16 required fields — which is stronger than the element schema was at the same stage. `run_examples.py` still passes **14/14**.

**RUNTIME RESULT: PASS.** `tools/run_fixtures.py` exits 0 with both fixtures PASS:

| Fixture | Buses | Elements | Converged | Total iter | Control iter | Lowest pu |
|---|---:|---:|---|---:|---:|---|
| ieee13 | 16 | 38 | yes | 2 | 1 | `611`, 0.960843 |
| ieee34 | 37 | 117 | yes | 25 | 6 | `890`, 0.923099 |

These reproduce the numbers I measured during preparation independently of the harness, which is the strongest available evidence that the tool solves rather than replays recorded values.

## Verified independently

| Check | Result |
|---|---|
| Byte identity, 9 vendored paths | **worktree = git blob = my pre-package upstream reference**, all nine, including the two 30-byte stubs and `License.txt` |
| The CRLF trap | `.gitattributes` holds `* -text`; CRLF files stay CRLF **in the blob** (`033ccd40…` matches in both), so a Linux checkout will not invalidate the checksums |
| Golden hashes | `f72d59d8…` (ieee13) and `b06282a6…` (ieee34) match the build audit's table |
| Circuit energy balance | ieee13: load 3454.6593 kW + losses 112.3917 kW = 3567.0538 kW = source magnitude, to the last digit |
| Reactive balance | source 1736.4395 kvar vs load 2094.5320 kvar; the 685.9528 kvar difference is the two capacitor banks (−685.95279 kvar summed) |
| Loss attribution | line losses 106.48475 kW + transformer losses 5.90696 kW = 112.39171 kW = `totals.losses_kw` exactly |
| Stack-pin enforcement | code compares installed `altdss`/`dss-python`/backend against both the fixture record and `manifest.json` `support_targets`, and `ctx.Version()` against the C-API pin, before compiling |
| Tolerance boundary | `+1e-9` pu on a bus voltage passes (no diff); changing `RegControl.reg1.tap` from 9 to 8 fails with `controls/RegControl.reg1/tap: value, expected 8, actual 9` — absolute tolerance on floats, exact on integers |
| Unapproved golden update | refused: `Record owner approval for revision 2 with the exact --reason before updating`, exit 1, goldens untouched |
| Missing reason | argparse refusal, exit 2 |
| Dirty fixture file | refused: `Golden update requires committed, clean fixture files` naming the modified path, exit 1 |
| Cleanup | every probe restored; fixture checksum re-verified to `033ccd40…` and `git status` clean afterwards |

The harness's own structure supports the verdict: it stages the verified redirect closure in a temporary directory, uses a fresh context per run, applies solver options only where they differ and then re-reads each one to prove it took, and publishes golden updates only after a lock, a second clean-tree check, a catalog-unchanged check, and rollback on write failure. The `--update-golden` path cannot write without a pre-existing approval entry carrying the exact reason, so the guard is structural rather than advisory.

## Findings

### E-1 — `losses_kw_kvar` is engine `Losses()`, not dissipation, and my design never said so (minor; architect-owned)

Per element the golden stores `losses_kw_kvar` from `element.Losses()` scaled by `0.001`. The units are right — for `Load.671`, `TotalPowers()` is `1155.0003 kW` while `Losses()` is `1_155_000.3 W`, i.e. the same quantity in watts — but for PC elements `Losses()` **is the element's own power**, not a loss. Measured class sums in the ieee13 golden:

| Class | Σ `losses_kw` | Reading |
|---|---:|---|
| Line | 106.48475 | dissipation |
| Transformer | 5.90696 | dissipation |
| Load | 3454.65929 | the load's consumption |
| Capacitor | 0.0 kW (kvar −685.95279) | the bank's reactive output |
| Vsource | −3567.05378 | the source's injection |
| **Σ all elements** | **≈ −0.003** | energy balance, not losses |
| `totals.losses_kw` | **112.39171** | the dissipation figure |

So a reader who sums `elements.*.losses_kw` and compares it with `totals.losses_kw` sees ~0 against 112.39 and can reasonably conclude the golden is inconsistent. The golden is not inconsistent; my design skeleton (§5) named the field without defining it, and the harness implemented the engine faithfully.

**Correction applied (architect-owned).** The Phase 4 design now defines the field: `losses_kw_kvar` is the engine's `Losses()` converted from W/var to kW/kvar, which for PC elements and the source equals their own power, so only passive elements contribute to `totals.losses_kw`, and `totals.losses_kw` is the sole dissipation figure. **Owner option, not applied:** if a dissipation-only per-element figure is wanted for Phase 5 consumers, the harness can add `passive_losses_kw_kvar` (or emit `null` for power-conversion elements) as a new `golden_revision`. I recommend documenting rather than adding a field, because the engine view is reproducible and a derived field invites disagreement with the engine.

- [Golden](../../opendss_altdss_library/examples/fixtures/ieee13/golden.json) · [Harness](../../opendss_altdss_library/tools/run_fixtures.py) · [Design §5](../phase_4/README.md)

### O-1 — `elements` includes control objects, so the 38/117 counts are not all power elements (no action, documentation applied)

The ieee13 golden's `elements` map holds 12 Line, 5 Transformer, 15 Load, 2 Capacitor, **3 RegControl** and 1 Vsource. RegControls appear with zero powers and are also present in `controls`; `NumCircuitElements` counts them, which is why the design's "38 elements" exceeds the 35 power elements. The design now states this, so a later reader does not infer that IEEE 13 has 38 pieces of plant.

### O-2 — the comparison deliberately ignores `python_version` and `platform` (no package action, documentation applied)

`compare()` skips those two `environment` keys by design, so a golden produced on Python 3.14 passes on another interpreter, while engine and wrapper pins remain exact. That is a sensible policy — those pins are what reproducibility depends on — but it was invisible outside a code comment. The design now records it, so a future reader does not mistake the skip for an oversight or assume a Python bump will be caught.

### O-3 — the omission table is duplicated into the fixture where it does not apply (cosmetic)

`ieee13/PROVENANCE.md` lists `34Bus/Run_IEEE34Mod*.dss`, `ieee34Mod2.dss` and `nmsu_linecode2_ABC.txt` as "deliberately omitted upstream files". None of those was ever a candidate for the 13-node fixture, so the table reads as if `13Bus` has a plot-bearing driver to omit. Harmless duplication, worth scoping to the fixtures tree when package 4.3 adds the forced-tap or daily variants and introduces genuinely fixture-specific omissions.

### O-4 — revision 1 approval is recorded as the package release (no action, recorded)

`golden_updates[0].approver` reads "Project owner (Phase 4.1 coding release)". That is defensible — the owner approved the package whose deliverable is the initial golden — and the tool nevertheless enforces an explicit approval entry for every later revision. Recorded so Phase 5 does not cite it as an explicit per-golden sign-off.

### Credit where the coder corrected me

The coder edited my design document in two places where it was wrong and one where it was thin: the golden skeleton now carries `revision_date` and the licence block, `buses` shows `nodes` with a **single** value for bus `611` (my sketch implied three phases at a one-node bus — the fixture is right and my example was wrong), and the catalog path conventions are stated. The coder also documented the two-iteration versus four-iteration behaviour: rewriting the already-active `SnapShot` mode reinitialises the solve, which is why the harness only writes options that differ. That note is the reason the golden's iteration counts are defensible, and it came from the coder's own probe rather than from my handoff.

## Limitations

- Snapshot scenario only. Regulator taps are recorded but control *action* under a time series is package 4.3; cross-interface agreement is package 4.4 and, since every interface wraps DSS C-API 0.14.5, would be an API-layer check rather than independent validation.
- The recorded regulator taps (ieee34 `creg1a=14, creg1b=4, creg1c=5, creg2a/b/c=13`) are the unforced solution. The upstream `Run_IEEE34Mod*.dss` drivers exist precisely to force the published taps (12/5/5/13/11/11); those drivers are deliberately not vendored, so the published-tap variant is not covered and should not be claimed.
- The only `LoadShape` in either circuit is the engine's built-in `default`, so these fixtures provide no LoadShape evidence.
- This review re-ran the package's own tools and its own arithmetic; it did not re-validate Phases 1–3 beyond confirming their files are untouched in `f8fac0c..d1acffc`.

## Disposition

**PASS WITH FINDINGS.** The fixture inputs are byte-identical to the pinned upstream commit in the working tree *and* in the repository blobs, the goldens are correctly generated, the guards are structural rather than advisory, and the numbers reconcile against independent arithmetic. The single finding is a definition gap in my own design, now closed, with a package option left to the owner. With independent QA/QC also reporting PASS, nothing technical stands between package 4.1 and acceptance, and packages 4.2 (RegControl), 4.3 (daily), 4.4 (cross-interface) and 4.5 (exit) remain as sequenced.
