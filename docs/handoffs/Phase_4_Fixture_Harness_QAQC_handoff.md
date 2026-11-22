# Phase 4.1 QA/QC handoff

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase4`
- **Inputs revision** `9736d46a3b30b7c3f7c10322bd3886f61fe78991`
- **Package revision** `d1acffc6d064418bf9f232ff2e779860ed395c2e`. Review the package artifacts at this commit. The follow-up commit supplies the handoff pin.

Review the fixture harness and revision 1 snapshot results at the pinned package commit. Record the revision and working-tree state. [Coder handoff](Phase_4_Fixture_Harness_Coder_handoff.md) · [Build audit](../audits/phase4_fixture_harness_audit.md)

## Run verification

From the repository root in a fresh environment installed from `tools/requirements-validation.txt`:

```powershell
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
python -B opendss_altdss_library/tools/run_fixtures.py --fixture ieee13 --report qa-ieee13-diff.json
```

Expect 16 schema pairs, 14 prior examples, and two snapshot golden comparisons to pass. Run the absolute fixture tool path from another directory and confirm the redirects resolve.

## Checklist

- Check the nine upstream blobs with `git cat-file -p` and SHA-256. Verify the committed hashes, case, redirect stubs, license notice, and both provenance files against the fixture catalog.
- Confirm the catalog schema and source IDs. Check compatible solver, engine, and environment metadata in the revision 1 goldens. Confirm the prior catalogs and inputs are preserved.
- Reproduce the bus counts, source and load powers, iteration counts, regulator taps, capacitor states, and lowest per-unit bus voltages. Check kW/kvar units and exact bus node order.
- Use a disposable Git tree for negative checks. Alter one golden quantity and verify the nonzero return code and report path. Check rejection of checksum failure, missing approval or reason, and dirty fixture files.
- In two clean disposable trees, generate from the same initial approval and compare the golden bytes. Use a disposable next-revision approval to verify that a targeted update advances only the selected fixture.

## Report

Record the verdict, reviewed revision, environment, checksum proof, both solve results, and any required corrections in `docs/audits/phase4_fixture_harness_qaqc.md`. The 4.1 package covers AltDSS snapshot validation. [Phase 4 sequence](../phase_4/README.md)
