# QA/QC handoff for Phase 3B package 6

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase3`
- **Baseline** `f0d487ec9e93fce200e6f30f431ffe0ff77217c8`
- **Package revision** Pending the package commit.

Review the Generator artifacts at the pinned commit. Record the revision and working-tree state. [Coder handoff](Phase_3B_Generator_Coder_handoff.md) · [Build audit](../audits/phase3b_generator_audit.md)

## Setup

Run from the repository root in a fresh environment.

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
python -m pip install -r opendss_altdss_library/tools/requirements-validation.txt
python opendss_altdss_library/tools/validate_catalogs.py
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_generator.py
```

Expect 15 schema pairs and 14 examples to pass. Compare the runtime matrix for solved values and error paths. [Runtime matrix](../audits/phase3b_generator_readback.json)

## Checklist

- Verify 49 property rows, 47 exact advertised Python keywords, the object name, and DSS-only `MVA`. Check the lower-case engine path, enum spellings, inherited citations, shape references, and the three declared optional schema fields.
- Compare the 11 source, 17 engine, and two example additions with the baseline. Verify source IDs, EPRI page scope, and preservation of prior records.
- Reproduce both power families, the independent machine rating, the MVA scale, automatic versus explicit rating, and negative-kW consumption.
- Verify topology and input errors, solved sign, scheduled versus terminal values, and the Model 3 limit and achieved voltage in each case. The high-target saturation is at `Maxkvar` in generator injection units.
- Verify Model 6 guard timing, the missing dynamic reference, shape assignment, fuel action and units, register values, and `Like` behavior across both action paths.
- Review the source-only Generator dispatch, Model 3 `PVFactor`, and GenDispatcher descriptions. Keep controller operation, compiled libraries, and dynamic or fuel-consumption studies outside the validation run.

## Report

Save the verdict, branch and revision, working-tree state, environment, source findings, schema and runtime results, limits, and required corrections in `docs/audits/phase3b_generator_qaqc.md`. Package 6 completes the six-package implementation sequence. Independent QA/QC and architect review precede owner disposition and Phase 4 planning.
