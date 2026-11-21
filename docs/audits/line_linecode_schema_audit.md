# Line and LineCode Catalog Audit

**Review date:** 2026-11-20
**Artifact:** `opendss_altdss_library/references/lines/opendss_line_linecode_properties.json` (Phase 1 starter catalog)
**Target:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API backend 0.14.5

## Status

**Source review: partial; schema validation: passed; runtime validation: not performed.** This reviews the restored branch after incorporating the prior Rev 2 findings. The catalog remains a Phase 1 starter artifact; remediation is planned in Phase 2. Schema validity does not certify the source claims or runtime compatibility.

## Findings carried forward and addressed

- `LineCode.x0` is present.
- `Line.required_properties` contains only unconditional creation fields; length and impedance alternatives are represented in `property_requirements.conditional`.
- Evidence is version-scoped instead of labeled `Official-current`.
- `Line.epsrmedium` is retained for traceability and marked `supported_in_target: false`.
- The catalog records package/backend versions, source URLs, access date, and source scope.
- The catalog validates against `schemas/catalogs/line_linecode_properties.schema.json` with PowerShell `Test-Json` (2026-11-20).

## Source observations

The EPRI [Line reference](https://opendss.epri.com/Line.html) describes the default 1000-ft overhead line, its sequence values, and impedance sources. The EPRI [LineCode reference](https://opendss.epri.com/LineCode1.html) lists LineCode properties and behavior. Neither page identifies an OpenDSS release, so these are version-qualified references rather than a claim about every OpenDSS release.

The external audit report records broader documentation/release discrepancies. Exact property-level API support and engine defaults still need comparison against the release-tagged sources. In particular, verify the `epsrmedium` exclusion against the pinned target API/backend source.

## Remaining work

1. Correct both collection mappings in Phase 2. The starter records lower-case mappings, but the 0.2.4 source initializes `altdss.Line` and `altdss.LineCode` as collection instances on the exported `altdss` context. Use these source-confirmed names when reviewing the catalog and examples. [Context export](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/__init__.py#L23-L30) · [Collection initialization](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Obj.py#L170-L184)
2. Compare each property name, type, default, and target API support against EPRI pages and release-tagged AltDSS-Python 0.2.4 / DSS C-API 0.14.5 sources.
3. Resolve ambiguous default units and statements whose EPRI units appear inconsistent, including C1/C0.
4. Complete source corrections in Phase 2 and revalidate the revised catalog against its schema.
5. Runtime-test representative creation and inspection examples in the validation phase and record the environment and result.

The archived audit at `line_linecode_schema_audit_legacy.md` preserves previous findings and prompts. It is historical input, not the status of the current artifact.
