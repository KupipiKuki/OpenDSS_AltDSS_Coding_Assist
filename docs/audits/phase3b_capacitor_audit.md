# Phase 3B Package 5 build audit

- **Date** 2026-11-21
- **Branch** `wp/phase3`
- **Status** Coder validation complete. Independent QA/QC and architect review pending.

## Scope and method

The package covers Capacitor and the bank-side step switching that CapControl uses. CapControl property coverage and controller operation are deferred. Compared the pinned wrapper, engine property table, edit side effects and admittance implementation. Verified the EPRI element page at `Capacitor1.html` and the vocabulary page at `Properties12.html`. The separately titled `Capacitor.html` documents the CapControl reference to a capacitor. EPRI's stated default kvar differs from the pinned engine's 1200 kvar constructor. [EPRI element](https://opendss.epri.com/Capacitor1.html) · [EPRI properties](https://opendss.epri.com/Properties12.html) · [CapControl reference](https://opendss.epri.com/Capacitor.html) · [Coder handoff](../handoffs/Phase_3B_Capacitor_Coder_handoff.md)

Ran on Windows 11 AMD64 with Python 3.14.6, AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5, and jsonschema 4.26.0. A fresh virtual environment used a local path entry to matching installed distributions from the previous validation environment. [Validation requirements](../../opendss_altdss_library/tools/requirements-validation.txt) · [Runtime matrix](phase3b_capacitor_readback.json)

## Coverage and results

| Check | Result |
|---|---|
| Property surfaces | 22 rows, including 21 exact advertised Python keywords, one identifier, and an action entry for `Like`. The class registers 13 own properties. Each row has a versioned source citation. The matrix checks NumPy array dtypes and shapes. |
| Shared catalogs | Appended 11 source records, 14 engine records, and two examples. Prior records were preserved. |
| Schema and examples | 14 of 14 schema pairs and 12 of 12 catalogued examples passed. Both new examples are recorded as `Observed-working`. |
| Focused readbacks | Defaults, three family paths, one-to-many step resize, array validation, filter property edits, wye and delta topology, series wiring, state writes and switching, rating overrides, JSON omission, copy behavior, and legacy names. |
| Solves | Grounded wye and delta shunts, wye series with a Load fixture, wye Cuf and CMatrix paths, and equal and unequal step comparisons. The dedicated readback asserts convergence and terminal output for the DSS example. |

[Catalog](../../opendss_altdss_library/references/capacitors/capacitor_properties.json) · [Workflow](../workflows/capacitor.md) · [Evidence](phase3b_capacitor_readback.json)

## Findings for QA/QC

- `CMatrix` accepted the six-value lower triangle and nine-value full array for three phases. Eight values raised `#2020036`. The switched family left `kvar` and `Cuf` readbacks intact and automatic ratings at zero. [Matrix registration and scale](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L219-L224) · [Rating calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L666-L692)
- With `kvar=[100,200]`, derived Cuf values were equal because `RecalcElementData` references the first kvar entry for each step. Switching each step on alone supplied about 100.01 kvar. With `Cuf=[7,14]` the solves supplied about 410.52 and 821.37 kvar. [kvar branch](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L625-L645) · [Per-step admittance](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L924-L960)
- After changing a 600 kvar bank to `Cuf=[10]`, the stored kvar stayed at 600, the normal and emergency ratings read about 0.0000122 and 0.0000163 A, and the solve supplied about 586.56 kvar. The solved Q matches the capacitance calculated against measured terminal voltages. The amp discrepancy follows the scale in the Cuf rating accumulator. [Cuf accumulator](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L646-L665)
- `States` writes through Python creation kwargs, assignment, and `edit` kept the old states in the probes. DSS text changed the states and power. The shorthand `State=[0 0 1 1]` was accepted as an abbreviation using array semantics. Ten other probed legacy names raised `#110`. [Wrapper States](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Capacitor.py#L263-L274) · [Engine States](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L472-L498)
- `Like` works through DSS text and the Python action method. The Python creation keyword raised `AttributeError`. Both successful copies retained the target bus and two-terminal allocation while copying the source's delta setting. The copy and topology-transition probes only read back the resulting objects. [Copy routine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L503-L544)
- In the kvar family the pinned engine derived normal and emergency ratings at 135% and 180% of phase current. The wrapper docstring's normal factor is 180%. The probe verified independent stickiness when specifying one or both ratings. [Wrapper normal rating](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Capacitor.py#L276-L286) · [Engine rating factors](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Capacitor.pas#L684-L692)

CapControl runtime, harmonic-analysis solves, reliability studies, and feeder fixtures are outside this package. The matrix verifies the Capacitor bank's state hook with manual DSS edits. Independent QA/QC and architect review precede owner disposition. [QA/QC handoff](../handoffs/Phase_3B_Capacitor_QAQC_handoff.md)
