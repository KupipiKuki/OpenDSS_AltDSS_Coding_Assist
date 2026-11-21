# QA/QC Handoff: Phase 3A API and Engine Catalogs

## Review target

Review the Phase 3A working revision on `wp/phase3` against the Phase 2 merge commit `8053b67` (or `1d4088f` if the docs commit is out of scope). Read [the build audit](../audits/phase3a_api_catalogs_audit.md), then inspect the generated catalog, the engine records, and the generator against the pinned sources. Record the reviewed branch and commit or working-tree state in your report.

Artifacts: [altdss_python_api.json](../../opendss_altdss_library/references/altdss_python_api.json) · [dss_capi.json](../../opendss_altdss_library/references/dss_capi.json) · [sources.json](../../opendss_altdss_library/references/sources.json) · [generator](../../opendss_altdss_library/tools/build_altdss_api_catalog.py) · [schemas](../../opendss_altdss_library/schemas/catalogs/)

## Audit checklist

- Re-run `tools/build_altdss_api_catalog.py` on the extracted `altdss==0.2.4` wheel and confirm a byte-identical result.
- Confirm the catalog covers the expected classes: object classes, `I<Element>` collection interfaces with `new`/`batch_new`, and the `AltDSS` context. Flag missing or spurious records.
- Sample at least ten classes against the tagged source: class name, module path, method signatures, property names, and type hints. Check casing exactly (`pctPerm` vs `PctPerm`, `rho`, `Conductors`).
- Confirm descriptions are docstring-derived and do not assert behavior the source does not state.
- Verify engine records against DSS C-API `0.14.5`: property enums, specification sets, C1/C0 and Z scaling, `Wires`/`Conductors` aliasing, `Switch` side effects, defaults, ratings, `BaseFreq`, `RequiresCircuit`, `Neutral`/Kron, `Repair`, and the `epsrmedium` absence. Check each file and line citation.
- Confirm every `tested` entry matches an execution that actually happened; `not-run` must not be presented as verified.
- Confirm the source index has no duplicate ids, no dangling `source_ids` from `examples.json`, and that the removed Line/LineCode index leaves no broken links.
- Run `python opendss_altdss_library/tools/validate_catalogs.py` and report the result separately from source review.
- Confirm the documentation (plan, manifest, READMEs, skill) describes the catalogs at their real validation level.

## Report format

Save the report as `docs/audits/phase3a_api_catalogs_qaqc.md`.

- **STATUS:** PASS / PASS WITH FINDINGS / FAIL
- **COVERAGE FINDINGS:** missing, spurious, duplicated, or mislabelled records or classes
- **SOURCE FINDINGS:** citation, version, signature, type, or description problems
- **EVIDENCE FINDINGS:** `tested` status or evidence-label problems
- **SCHEMA RESULT:** pass / fail / not run
- **RUNTIME RESULT:** pass / fail / not run, with environment if run
- **REQUIRED CORRECTIONS:** exact record or field, source URL and tag, requested change

Do not treat schema validity as runtime validation, and do not accept generated output as correct without sampling it against the tagged source.
