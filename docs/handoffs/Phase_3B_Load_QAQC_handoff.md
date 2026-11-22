# QA/QC handoff for Phase 3B package 4

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase3`
- **Baseline** `b896db8a298ad9fe1963d692c6a53649cf9b7ed0`
- **Package revision** `37854f664369e61c9c2a7f22ee05a7295152685c`. Review the package artifacts at this commit. The follow-up commit supplies the handoff pin.

Review Load against the coder handoff at the pinned commit. Record the revision and working-tree state. [Coder handoff](Phase_3B_Load_Coder_handoff.md) · [Build audit](../audits/phase3b_load_audit.md)

## Setup

Run from the repository root in a fresh environment.

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_load.py
```

Expect 13 schema pairs and ten examples to pass. Compare the readbacks against the committed matrix. [Runtime matrix](../audits/phase3b_load_readback.json)

## Checklist

- Verify 43 property rows, 42 case-sensitive Python keywords, one identifier, all source ranges, inherited fields, enum member types and object references.
- Compare the 10 source, 13 engine, and two example additions against the baseline. Check example source IDs, the corrected EPRI property page, and scope notes for LoadShape and GrowthShape.
- Verify the five engine specification sets and the billing set's declaration order. Reproduce family switching, the PF-only edit under kW/kvar, and the 44 versus 45 kW connected capacity result for both input paths.
- Reproduce the bare-load attribute readbacks and edit finalization, including the completed-kwargs comparison. Verify fresh billing-family zero kVA and the reference-based kVA from an existing kW/kvar load.
- Verify topology and shape assignment, including Daily's Yearly fill and `UseActual` with specified PF or kvar. Confirm the percent scaling, voltage-limit defaults, and Spectrum reference.
- Re-run both examples. Use the dedicated readback for DSS convergence, served power, terminal currents, and ZIPV array length validation.

## Report

Save the report as `docs/audits/phase3b_load_qaqc.md`. Include verdict, branch and commit, working-tree state, environment, source and property findings, schema and runtime results, coverage limits, and any required corrections. The owner dispositions the package before Phase 3B Package 5 begins.
