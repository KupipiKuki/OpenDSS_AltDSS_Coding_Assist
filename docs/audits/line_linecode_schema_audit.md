# Line and LineCode Catalog Audit

**Review date:** 2026-11-20
**Artifact:** Line/LineCode catalog, first Phase 2 remediation pass from Phase 1 baseline `3263daa`. [Catalog](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties.json)
**Target:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5

## Status

Mistral reported **pass with findings** on 2026-11-21 UTC. Its independent schema check and focused runtime checks passed. The coder checked the two requested corrections against the primary sources and applied them below. [Independent QA/QC report](line_linecode_phase2_qaqc.md)

## Phase 2 source findings

- The exported context initializes `altdss.Line` and `altdss.LineCode` as collections. The catalog now gives exact creation keywords from both wrappers, including Python `Conductors` for DSS `wires`. [Context export](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/__init__.py#L23-L30) · [Collections](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Obj.py#L170-L184) · [Line keywords](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Line.py#L723-L759) · [LineCode keywords](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/LineCode.py#L488-L516)
- Both engine constructors initialize C1 and C0 as farad values. The property scale converts them to 3.4 and 1.6 nF per 1,000 ft for the default sequence data. Use the engine scale to interpret the discrepancy in the online EPRI Line page. [Line defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L940-L950) · [Line scale](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L253-L259) · [LineCode defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L462-L469) · [LineCode scale](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L300-L306)
- The catalog now records the full explicit impedance specification sets for both elements. The constructors also initialize default sequence data. The catalog describes `bus1` and `bus2` as required Line model inputs and documents the object name separately from the Python keywords. [Line sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L302-L320) · [Line bus properties](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L403-L410) · [LineCode sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L215-L226)
- The pinned `Switch` setter changes sequence values, length, and prior impedance specifications. The catalog records those side effects and the constructors' initial ratings. It also describes the circuit-dependent LineCode base frequency and removes the fixed `LineCode.Repair` default because the constructor does not explicitly initialize that field. [Switch behavior](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L672-L699) · [Line ratings](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L1003-L1005) · [LineCode constructor](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L456-L504)

## Independent QA/QC disposition

- **E-1 resolved.** The `Line.Switch` catalog entry now says that setting `Switch=True` marks the symmetrical-component definition as changed. The setter's other documented effects are unchanged. [Pinned setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Line.pas#L672-L699)
- **E-2 resolved.** The `LineCode.BaseFreq` entry now cites the EPRI page's 60.0 Hz default and explains that the pinned engine initializes from the active circuit's fundamental frequency. The catalog keeps the fixed default unspecified. [EPRI LineCode reference](https://opendss.epri.com/LineCode1.html) · [Pinned constructor](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/General/LineCode.pas#L483-L487)
- **E-3 deferred.** The optional expansion of property-level citations can be handled as records are curated. Existing element-level citations provide the fallback.

QA/QC observed an initial `LineCode.Repair` readback of `0.0` in its pinned environment. The catalog leaves the default unspecified because the constructor does not explicitly assign it. The `epsrmedium` row retains its unsupported marker for the pinned target. Broader fixture and edit coverage remain pending. [Runtime evidence](line_linecode_phase2_qaqc.md#runtime-result-pass) · [Archived audit](line_linecode_schema_audit_legacy.md)
