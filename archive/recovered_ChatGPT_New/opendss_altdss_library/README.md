# OpenDSS / AltDSS Reference Library

**Package status:** Phase 1 scaffold; schemas are initial drafts.  
**Support target:** Not selected.  
**Runtime validation:** None.

## Phase placement

Phase 1 establishes this package structure, its record schemas, source inventory, and review documents. Phase 2 populates the references with version-pinned catalog data. In particular, `references/opendss_line_linecode_properties.json` is a planned Phase 2 catalog artifact; it does not belong to the Phase 1 source inventory or schema package.

## Layout

```text
opendss_altdss_library/
  README.md
  manifest.json
  schemas/
    common.schema.json
    object_property.schema.json
    api.schema.json
    example.schema.json
    issue.schema.json
  references/   # Phase 2 catalogs
  examples/     # Versioned examples and their metadata
```

The schemas use the evidence labels and provenance fields from the Coding Assistant Skill Framework template. The `source` record captures title, URL or path, section/symbol, and access date. Execution state is recorded separately from source evidence.

## Schema status

These schemas define a first pass based on the charter's object/property, API, example, and issue record categories. They are structural contracts for later records; they do not establish API behavior, select a supported package version, or claim runtime compatibility. Review and refine them before bulk extraction.
