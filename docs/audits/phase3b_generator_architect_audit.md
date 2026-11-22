# Phase 3B Package 6 (Generator) — Architect/Auditor Review

**STATUS: PASS WITH FINDINGS** — nothing in the package blocked the owner's disposition, and the owner accepted package 6 on 2026-11-21 (local) directing E-1 and E-2 to be applied first. **Both findings are applied**, which also closes the Phase 3 exit gate. Two evidence findings are recorded (E-1 the enum text-write behaviour is understated, E-2 the EPRI default divergences are not disclosed in the rows), five architect-owned handoff statements are corrected (A-1 to A-5), and one schema follow-up is confirmed partly closed (O-1).

- **Reviewed revision:** `0a88ad3bb2b1199eeb06fbd30f58baa0477b9a61` (Phase 3B: Generator package), plus `fe5f9c2` (re-pins the QA handoff) and `cb6a098` (the independent QA/QC report). **Baseline:** `f0d487ec9e93fce200e6f30f431ffe0ff77217c8` (package-5 acceptance). **Audit performed at:** `cb6a098` on `wp/phase3`, working tree clean.
- **Scope boundary:** `git diff --stat 0a88ad3..HEAD` shows only the pinned QA handoff and the QA report after the package commit, so every catalog, tool, schema, workflow, and example file reviewed is byte-identical to `0a88ad3`.
- **Review date:** 2026-11-21 local (2026-11-22 UTC). **Environment:** fresh venv, Windows 11 AMD64, Python 3.14.6, `jsonschema` 4.26.0, `altdss` 0.2.4, `dss-python` 0.15.7, backend 0.14.5. Pinned sources: wrapper `2b6fa7e5961cedaf8482c07d377b20bdab4a1bee` (0.2.4), engine `87d85c2622c8281b92255335bc7c09b11191b21d` (0.14.5). EPRI pages re-checked live.

## Method

Independent re-derivation, with the package's own tool treated as a claim to test rather than as evidence:

1. Re-ran every harness tool and diffed the committed matrix byte-for-byte.
2. Parsed `TGeneratorProp` from the pinned `generator.pas` and `GeneratorProperties` from the installed 0.2.4 wheel by AST, then compared both to the 49 rows.
3. Machine-checked every citation for pinning, parseability, span ordering, and range against the real length of each cited file, fetching each pinned file fresh rather than reusing an earlier cache.
4. Re-derived the constructor defaults from `generator.pas` L937-L1046 and compared them cell by cell with the matrix.
5. Wrote independent probes for the claims most likely to be wrong: the defaults trio, the automatic rating, the `MVA` alias, the `Like` conductor count, the `Fuel`/`Refuel` paths, the three guard errors, and a four-path `DispMode` matrix (Python attribute, DSS text name, DSS text number, low-level integer).
6. Ran the committed DSS example directly and read the bus voltage, rather than accepting the tool's recorded figure.

## Results

**SCHEMA RESULT: PASS.** `tools/validate_catalogs.py` exits 0 with **15/15** pairs, including `references/generators/generator_properties.json`. Counts: `dss_capi.json` 119 records, `sources.json` 99, `examples.json` 14.

**RUNTIME RESULT: PASS.** `tools/run_examples.py` exits 0, **14/14** examples; both new examples are recorded `Observed-working` with a matching environment. `tools/readback_generator.py` exits 0 and its output is **identical to the committed `phase3b_generator_readback.json`, all twelve sections, including the `environment` block**. Independently, the committed DSS example converges in 7 iterations with the generator terminal at **−799.9997 kW / −3000.0001 kvar**, scheduled `kW` 800, `kvar` 431.794, `PF` 0.88, and the remote bus at ≈1.0044 pu — the recorded `1.00443` is real, not a tool artefact.

## Coverage verification

| Check | Result |
|---|---|
| Catalog rows | 49 = 47 wrapper creation keywords (two of them actions, `Like` and `Refuel`) + 1 identifier + 1 DSS-text-only `mva` |
| Keyword fidelity | `GeneratorProperties` keys parsed from the installed wheel: **47/47, case-exact, no missing, no extras**. `VMinpu`/`VMaxpu` casing confirmed the hard way — the wrong casing raises `AttributeError` |
| Engine coverage | `TGeneratorProp` = **44** members after `INVALID`; every one has a row. The other five rows are `name`, the three inherited members (`Spectrum`, `BaseFreq`, `Enabled`), and the `Like` action. `cls` → row `class` → keyword `Class` matches the Load precedent |
| `MVA` handling | Absent from the wrapper (confirmed by AST), present in the engine enum, marked `supported_in_target: false` with `dss_text_keyword: MVA`. `g.MVA` raises `AttributeError`; `Edit ... MVA=3` sets `kVA` 3000. Correct |
| Required inputs | `required_properties` = `name`, `bus1`, `kv`; provenance verified (`kV` and `Bus1` are `Required` in the engine registration) |
| Conditional families | `(kw, pf)` and `(kw, kvar)` in engine declaration order, with the `kvar`-after-`kW` rule and the explicit note that `kVA`/`MVA` are ratings outside the families |
| Citations | 242 row-level + 10 conditional = **252** refs, 155 unique, across 9 files; **all pinned**, all parseable, **none reversed, none beyond EOF** (`generator.pas` 2946 max L2897, `Generator.py` 1835 max L1818, `DSSObj.py` 471, `enums.py` 525, `Spectrum.pas` 412, `PCElement.pas` 295, `CktElement.pas` 1206, `CktElementClass.pas` 144, `PCClass.pas` 103) |
| Engine records | 102 → 119; 17 added, all pinned to `0.14.5`; **13 `pass` / 4 `not-run`**, the four being dispatch checks, `PVFactor` sensitivity, controller scope, and dynamic-model scope — all source-only with null environment |
| Source index | 88 → 99; 11 added, ids unique, EPRI entries undated with scope notes. 0 removals, 0 modifications in all three shared catalogs |
| Examples | 14 → both new examples `Observed-working`, every `source_id` resolves, no duplicate ids |
| Version metadata | `target_versions` carries all four pins **plus** `opendss_documentation: "EPRI online documentation is mixed-version"` — no reader can read this as an unpinned current EPRI release |
| Schema change | Three **optional** string fields added to the shared row definition (`enum_type`, `reference_class`, `dss_text_keyword`); additive only, and packages 1–5 still validate unchanged |

**Defaults re-derived from `generator.pas` and matched to the matrix:** `kWBase` 1000, `kvarBase` 60, `kvarMax`/`kvarMin` ±120, `PFNominal` 0.88, `Conn` wye, `GenModel` 1, `Vpu` 1.0, `VMinpu` 0.90, `VMaxpu` 1.10, `puXdp` 0.28, `puXdpp` 0.20, `XRdp` 20.0, `PVFactor` 0.1, `kVArating = kWBase × 1.2` = 1200 with `kVANotSet` set, `SpectrumObj = DefaultGen`, `pctFuel` 100, `pctReserve` 20, `FuelkWh` 0, `UseFuel` false, one terminal, four conductors for wye.

**Claims re-verified by independent probe:**

| Claim | Independent result |
|---|---|
| `kVA` follows 1.2 × signed kW until written | `kW=2000` → 2400; explicit `kVA=5000` then `kW=3000` → **still 5000**, kvar recomputed to 1619.23 |
| `MVA` is text-only | `Edit ... MVA=3` → `kVA` 3000; `g.MVA` → `AttributeError` |
| `Like` keeps the target's conductors | Delta source (3 conductors) copied into a wye target: `Conn` became delta, **conductors stayed 4**, bus unchanged, `Like()` returned `None` |
| `Like`/`Refuel` keywords are read-only | Both raise `AttributeError: 'Generator' object attribute ... is read-only` |
| `Refuel` restores fuel only | `(pctFuel 40, pctReserve 15, FuelkWh 100)` → `(100, 15, 100)` via both the method and `Refuel=yes`; method returns `None` |
| Model 6 guards | `#567` on solve without a model, `#570` for an explicitly missing DLL, `#401` for a missing `DynamicEq` — all reproduced verbatim |
| `pctFuel`/`pctReserve` text names | `pctFuel=40` raises `#110 Unknown parameter`; `%Fuel=40 %Reserve=15` works — the new `dss_text_keyword` field is load-bearing |
| Model 1 example | `−999.99999 kW / −328.684 kvar` against a 1000 kW, PF 0.95 schedule |

## Findings

### E-1 — enum text writes are silently discarded, and the package only documents the Python half (minor, actionable)

The matrix records one enum anomaly: `dispatch_review.invalid_python_enum_readback = "3 is not a valid GeneratorDispatchMode"`. The build audit words it as *"Writing a numeric DispMode of 3 succeeded in the probe. The Python getter then rejected the value during enum conversion."* That is true of the **Python attribute** path only, and the more dangerous path is not recorded anywhere. My four-path probe on the pinned stack:

| Property | Write path | Stored integer | Read back |
|---|---|---|---|
| `DispMode` | `Edit ... DispMode=Loadlevel` / `=Price` / `=Default` | 1 / 2 / 0 | correct member |
| `DispMode` | `Edit ... DispMode=1`, `=2`, `=3` (numeric text) | **stays 0** | `Default` — **no error raised** |
| `DispMode` | `g.DispMode = 2` | 2 | `Price` |
| `DispMode` | `g.DispMode = 3` | **3** | `ValueError: 3 is not a valid GeneratorDispatchMode` |
| `Status` | `Edit ... Status=Fixed` / `=Variable` | 1 / 0 | correct member |
| `Status` | `Edit ... Status=1` | **0** | `Variable` — **silent, wrong** |
| `Conn` | `Edit ... Conn=delta` | 1 | `delta` |
| `Conn` | `Edit ... Conn=1` (numeric text) | unchanged | raises `#303 Could not match enum ("Connection") value "1"` |
| `Model` | `Edit ... Model=3` | 3 | `ConstantPV` |
| `Model` | `Edit ... Model=ConstantZ` | unchanged | raises `#303 Invalid inline math entry` |

So the enum text behaviour is **per property and inconsistent**: `Conn` fails loudly on a number, `Model` fails loudly on a name, and `DispMode`/`Status` **silently discard** the numeric form. A DSS script that writes `Status=1` gets a *variable* generator with no diagnostic, and `DispMode=2` leaves the dispatch at `Default`. This is the same hazard class as the Capacitor `states` finding E-1 that the owner directed to be applied, and it matters more here because the affected values gate dispatch.

**Requested correction (E-1). APPLIED at owner direction** — the `dispmode` row now records that DSS text accepts the names only and that a numeric text write is silently discarded, while an out-of-range Python attribute write is stored and makes the next read raise; the `status` row records the same silent-discard rule for `Status=1`; and `docs/workflows/generator.md` now spells out the per-interface difference, including that `Conn` and `Model` fail loudly where `DispMode` and `Status` fail silently. The specification was: In `references/generators/generator_properties.json`, extend the `dispmode` and `status` row descriptions, and add a sentence to `docs/workflows/generator.md` §"Assign shapes and interpret dispatch inputs", along these lines: *"DSS text accepts the enum names only (`Default`/`Loadlevel`/`Price`; `Fixed`/`Variable`). Numeric text values are silently discarded and leave the prior value; use the name in text and the enum member or integer in Python. The Python attribute stores an out-of-range integer unvalidated, so the next Python read raises `ValueError`."* The build audit's sentence should also name the path it probes.

- [Enum conversion in the wrapper](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Generator.py#L360-L375) · [Engine enum construction](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L449-L462) · [Matrix](../audits/phase3b_generator_readback.json) · [Catalog](../../opendss_altdss_library/references/generators/generator_properties.json)

### E-2 — the rows do not disclose the EPRI divergences the audit relies on (minor, non-blocking)

The build audit correctly states the live EPRI values: `Properties9.html` gives **Vminpu 0.95**, **Vmaxpu 1.05**, and **Xdp 0.27**, while the pinned constructor sets 0.90, 1.10 and 0.28 (`generator.pas` L980-L981, L996), and the wrapper docstring repeats 0.27 (`Generator.py` L563-L574). The catalog rows `vminpu`, `vmaxpu` and `xdp` record the **pinned** values, which is the correct precedence, but they cite no EPRI reference and carry no divergence note; the only hint is the record-level scope line *"Version-sensitive values follow the pinned engine."* A reader comparing the catalog to the EPRI page sees three unexplained contradictions.

I verified both halves myself: `Generator.html` contains none of these tokens (it is model and register vocabulary only), and `Properties9.html` contains the 0.95 / 1.05 / 0.27 statements verbatim.

**Requested correction (E-2). APPLIED at owner direction** — `vminpu` now ends "EPRI states 0.95; the pinned constructor and this readback use 0.90.", `vmaxpu` ends "EPRI states 1.05; the pinned constructor and this readback use 1.10.", and `xdp` ends "EPRI and the wrapper docstring state 0.27." No value changed. The specification was: Append one clause each, changing no value: `vminpu` → "EPRI states 0.95; the pinned constructor and this readback use 0.90."; `vmaxpu` → "EPRI states 1.05; the pinned constructor and this readback use 1.10."; `xdp` → "EPRI and the wrapper docstring state 0.27; the pinned constructor and this readback use 0.28." This is the treatment the owner directed for the equivalent Capacitor finding, applied here for consistency.

- [EPRI properties vocabulary](https://opendss.epri.com/Properties9.html) · [Engine defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L978-L1000) · [Wrapper Xdp docstring](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Generator.py#L563-L574)

### A-1 to A-5 — architect-owned handoff corrections applied (my handoff, not the package)

Five traps in `docs/handoffs/Phase_3B_Generator_Coder_handoff.md` were wrong or imprecise. In every case the package is right and the handoff is being corrected:

| # | Trap | What the handoff said | What is true |
|---|---|---|---|
| A-1 | 11 | "`DispMode=3` raises `ValueError`; use the enum or 0/1/2" | The **write** does not raise. A Python attribute write stores 3 and the **next read** raises; a text write of 3 is silently discarded (E-1) |
| A-2 | 13 | "`Like` is read-only on the object" | Read-only **as a creation keyword** only; `g.Like("src")` is a working method that copies parameters and returns `None` — the same correction I had to make for Capacitor (A-1 there) |
| A-3 | 7 | "terminal power was `(−800 − j3000)` — clamped at **`Minkvar`**" | The sign convention is into-element, so that value is the **positive `Maxkvar`** injection limit. Also, the voltages in traps 7-8 came from my own 3 MW fixture; the committed figures are 0.99473 and 1.00443 pu |
| A-4 | 4 | "`kW`/`kvar` imply PF 0.9988" | 1000 kW with 60 kvar implies **0.9982** (1000/√(1000²+60²)); the coder's value is correct |
| A-5 | 9 | "`Model` 6 raises `#570` … a construction-time error" | Two distinct paths: `#567` on **solve** with no user model, `#570` at construction for an explicitly missing DLL. Conflating them loses the guard the reader needs |

Two further trap-14 omissions were also fixed: the conductor counts skipped the two-phase case (wye 3, delta 3), and trap 12 presented the `Refuel` result in a way that read as if nothing changed.

**Process note.** This is the fourth and fifth architect-owned handoff correction in three packages, and A-2 is the *same* error I had already corrected for Capacitor one package earlier. The pattern is not random: my traps are written from a single source read, with numbers and signs reproduced from a one-off fixture and with the scope of each claim ("read-only" as keyword or as object) left implicit. Two remedies are worth adopting for the Phase 4 handoffs: probe every numeric or sign claim on the pinned stack before issuing, and state the scope inside each trap rather than leaving it to context.

- [Corrected handoff](../handoffs/Phase_3B_Generator_Coder_handoff.md) · [Model 3 clamp](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1635-L1692) · [User-model guards](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1816-L1836)

### O-1 — the shared schema gap is now closed for Load and Generator, and remains for Capacitor (carried forward)

The package did what the earlier findings asked: `enum_type`, `reference_class` and `dss_text_keyword` are now declared as optional strings in the shared row schema. I re-counted the undeclared usage across all three element catalogs:

| Catalog | Rows | Undeclared row fields |
|---|---|---|
| Load | 43 | none — closed |
| Generator | 49 | none — closed |
| Capacitor | 22 | **7 fields, 26 uses**: `array_element_type` (7), `readback_type` (7), `array_length` (7), `dss_text_write` (2), `python_write_status` (1), `python_creation_status` (1), `python_method` (1) |

The row subschema still sets `additionalProperties: true`, so anything else added later is unvalidated by default. The remaining Capacitor declarations are already the manifest's second next action; nothing here is a package-6 defect.

- [Shared schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json) · [Capacitor catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json)

### O-2 — the QA report attributes the EPRI bounds to the wrong page (no package action)

The QA/QC report says *"EPRI `Generator.html` states voltage bounds 0.95/1.05"*. They are on `Properties9.html`; `Generator.html` contains none of `Vminpu`, `Vmaxpu`, `Xdp`, `0.95`, `0.27`, or `0.28`. The build audit and the catalog cite `Properties9.html` correctly, so this is a QA-report wording slip, recorded for accuracy rather than as a finding against the package.

### O-3 — `dss_text_keyword` earned its place immediately (no action)

Adding the field to the schema looked like bookkeeping; the probe shows it is not. `Edit ... pctFuel=40` raises `#110 Unknown parameter`, while `%Fuel=40` works, so a reader who trusts the wrapper name in a DSS script gets a hard error. Recording the text name per row is the right fix and should be kept for every future element.

### O-4 — `not-run` is used honestly (no action)

Four engine records (`capi-generator-dispatch-checks`, `capi-generator-pv-factor`, `capi-generator-controller-scope`, `capi-generator-dynamic-model-scope`) and two matrix cells (`shapes.time_shape_dispatch`, `actions_and_fuel.fuel.consumption_study`, plus every entry in `dispatch_review.behavior`) are labelled `not-run` rather than dressed up. `compiled_model_execution` and `dynamics_and_shaft_execution` are likewise `not-run`. With GenDispatcher, PVSystem and Storage deferred by owner scope, this is the correct boundary.

## Limitations

- GenDispatcher, PVSystem, Storage and the other controllers remain deferred; dispatch behaviour, `PVFactor` sensitivity, and controller operation are source-reviewed only.
- Compiled user models, dynamics, harmonics, and fuel-consumption time series were not executed; the guards are proven, the models are not.
- Runtime coverage is a snapshot at a single circuit and load level. The `DispMode`/`Status` paths in E-1 were probed for storage semantics, not for their dispatch *effects*, which stay `not-run`.
- This review re-derived facts from pinned sources and re-ran the recorded tools; it did not re-validate packages 1–5 beyond confirming that their catalogs are untouched in `f0d487e..0a88ad3`.

## Disposition

**PASS WITH FINDINGS.** The catalog is complete against the engine enum, exact against the wrapper surface, correctly pinned, and honest about what was not run. The two findings are wording and disclosure fixes with no runtime dependency; E-1 is worth applying because it documents a silent-failure path that affects DSS scripts. The five handoff corrections are mine, not the package's. O-1 is now closed for Load and Generator and narrowed to Capacitor.

With independent QA/QC reporting PASS and no blocking findings, nothing technical stood between package 6 and owner acceptance. **Resolved:** the owner accepted package 6 and directed E-1 and E-2 to be applied; both are applied with no value, type, default, or citation change, schema validation re-passed 15/15 after the edit, and the Phase 3 exit gate is closed.
