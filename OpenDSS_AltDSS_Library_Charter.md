# OpenDSS and AltDSS Reference Library

**Status:** Initial scope and architecture  
**Library version:** 0.1 draft  
**Source review date:** 2026-11-13

## Purpose

Build a searchable, evidence-based reference library for OpenDSS circuit modeling and the AltDSS-Python implementation interface. OpenDSS remains the domain model: circuit elements, buses and nodes, DSS command language, object properties, and electrical behavior. AltDSS-Python is the intended Python interface engine for building, compiling, and inspecting models.

This library documents OpenDSS and its selected Python interface. It does not yet define WindMil-to-OpenDSS conversion mappings.

## Scope and source layers

| Layer | What the library records | Primary sources |
|---|---|---|
| OpenDSS concepts and text format | Circuit model, buses/nodes, element classes, DSS commands, properties, and example circuit organization | EPRI OpenDSS documentation and examples |
| AltDSS-Python | `altdss` objects, properties, methods, creation/editing patterns, batch behavior, and package version | AltDSS-Python documentation and source |
| DSS C-API backend | Engine identity, supported platforms, engine-facing API behavior, version relationship, and known extensions | `dss_capi` documentation and source |
| Related Python interfaces | A separate comparison/reference for DSS-Python (`dss`) and OpenDSSDirect.py (`opendssdirect`) | Their respective documentation and source |

The C-API and the Python packages are separate catalog namespaces. DSS-Python and OpenDSSDirect.py are not synonyms for AltDSS-Python. Keep each package’s import names, object model, signatures, and compatibility notes distinct. The related packages are documented for comparison and interoperability; the project’s primary implementation target is AltDSS-Python.

## Hybrid data strategy

### Generated from documentation and source

- Documentation inventory: title, publisher, URL, applicable version, retrieval date, topics, and known coverage gaps.
- API catalogs: class/object names, properties, methods, signatures, argument types, enumerations, and links to source locations when machine-readable documentation or source declarations expose them.
- DSS examples: extract code blocks and index by task, object classes, dependencies, source, and documented version.
- Cross-references: connect OpenDSS object classes to AltDSS counterparts and to relevant DSS-Python or OpenDSSDirect.py interfaces without assuming one-to-one equivalence.
- Release metadata: version, source revision/tag, checked date, and changes recorded in release notes.

Generated records retain the original spelling and source location. Extraction is a starting point; it does not establish behavior beyond what the cited source says.

### Curated or user-reviewed records

- Differences between OpenDSS concepts and AltDSS-specific APIs or extensions.
- Behavioral interpretations where documentation is incomplete, conflicting, or ambiguous.
- Which API patterns the project intends to standardize on.
- Examples marked as successfully executed, including package versions, environment, commands, and observed results.
- Engineering conventions and modeling policies that are not determined by OpenDSS documentation alone.

Do not fill unresolved items with inferred method names, default values, or assumed equivalence. Record them as open questions until a primary source or reproducible test resolves them.

## Evidence labels

Use the Coding Assistant Skill Framework labels on each behavior or example record:

- `Official-current`
- `Official-versioned`
- `Observed-working`
- `Example-only`
- `Inferred`
- `Unverified`

Every record should preserve its exact source URL or repository path, section or symbol, version/tag where available, and access date. Execution status must distinguish inspected examples from tests run against AltDSS.

## Suggested package layout

```text
opendss_altdss_library/
  SKILL.md
  manifest.json
  references/
    opendss_concepts.json
    dss_language.json
    opendss_objects.json
    altdss_python_api.json
    dss_capi.json
    python_interface_comparison.json
    examples.json
    troubleshooting.json
    changelog.json
  examples/
```

Large catalogs and examples belong in references. `SKILL.md` should hold operating instructions: check target versions, search evidence before coding, preserve API namespaces, validate with the selected engine, and report the validation level accurately.

## Initial primary-source set

- [OpenDSS documentation home](https://opendss.epri.com/)
- [OpenDSS scripting language](https://opendss.epri.com/BasicsoftheOpenDSSScriptingLangu.html)
- [Circuit model concept](https://opendss.epri.com/CircuitModelConcept.html)
- [Basic examples](https://opendss.epri.com/BasicExamples.html)
- [OpenDSS COM interface overview](https://opendss.epri.com/COMInterface.html)
- [OpenDSS Direct DLL overview](https://opendss.epri.com/OpenDSSSharedlibrary-DirectDLL1.html)
- [DSS C-API repository](https://github.com/dss-extensions/dss_capi)
- [AltDSS-Python documentation](https://dss-extensions.org/AltDSS-Python/)
- [DSS-Python documentation](https://dss-extensions.org/DSS-Python/)
- [OpenDSSDirect.py repository](https://github.com/dss-extensions/OpenDSSDirect.py)

EPRI documentation supplies the OpenDSS model and language reference. DSS-Extensions sources establish the behavior and API for the selected alternative engine and Python packages. Record those source families separately; do not imply that the alternative engine is the EPRI implementation.

## Build sequence and stop gates

1. **Inventory:** index the source pages, repositories, release notes, package docs, examples, and existing OpenDSS Library files. Mark each source’s scope and version.
2. **Normalize:** define JSON schemas for object/property, API, example, and issue records; preserve source paths and evidence labels.
3. **Extract:** generate initial catalogs from structured docs and source declarations; retain extraction provenance and flag uncertain fields for review.
4. **Curate:** review API namespace boundaries, version distinctions, conflicting descriptions, and examples needing target execution.
5. **Retrieve:** add exact-symbol and concept search with version/evidence filters and source output.
6. **Validate:** check schemas and retrieval, then exercise representative AltDSS-Python tasks against a recorded package version and fixture circuit.
7. **Release:** package the skill with a manifest listing package versions, source check date, validation levels, known gaps, and supported tasks.

**Stop gate:** Do not label the library compatible with an AltDSS release until its target version is stated and representative tasks have been validated against that version. A source review alone is not runtime validation.

## Open decisions

- Exact AltDSS-Python package version to support first.
- Whether the first implementation will build circuits through `altdss` objects, emit DSS text and compile it, or support both workflows.
- Whether DSS-Python or OpenDSSDirect.py is needed in the production code path or only belongs in the comparison catalog.
- Which representative circuits and operations will form the first regression set.
