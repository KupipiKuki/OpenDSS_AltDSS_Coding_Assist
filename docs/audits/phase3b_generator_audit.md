# Phase 3B Package 6 build audit

- **Date** 2026-11-21 (local validation environment)
- **Branch** `wp/phase3`
- **Status** Coder validation complete. Independent QA/QC and architect review pending.

## Scope and method

The package covers Generator. GenDispatcher, PVSystem, Storage, and other controllers remain deferred. Dynamic fields and user-model configuration are source-catalogued. Runtime coverage for those paths stops at default readbacks and missing model or reference guards. [Coder handoff](../handoffs/Phase_3B_Generator_Coder_handoff.md)

Compared the pinned 0.2.4 wrapper and 0.14.5 engine sources. Verified the lower-case `src/PCElements/generator.pas` path and used EPRI's Generator element and `Properties9.html` vocabulary pages. The live EPRI page gives voltage bounds of 0.95 and 1.05, while the pinned constructor and runtime give 0.90 and 1.10. The pinned `Xdp` readback is 0.28, while the wrapper docstring says 0.27. [EPRI element](https://opendss.epri.com/Generator.html) · [EPRI properties](https://opendss.epri.com/Properties9.html) · [Engine constructor](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L937-L1049) · [Wrapper Xdp documentation](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Generator.py#L563-L574)

Ran on Windows 11 AMD64, Python 3.14.6, AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5, and jsonschema 4.26.0. A fresh virtual environment used the matching installed distributions from the earlier validation environment through a local path entry. [Validation requirements](../../opendss_altdss_library/tools/requirements-validation.txt) · [Runtime matrix](phase3b_generator_readback.json)

## Coverage and results

| Check | Result |
|---|---|
| Catalog | 49 rows. The 47 exact advertised Python keywords include two actions. The other two rows are the object identifier and DSS-text-only MVA. The engine defines 44 own properties. |
| Shared catalogs | Appended 11 source records, 17 engine records, and two examples. Existing records were preserved. |
| Schema handling | 15 of 15 pairs passed. The shared row schema now validates optional `enum_type`, `reference_class`, and `dss_text_keyword` string fields. Catalogs from accepted packages required no edits. |
| Example harness | 14 of 14 examples passed. Both new examples have `Observed-working` records. |
| Readback matrix | All 49 rows accounted for. Probes cover power families, ratings, MVA, topology, signs and terminal powers, PV voltage limits, model and dynamic lookup guards, shapes, actions, fuel units, and registers. |
| Model coverage | Models 1, 2, 4, 5, and 7 solved snapshots near rated voltage. Four Model 3 cases checked voltage targets and limiting Q. The two Model 6 failure paths were checked. |

[Generator catalog](../../opendss_altdss_library/references/generators/generator_properties.json) · [Workflow](../workflows/generator.md) · [Examples](../../opendss_altdss_library/references/examples.json)

## Findings for QA/QC

- The bare schedule independently initializes 1000 kW, 60 kvar, PF 0.88, and a 1200 kVA rating. The scheduled P and Q imply PF 0.9982. Both power families reproduced in Python and DSS. Automatic kVA followed 1.2 times signed kW, and explicit kVA or DSS MVA kept its value after power edits. [Specification sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L510-L517) · [Alias registration](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L620-L647) · [Power synchronization](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L2880-L2897)
- The DSS Model 3 example requests 1.03 pu. With ±3000 kvar limits it achieved about 1.00443 pu and returned −3000 kvar into the terminal, corresponding to the positive `Maxkvar` injection limit. Nominal kvar still read about 431.79. At ±120 kvar, both the 1.00 and 1.03 requests reached about 0.99473 pu. The 1.00 case with wide limits reached its target within the solve tolerance. [Model 3 iterates and clamps Q](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1635-L1692)
- `DispMode`, `DispValue`, `ForceOn`, and `Status` participate in the Generator's built-in dispatch logic. `PVFactor` belongs to the Model 3 iteration. GenDispatcher is a separate controller that can edit kW and kvar. The dispatch effects and sensitivity to changing PVFactor are tagged `not-run`. Writing a numeric DispMode of 3 succeeded in the probe. The Python getter then rejected the value during enum conversion. [Dispatch checks](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1120-L1183) · [PV correction](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1658-L1675) · [Controller updates](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/GenDispatcher.pas#L302-L345)
- Model 6 alone constructed and later raised `#567` on solve. The `#570` construction error required an explicitly missing DLL. No compiled model was loaded. The DynamicEq lookup guard raised `#401`. [Library selection](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/GenUserModel.pas#L140-L174) · [Solve guard](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1816-L1836)
- The working `Like` action paths were DSS text and the Python method. The probe preserved target buses and the old four-conductor count while copying a delta source with three. Both refuel action paths restored the level to 100% without changing capacity or reserve. The two Python action creation keywords raised `AttributeError`. [Copy action](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L844-L897) · [Refuel action](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L483-L487)

The matrix verifies one daily register sample with fuel disabled and default dispatch. It covers shape assignment, without a variable-shape time series. The dedicated matrix checks DSS example convergence, achieved voltage and terminal power. The generic example harness runs the file and reports execution status. [Readback tool](../../opendss_altdss_library/tools/readback_generator.py) · [QA/QC handoff](../handoffs/Phase_3B_Generator_QAQC_handoff.md)
