# QA/QC Handoff for Phase 3B Package 1

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase3`
- **Baseline** `ab444fd`
- **Package revision** `2cd9b335e83f7a3d61134a8400ccd6800ddc1f57`. A later commit may update this handoff. Review the catalog and runtime artifacts at the pinned package revision.

Review LineGeometry, LineSpacing, WireData, CNData, and TSData against the Phase 3B coder handoff. Preserve the package revision and record the reviewed commit and clean or dirty state in the report. [Coder handoff](Phase_3B_LineGeometry_WireData_Coder_handoff.md) · [Build audit](../audits/phase3b_line_geometry_wires_audit.md)

## Setup

From the repository root, create and activate a fresh environment with the pinned validation requirements, then run:

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_line_geometry_wires.py
```

Expected scope is 10 schema pairs and four runnable examples. Compare the new readbacks to the checked-in matrix and record the environment. [Recorded matrix](../audits/phase3b_line_geometry_wires_readback.json)

## Checklist

- Verify all 82 rows against the five pinned wrappers and the engine. Require a usable citation on each property. Check that any absent standalone EPRI reference is clearly disclosed.
- Verify the 16 added source records and 19 engine records. Confirm that source IDs resolve, inherited conductor and cable properties are correctly attributed, and runtime claims match the matrix.
- Compare the whole property, example, engine, and source data against the baseline. The existing Line/LineCode catalog and existing API, engine, and source records should be preserved.
- Check the geometry and spacing paths in both example files. Verify phase and conductor counts, reduction, ordering, units, and typed cable readback.
- Review the two limits called out by the coder. The scalar Python `LineGeometry.Units` readback can be unavailable. A `rho` edit at the same frequency can leave the cached impedance matrix unchanged.
- Keep the review to these five elements and their use from Line. Phase 4 feeder regressions and later Phase 3B element packages are tracked separately.

## Report

Write `docs/audits/phase3b_line_geometry_wires_qaqc.md`. Include a verdict, reviewed branch and commit, coverage findings, source and runtime findings, schema and execution results, limitations, and explicit corrections with file and source coordinates. The owner decides which findings block the next package.
