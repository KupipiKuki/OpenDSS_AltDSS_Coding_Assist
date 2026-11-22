# Phase 3B Package 4 build audit

- **Date** 2026-11-21
- **Branch** `wp/phase3`
- **Status** Coder validation complete. Independent QA/QC and architect review pending.

## Scope and method

The package covers `Load` and assignment effects for its five shape references. LoadShape and GrowthShape property catalogs remain deferred. Shape objects used by the readback are minimal fixtures. [Coder handoff](../handoffs/Phase_3B_Load_Coder_handoff.md)

Compared the 0.2.4 wrapper and constructor API with the 0.14.5 property tables, initialization, edit finalization, and solve paths. Verified that EPRI's `Properties17.html` is the Fault property page. Used `Properties7.html` for Load property vocabulary and `Load1.html` for model concepts. The shared index already contains the pinned circuit and power-conversion inheritance sources. [EPRI Load](https://opendss.epri.com/Load1.html) · [Load property page](https://opendss.epri.com/Properties7.html) · [Fault property page](https://opendss.epri.com/Properties17.html) · [Source index](../../opendss_altdss_library/references/sources.json)

Ran on Windows 11 AMD64 with Python 3.14.6, AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5, and jsonschema 4.26.0. A fresh virtual environment loaded the installed pinned distributions from the prior validation environment through a local path entry. [Runtime matrix](phase3b_load_readback.json) · [Validation requirements](../../opendss_altdss_library/tools/requirements-validation.txt)

## Coverage and results

| Check | Result |
|---|---|
| Load catalog | 43 rows, consisting of 42 exact creation keywords and one name row. All rows have versioned source references. `Like` is recorded as an action. |
| Shared catalogs | 10 source records, 13 engine records, and two example records appended. Prior records were preserved. |
| Schema validation | 13 of 13 manifest and catalog schema pairs passed with Draft 2020-12 format checking. |
| Example harness | 10 of 10 examples passed. Both new examples have an `Observed-working` record. |
| Targeted readback | All 43 rows accounted for. Verified the five families in Python and DSS, family switching, allocation order, edit finalization, topology, shape assignment, percent fields, and ZIPV. |
| Solved examples | Both Python loads served 60 kW and about 19.721 kvar. The DSS ZIPV load served 60 kW and 15 kvar and returned four terminal currents. A six-coefficient ZIPV write raised `#20200423`. |

[Catalog](../../opendss_altdss_library/references/loads/load_properties.json) · [Workflow](../workflows/load.md) · [Runtime matrix](phase3b_load_readback.json)

## Findings for QA/QC

- Every declared family was exercised. The billing member order in `TSpecSets` places PF second. Writing only PF after switching to kW/kvar returned the power factor implied by kW and kvar in Python attributes, `edit(...)`, and DSS text. [Specification sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L368-L381) · [Recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1152-L1198)
- The order effect for capacity allocation reproduced in both input paths. PF last gave 44 kW, PF first gave 45 kW, and reapplying the allocation factor with PF set restored 45 kW. The property table's `Ordering_Last` flag does not establish the execution order of the tested DSS commands. [Allocation property effects](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L562-L618) · [Allocation math](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L2167-L2191)
- Fresh allocation examples with explicit PF read zero kVA. A billing edit on an existing kW/kvar load kept the prior reference-based kVA. The engine branch can compute kVA from reference fields separately from the allocated kW and kvar. [Allocated-family recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1189-L1198)
- Separate attribute writes on a bare `Load.new(name)` left kvar and kVA stale, in either order. Ending the edit, using kwargs on construction, or using a DSS command refreshed both. The bare `begin_edit=False` constructor also reproduced stale reads until a completed `edit(...)`. Individual writes on a load initialized with completed kwargs refreshed in the observed sequence. [Constructor edit state](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/DSSObj.py#L414-L432) · [Engine EndEdit](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L725-L737)
- Verified all five references, Daily's Yearly fill, preservation of an explicit Yearly, and `UseActual` effects for Daily, Yearly and Duty. Shape dispatch during time-series solves, voltage-limit service evaluation, and ZIPV cutoff and very-low-voltage sweeps were source reviewed. The runtime evidence is limited to the recorded assignment and snapshot cases. [Shape assignment](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L620-L643) · [ZIPV voltage branches](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1581-L1652)

The generic example harness reports process execution. The dedicated readback verifies convergence and power for the DSS ZIPV example. Independent QA/QC and architect review precede owner disposition. [QA/QC handoff](../handoffs/Phase_3B_Load_QAQC_handoff.md)
