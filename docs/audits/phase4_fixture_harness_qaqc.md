# Phase 4.1 Fixture Harness and Snapshot Goldens — Independent QA/QC Report

**Reviewed branch:** `wp/phase4` (synced with `origin/wp/phase4`, tip `a55108c` = handoff pin only). **Package revision under review:** `d1acffc6d064418bf9f232ff2e779860ed395c2e`; **inputs revision:** `9736d46a3b30b7c3f7c10322bd3886f61fe78991`. **Phase 4 baseline:** `f8fac0c`. **Reviewed state:** `git status --porcelain` clean.
**Review date:** 2026-11-22. **Reviewer environment:** existing validation venv, Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine reports `DSS C-API Library version 0.14.5 revision 87d85c2622c8281b92255335bc7c09b11191b21d`, matching the pinned tag), `jsonschema 4.26.0`; upstream fixture files re-downloaded live from raw.githubusercontent.com at the pinned commit.

**STATUS:** PASS (no blocking findings; no required corrections)

## Run verification (fresh runs on the pinned stack, `python -B` from the repo root)

- `tools/validate_catalogs.py` → exit 0, **16/16 schema pairs**, including the new `references/fixtures.json` (2 records) against `schemas/catalogs/fixtures.schema.json`; `sources.json` now 100 records, `dss_capi.json` 119 — Phase 3 catalogs unchanged.
- `tools/run_examples.py` → exit 0, **14/14** prior examples, RESULT: PASS.
- `tools/run_fixtures.py` → exit 0, **both fixtures PASS**:

| Fixture | Buses | Elements | Converged | Total iter | Control iter | Lowest pu bus |
|---|---:|---:|---|---:|---:|---|
| ieee13 | 16 | 38 | yes | 2 | 1 | `611`, 0.960843 |
| ieee34 | 37 | 117 | yes | 25 | 6 | `890`, 0.923099 |

- `tools/run_fixtures.py --fixture ieee13 --report qa-ieee13-diff.json` → exit 0, report `status: pass`, **zero diffs**.
- Absolute tool path invoked from an unrelated working directory (path containing spaces): both fixtures PASS, exit 0 — the relative `redirect ../IEEELineCodes.DSS` stubs resolve from the script location, not the CWD.

## Checksum proof (three-way, per file)

For every catalogued file, the bytes were compared across **the git blob at the pinned package commit** (`git cat-file -p d1acffc:<path>`), **the working tree**, and **the live upstream file** at `dss-extensions/electricdss-tst@3b208397160213cae4a9e2d0a7d1aa3528ce26e1` (raw.githubusercontent.com, fetched during this review). All nine committed paths (License.txt + 8 fixture files; 7 unique fixture-relative paths because the shared `IEEELineCodes.DSS` appears in both trees) are byte-identical across all three and match the catalog's `bytes`/`sha256` exactly:

| Path | Bytes | SHA-256 (verified blob = worktree = upstream) |
|---|---:|---|
| `License.txt` | 1816 | `f1354327…c21ef` |
| `*/IEEETestCases/IEEELineCodes.DSS` (×2) | 12032 | `71bc16ef…f58b3` |
| `ieee13/…/13Bus/IEEE13Nodeckt.dss` | 8354 | `033ccd40…d4a504` |
| `*/…/13Bus|34Bus/IEEELineCodes.DSS` stubs (×2) | 30 | `40ef533d…daeb` |
| `ieee13/…/13Bus/IEEE13Node_BusXY.csv` | 243 | `f8dd1528…7846e` |
| `ieee34/…/34Bus/ieee34Mod1.dss` | 14341 | `648f12f7…058f8` |
| `ieee34/…/34Bus/IEEE34_BusXY.csv` | 506 | `6e022bbb…7958` |

The upstream commit exists and is dated 2024-06-24 (GitHub API), and the tree page at the pinned commit returns 200. `examples/fixtures/.gitattributes` contains `* -text` and `git check-attr text` reports `unset` for a fixture file, so CRLF bytes are stored verbatim in the blobs (trap 1 closed). The stub content is exactly `redirect ../IEEELineCodes.DSS` (30 B). The four deliberately omitted upstream files (`Run_IEEE34Mod1.dss`, `Run_IEEE34Mod2.dss`, `ieee34Mod2.dss`, `nmsu_linecode2_ABC.txt`) all exist upstream (HTTP 200) and are recorded with reasons in both `PROVENANCE.md` files, which also name the repository, commit, retrieval date, BSD-3-Clause licence, and both copyright holders (DSS-Extensions contributors; EPRI). Source checks in the files themselves: `IEEE13Nodeckt.dss` has `redirect IEEELineCodes.DSS` (L47), `calcv`/`Solve` (L148-149), `BusCoords` (L150); `ieee34Mod1.dss` ends at `CalcVoltageBases` with no `Solve` line — both as the handoff traps state.

## Catalog, schema, and preservation

- `fixtures.json` records carry all design §8 fields; both `source_ids` lists resolve against `sources.json` (`electricdss-tst-ieee-fixtures-3b20839` added purely additively — zero removed lines; `capi-release-0145`, `dss-python-release-0157` pre-existing). `golden_updates` holds the single approved revision 1 with the exact reason later written into the goldens; `golden_revision` = 1 matches the golden files.
- Golden metadata verified: `environment` records all four version pins + Python 3.14.6 + platform; `solver` records SnapShot / 15 max iterations / 0.0001 tolerance / Static / 10 max control iterations / 60 Hz — matching the catalog `solver` block and the design; `source` carries the upstream repo/commit/retrieved/license/files. The harness additionally refuses to run unless installed versions equal both the fixture pins and `manifest.json` `support_targets` (verified in code and exercised by the passing runs).
- Baseline preservation: `git diff f8fac0c..d1acffc` touches **only** `docs/`, `examples/fixtures/`, `references/` (fixtures.json new, sources.json +1 record), `schemas/catalogs/fixtures.schema.json` new, `tools/run_fixtures.py` new, `tools/validate_catalogs.py` +1 line. No Phase 3 catalog, example, or manifest file changed; all 23 changed paths are inside the allowed prefixes (requirement 8).

## Golden content and independent solve

Committed goldens hash to `f72d59d8…` (ieee13) and `b06282a6…` (ieee34), matching the build audit. Class counts from the golden element keys match design §4 exactly — ieee13: 12 Line, 5 Transformer, 15 Load, 2 Capacitor, 3 RegControl, 1 Vsource (38); ieee34: 32/8/68/2/6/1 (117). Regulator taps recorded: ieee13 `reg1=9, reg2=6, reg3=9`; ieee34 `creg1a=14, creg1b=4, creg1c=5, creg2a/b/c=13`; two capacitor state arrays each, all `[1]`. Powers are kW/kvar per terminal with into-element sign convention (source totals negative); losses converted W→kW; bus entries carry the engine node order with matching array lengths (no malformed bus arrays).

Independent re-solve with fresh AltDSS contexts and no harness code: ieee34 matched the golden with **max |delta| = 0.0** across all 37 buses, identical totals/taps/states (25 total / 6 control iterations). For ieee13, a naive option rewrite re-assigning the already-active SnapShot mode reproduced the audit's noted 4-iteration variant; setting options only where they differ (as the harness's `configure_snapshot` does) gave **2 total / 1 control iteration and max |delta| = 0.0** vs the golden, load 3454.659287 kW / 2094.531954 kvar — the golden is the correctly preserved repeat-solve result, not an artifact.

## Negative and governance checks (disposable clones at the pinned commit; committed goldens untouched — SHA-256 verified before/after)

| Check | Result |
|---|---|
| Perturb one golden quantity (bus 611 pu_vmag[0] +0.01) | exit 1; report shows exactly one `value` diff at `["buses","611","pu_vmag",0]` |
| Remove bus `650` from golden | exit 1; `extra` diff at `["buses","650"]` |
| Zero one declared checksum | exit 1; `Checksum mismatch …` raised before any compilation |
| `--update-golden` without `--reason` | exit 2 (argparse) |
| `--update-golden --reason` with no matching approval | exit 1; `Record owner approval for revision 2 with the exact --reason before updating`; goldens unchanged |
| Untracked file inside the fixture tree + `--update-golden` | exit 1; `Golden update requires committed, clean fixture files`; nothing written |

## Determinism and targeted update (two clean disposable trees)

Both trees were reset to the recorded initial approval (revision 0, goldens removed, committed), then run via absolute tool path from a different directory containing spaces: both `--update-golden --reason "Initial snapshot goldens for Phase 4 package 4.1"` runs exited 0 and produced goldens **byte-identical to each other and to the committed package goldens** (`f72d59d8…`, `b06282a6…`). A disposable revision-2 approval for ieee13 only, followed by `--update-golden --fixture ieee13 --reason "Targeted ieee13 revision 2 probe"`, advanced ieee13 to revision 2 (golden changed only in `golden_revision`/`update_reason`) while ieee34 stayed at revision 1 with a byte-identical golden; a full compare afterwards passed both fixtures.

## Limitations (as documented, confirmed)

- Snapshot scenario only; packages 4.2 (RegControl catalog), 4.3 (daily time series), 4.4 (cross-interface, API-layer only since all wrappers share DSS C-API 0.14.5), and 4.5 (exit/manifest/troubleshooting) remain open by design.
- The only LoadShape present is the engine built-in `default`; no LoadShape coverage is claimed — confirmed in both fixture notes.
- The 4-iteration ieee13 variant when Mode is redundantly rewritten is a documented probe artifact, not a golden defect.

## Required corrections

None.

No files were modified by this review; this report is the only file added.
