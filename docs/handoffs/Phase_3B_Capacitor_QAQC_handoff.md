# QA/QC handoff for Phase 3B package 5

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase3`
- **Baseline** `6663beaa2578748bd39749f42905341733bdfe5c`
- **Package revision** `d7fc55c5de6ae6533af69aa17ce16bdf22e90026`. Review the package artifacts at this commit. The follow-up commit supplies the handoff pin.

Review the Capacitor package on the pinned commit. Record the revision and working-tree state. [Coder handoff](Phase_3B_Capacitor_Coder_handoff.md) · [Build audit](../audits/phase3b_capacitor_audit.md)

## Setup

Run from the repository root in a fresh environment.

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_capacitor.py
```

Expect 14 schema pairs and 12 examples to pass. Compare the constructor readbacks, errors, and solved powers against the saved matrix. [Runtime matrix](../audits/phase3b_capacitor_readback.json)

## Checklist

- Verify 22 rows, 21 advertised Python keywords, one identifier, and the array types, sizes and cited sources. Verify the separate `Like` action and the working `States` write path.
- Compare 11 source, 14 engine, and two example additions against the baseline. Check example source IDs, CapControl deferral, and the distinction between EPRI's two pages titled Capacitor.
- Reproduce the three specification families and inactive readbacks. Verify the eight-value CMatrix rejection, Cuf rating discrepancy against solved reactive power, and equal electrical output across the two unequal kvar entries.
- Reproduce step ordering and validation, resize behavior, `NumSteps` JSON omission, the `States` write divergence and electrical effect, and the DSS `State` abbreviation.
- Verify series and shunt topology, the Bus2 change under delta and back, explicit amp-rating stickiness, and copy behavior. Check solved complex power per terminal, including one terminal for delta.

## Report

Save the report as `docs/audits/phase3b_capacitor_qaqc.md`. Include the verdict, branch and revision, working-tree state, environment, source and property findings, schema and runtime results, validation limits, and required corrections. The owner dispositions findings before Phase 3B Package 6 begins.
