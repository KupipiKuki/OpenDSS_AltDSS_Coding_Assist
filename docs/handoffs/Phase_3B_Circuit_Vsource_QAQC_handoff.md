# QA/QC Handoff for Phase 3B Package 2

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase3`
- **Baseline** `861a6e6`
- **Package revision** Coder working tree based on `861a6e6`. Pin the package commit after staging and committing this revision.

Review the Circuit and Vsource package using the boundary set by the coder handoff. Record the reviewed commit and clean or dirty working-tree state. [Coder handoff](Phase_3B_Circuit_Vsource_Coder_handoff.md) · [Build audit](../audits/phase3b_circuit_vsource_audit.md)

## Setup

Run from the repository root in a fresh environment.

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_circuit_vsource.py
```

Expect 11 schema pairs and six catalogued examples. Compare the property rows and focused probes with the committed matrix. [Runtime matrix](../audits/phase3b_circuit_vsource_readback.json)

## Checklist

- Confirm the Circuit command mapping and thin identifier row, routing to `Vsource.source`, and readback through the context, source, solution, and bus.
- Verify the 36 Vsource rows against the pinned engine and wrapper, including the 33 Python keywords, inherited fields, and the two DSS text-only entries.
- Compare the 17 added source records and 14 engine records to the baseline. Verify cited lines, case-sensitive wrapper names, evidence scope, and source ID resolution.
- Reproduce the five impedance families, ohmic base scaling, ratio edit, per-unit input persistence, and grounded terminal behavior. Confirm source frequency initialization and independent later edits.
- Check the two new examples on the pinned stack, including the dedicated DSS readback. Distinguish recorded one-source solves and unsolved standalone probes from broader fixture or multi-source validation.

## Report

Save the review as `docs/audits/phase3b_circuit_vsource_qaqc.md`. Include the verdict, reviewed branch and commit, environment, coverage and source findings, schema and runtime results, limitations, and concrete corrections. The owner dispositions findings before Package 3.
