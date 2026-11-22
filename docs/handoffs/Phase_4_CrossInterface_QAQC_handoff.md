# Phase 4.4 cross-interface QA/QC handoff

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase4`
- **Inputs revision** `5e323265cda7447f8e933231014b5ffe1ce4db3c`
- **Package revision** `159fce02c6a1753ea84933441f2f74f6e8f4dc88`. Review the package artifacts at this commit. The follow-up commit supplies the handoff pin.

Review the snapshot comparison, accessor catalog, example, and recorded report. Each interface uses DSS C-API 0.14.5. The comparison verifies agreement among the wrappers on that engine. [Coder handoff](Phase_4_CrossInterface_Coder_handoff.md) · [Build audit and commands](../audits/phase4_cross_interface_audit.md) · [Comparison report](../audits/phase4_cross_interface_report.json)

## Verify

- Install from the validation requirements in a fresh environment. Reproduce both snapshot comparisons, all 18 schema checks, all 19 examples, and the three separate fixture-to-golden checks. Confirm the report records six worker results and three pairwise comparisons per fixture.
- Check each pinned version string and the OpenDSSDirect.py dependency on DSS-Python 0.15.7. Review the worker subprocess and input-directory boundaries.
- Match the catalog against the tool's exact accessor spellings. Reproduce the IEEE 13 9/6/9 tap queries and the active tap behavior in a disposable context. Check element loss and circuit loss conversion from W/var to kW/kvar.
- Verify name-order independence and the discrete and numeric tolerances. Inject a single voltage discrepancy into an isolated worker readback and check the nonzero CLI exit and the fully qualified diff paths.
- Hash the IEEE 13 and IEEE 34 snapshots and the IEEE 13 daily golden against the inputs revision. Confirm the earlier catalogs, fixture inputs and schemas retain their baseline contents.

Record the verdict, reviewed commit, environment, pairwise results, hash proof, and any required corrections in `docs/audits/phase4_cross_interface_qaqc.md`.
