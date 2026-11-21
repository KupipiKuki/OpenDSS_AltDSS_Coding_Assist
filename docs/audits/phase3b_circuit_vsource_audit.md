# Phase 3B Circuit and Vsource Build Audit

- **Date** 2026-11-21
- **Status** Coder verification passed. Independent QA/QC pending.
- **Targets** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5.

[Property catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [Workflow](../workflows/circuit_vsource.md) · [QA/QC handoff](../handoffs/Phase_3B_Circuit_Vsource_QAQC_handoff.md)

## Method and coverage

The catalog follows the pinned wrapper and engine, with EPRI used for the model and classic interface descriptions. Circuit has one identifier row and notes for the context command path. Vsource has 36 rows covering 33 Python creation keywords, two DSS-only impedance properties, and the object identifier. Every row has a source reference. The engine enum has 31 fields after INVALID, through `puZIdeal`. The inherited fields and the two missing Python members account for the difference from the wrapper count. [Tagged enum](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L57-L94) · [Tagged wrapper](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Vsource.py#L694-L727)

The shared source index gained 17 records and now has 51. The engine catalog gained 14 records and now has 59. The package reused the generalized element schema and preserved the previously published catalog records. [Source index](../../opendss_altdss_library/references/sources.json) · [Engine catalog](../../opendss_altdss_library/references/dss_capi.json)

## Checks performed

- All **11 schema pairs** passed. All **six examples** passed through the repository harness. The dedicated readback script checked convergence and the source values of the new DSS example separately from the generic DSS harness output.
- The matrix covers **37 rows**. It has 34 Python/context readbacks, two DSS text query readbacks, and the `Like` action with no getter. The isolated validation environment reused the local audited package set and matched the pinned metadata on Windows 11 AMD64 with Python 3.14.6 and jsonschema 4.26.0.
- The routed circuit exposed one `Vsource.source` with the requested voltage, phase count, buses, magnitude multiplier, and angle. The default second terminal followed Bus1 until explicitly overridden. The solved bus read back nodes 1, 2, and 3. The installed Python package had no Circuit module or context member.
- The 115 kV default MVA source read back derived ohms after initialization. Changing its base to 12.47 kV changed the calculated ohms and retained the per-unit value within numerical tolerance. The explicit per-unit probe also checked a BaseMVA edit and scaling.
- The matrix probes MVA, current, scalar ohms, complex ohms, and per-unit input. It records the 10:1 X/R edit, the absent Python `Z1` and `Z0` attributes, and the corresponding DSS text write and query.
- At circuit creation, `DefaultBaseFrequency=50` initialized solution frequency, source frequency, and the element base frequency to 50 Hz. Later edits independently changed the solution to 55 Hz and the element base to 48 Hz while the source frequency remained 50 Hz.

[Recorded matrix](phase3b_circuit_vsource_readback.json) · [Readback tool](../../opendss_altdss_library/tools/readback_circuit_vsource.py)

## Limits for QA/QC

- The specification probe observed that explicit `puZ1` can override later scalar ohmic edits in the impedance branch and that `puZ1` readback can retain its stored value after returning to the MVA branch. The workflow recommends separate source definitions for comparisons across families. [Conversion and display paths](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L761-L875)
- The two runnable examples solve the circuit with its built-in source only. The matrix allocates standalone sources for unsolved default and scaling probes. Multi-source solves, harmonic behavior, shape-driven solves, and Phase 4 feeder fixtures remain outside the executed scope.
- The model enum and `puZIdeal` defaults were read back. The ideal branch and nondefault shape behavior are source observations.
