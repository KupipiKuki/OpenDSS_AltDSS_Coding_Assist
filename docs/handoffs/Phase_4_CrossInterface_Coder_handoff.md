# Phase 4 Package 4.4 — Cross-interface comparison (coder handoff)

**Issued** 2026-11-21 · **Architect/Auditor** DeepSeek · **Coder** GPT-6.2 Sol · **QA/QC** Mistral 4
**Depends on** 4.1 (fixtures and goldens, frozen by decision 16) and the accepted 4.3. **Scope authority** decision 15: the cross-interface tool stays in Phase 4 and adds `opendssdirect.py` 0.9.4 to the pinned stack.

## Goal

One tool that solves the two pinned fixtures through all three Python interfaces and reports what agrees. Its value is narrow and must be stated as such: agreement proves the **API layer** is consistent, not that the numbers are right.

## The premise, verified before issuing this handoff

| Interface | Package | Resolves to |
|---|---|---|
| `altdss` | AltDSS-Python 0.2.4 | dss-python 0.15.7 → backend 0.14.5 |
| `dss` | DSS-Python 0.15.7 | backend 0.14.5 |
| `opendssdirect` | opendssdirect.py **0.9.4** (latest release, 2024-03-29, wheel `py3-none-any`) | **declares `dss-python==0.15.7`** and imports `dss` / `dss_python_backend` |

`opendssdirect` is therefore a compatibility facade over the same library, not an independent binding. All three report `DSS C-API Library version 0.14.5 revision 87d85c2…` in-process. **The tool, its workflow page, the catalog record and the build audit must each say that a pass demonstrates wrapper agreement and not numerical validation.** A reviewer who reads this package as independent verification has been misled by us, not by the engine.

## Measured agreement (my probes, `ieee13` snapshot, pinned stack)

| Quantity | altdss | dss-python | opendssdirect |
|---|---|---|---|
| `TotalPower` | `complex(-3567.0537784187272, -1736.4395103613474)` | `array([-3567.05377842, -1736.43951036])` | `[-3567.0537784187272, -1736.4395103613474]` |
| `Losses` | `complex(112391.7090551033, 327860.85643111396)` | `array([112391.7090551, 327860.85643111])` | `[112391.7090551033, 327860.85643111396]` |
| Buses / elements | 16 / 38 | 16 / 38 | 16 / 38 |
| Iterations / control | 2 / 1 | 2 / 1 | 2 / 1 |
| Bus `611` nodes | `[3]` | `[3]` | `[3]` |
| Bus `611` pu / deg | `0.960842743` / `115.738201998` | same | same |
| Regulator taps | `[9, 6, 9]` via `reg.TapNum` | `"9"`,`"6"`,`"9"` via text query | `"9"`,`"6"`,`"9"` via text query |

Values agree to the last printed digit, which is the expected result when one binary answers three times.

## Traps, all probed on the pinned stack

1. **`Text.Command` is a *string property* in dss-python 0.15.7, and a *method* in opendssdirect.** `d.Text.Command("Solve")` raises `TypeError: 'str' object is not callable`; the dss-python method is `Commands`. The same flip applies to `Result`: property in dss-python, method in opendssdirect. This is the single trap most likely to burn an afternoon, because the call site looks correct.
2. **`IDSS` has no `.Circuit` and no `.Solution`.** dss-python reaches them as `d.ActiveCircuit` and `d.ActiveCircuit.Solution`. `odd` keeps the classic `odd.Circuit` / `odd.Solution`. altdss uses the context: `ctx.Solution`, `ctx.Element`, `ctx.Bus`.
3. **Accessor kind flips between the two dss-derived surfaces.** On dss-python they are properties, on opendssdirect they are methods: `TotalPower`, `Losses`, `Iterations`, `ControlIterations`, `AllElementNames`, `Nodes`, `puVmagAngle`. Writing one adapter and calling `.TotalPower()` on both fails on exactly one of them.
4. **`ActiveClass.First` is an int property in dss-python**, so `ac.ActiveClass.First()` raises `TypeError: 'int' object is not callable`, while opendssdirect's `First()` is a method.
5. **Names differ between the two dss-derived surfaces:** `NumElements` (dss-python) versus `NumCktElements` (opendssdirect), `ActiveCktElement` versus `CktElement`.
6. **Two units in one API.** `TotalPower` is kW/kvar but `Losses` is **W/var** in all three. This is the 4.1 finding E-1 restated per interface; a comparison that skips the `/1000` reports a 1000× disagreement and looks like a real defect.
7. **`TotalPower` returns a `complex` in altdss and a two-element array/list in the others.** Normalise to a `(kw, kvar)` pair before comparing, and compare both parts.
8. **`RegControls.TapNumber` is a property for the *active* control, not an indexed lookup.** Passing an index returns `None` in opendssdirect and raises `TypeError` in dss-python. **Corrected 2026-11-22 during the Phase 4.5 review:** the opendssdirect argument is not swallowed. `RegControls.TapNumber(*args)` is a getter with no arguments and a **setter** with one, so the call *writes the active control's tap* — verified: `TapNumber(7)` moved the cursor's control from 9 to 7 and left the other regulators alone. A stray argument silently rewrites a regulator, which is worse than a wrong read. Source: `opendssdirect/RegControls.py#L267-L279` at 0.9.4. Worse, inside an `ActiveClass` walk in opendssdirect it returned **9 for all three regulators** while the true taps are 9/6/9 — so the proxy cannot be trusted for a per-object tap read. **Use the text query** `? RegControl.<name>.TapNum` (verified `"9"`, `"6"`, `"9"` on both dss-derived surfaces) or altdss object properties, and say in the workflow why.
9. **State is shared between dss-python and opendssdirect, and isolated for altdss.** `altdss.NewContext()` created a circuit that opendssdirect could not see (`(#8888) There is no active circuit`), but creating a circuit through `odd` while dss-python held one raised `(#266) Warning: Duplicate new element definition: "Vsource.source"`. **Run each interface in its own subprocess.** A single-process triangle either collides or silently compares one interface against itself.
10. **Both facades import as `dss`.** `from dss import dss` and `from opendssdirect import dss` bind the same name; aliasing is mandatory in any shared file, and sharing a process is unsafe anyway (trap 9).
11. **`Nodes` returns node *numbers*, not a phase count.** Bus `611` reports `[3]`, a single node numbered 3, and its voltage array has `2 × len(nodes)` entries as magnitude/angle pairs in per-unit and degrees. Do not format it as "3 phases".
12. **Element enumeration happens to match, and must still not be trusted.** `AllElementNames` returned exactly `[FullName() for ctx.Element]` in the same order on all three, including `Vsource.source` first. Compare **name-keyed** anyway: order is an interface detail, not a contract, and a tool that compares by index will mis-attribute a real difference some day.
13. **Iteration counts agree and should compare exactly.** 2 total and 1 control iteration on `ieee13`; treat them as discrete quantities under the design's tolerance table, not as floats.
14. **Version assertion is part of the deliverable.** Each adapter must read its engine version string and assert it contains `DSS C-API Library version 0.14.5`. A comparison that silently ran a different backend would otherwise be indistinguishable from a pass.
15. **`ieee34` too.** The tool compares both fixtures, 37 buses and 117 elements on `ieee34`, 6 control iterations. A tool that only runs `ieee13` has not exercised the second golden.

## Deliverables

| # | Artifact | Notes |
|---|---|---|
| 1 | `tools/compare_interfaces.py` | Runs each interface in its own subprocess against both fixtures in the snapshot scenario, asserts the engine version, compares name-keyed, applies the design tolerance table, and writes a committed report plus a printed summary. Exit non-zero on any disagreement |
| 2 | `references/python_interface_comparison.json` + schema use | **This catalog currently holds zero records** and validates as such. Populate it with the per-interface accessor mapping (the traps above, as data) and the measured agreement, with `source_refs` pinned to the three packages |
| 3 | `docs/workflows/cross_interface.md` | The three idioms side by side, the shared-backend caveat in plain words, the property-versus-method flip, the tap-read hazard, and the subprocess requirement |
| 4 | `examples/interfaces/compare_ieee13.py` | One runnable example that performs the comparison and asserts agreement, recorded `Observed-working` with its environment block |
| 5 | `tools/requirements-validation.txt` | Add `opendssdirect.py==0.9.4`, with a comment that it pins `dss-python==0.15.7`, so the stack stays one backend |
| 6 | `docs/audits/phase4_cross_interface_audit.md` | Build audit: environment, exact commands, the three version strings, and the comparison result per fixture |
| 7 | `references/sources.json` | Additive records for opendssdirect 0.9.4 and for the DSS-Python/AltDSS-Python relationship |

## Acceptance

1. `tools/compare_interfaces.py` exits 0 and reports agreement for both fixtures, with the engine version asserted per interface.
2. `validate_catalogs.py`, `run_examples.py` and `run_fixtures.py` still pass unchanged; the snapshot and daily goldens are byte-identical to `HEAD` before the package, proven by hash.
3. `python_interface_comparison.json` is non-empty, schema-valid, and its accessor mapping matches what the tool actually does — a documented mapping that the code contradicts is worse than none.
4. No Phase 3 catalog, fixture input, golden or schema changes; `git diff` stays inside `docs/`, `references/`, `examples/` and `tools/`.
5. The shared-backend limitation appears in the workflow page, the comparison catalog record, the build audit, and the tool's own output header — not only in one place.
6. The tap value is read by a route that reproduces 9/6/9, and the workflow states why `TapNumber` is not that route.
7. The `Losses` unit conversion is visible in the code and covered by an assertion that `losses_kw_kvar` is not 1000× the `TotalPower` figure.

## Out of scope

No new numerical validation, no alternative backends, no QSTS, no changes to the fixtures or goldens. Do not add `CapControl` or any deferred class (decision 17). Package 4.5 owns the exit: `troubleshooting.json`, the documentation pass, and plan/manifest reconciliation.
