# Find a class in the object index

Start with the OpenDSS class name from the DSS command or model, such as `RegControl` or `PVSystem`. The object index has one entry per class in the Phase 5 scope. Each entry gives its catalogued or deferred status and points to the available workflow, AltDSS records, engine namespaces, examples, readback evidence, fixture runs, and sources. [Object index](../../opendss_altdss_library/references/opendss_objects.json)

From the repository root, read an entry by name in PowerShell.

~~~powershell
$library = 'opendss_altdss_library'
$index = Get-Content -LiteralPath "$library/references/opendss_objects.json" -Raw | ConvertFrom-Json
$entry = $index | Where-Object element_class -eq 'RegControl'
$entry | ConvertTo-Json -Depth 6
~~~

Open the file at `property_catalog.path` relative to the library root and select the row whose `element_class` matches your query. The property catalogs hold the property names, types, units, descriptions, defaults, and source citations. Both counts refer to the whole linked file, including every class in a shared catalog.

~~~powershell
$catalog = Get-Content -LiteralPath "$library/$($entry.property_catalog.path)" -Raw | ConvertFrom-Json
$catalog | Where-Object element_class -eq $entry.element_class
~~~

- Resolve `altdss.class_record` by `module_path` in the AltDSS API catalog. Resolve `interface_record` by the module and class name on either side of the separator. Circuit points to the AltDSS context and its `ctx.Commands` path. [AltDSS API catalog](../../opendss_altdss_library/references/altdss_python_api.json)
- Filter the engine catalog by `engine.namespaces`. Follow example IDs and source IDs to their registries for files, versions, evidence labels, and access dates. Workflow and readback paths are relative to the repository root. [Engine catalog](../../opendss_altdss_library/references/dss_capi.json) · [Examples](../../opendss_altdss_library/references/examples.json) · [Sources](../../opendss_altdss_library/references/sources.json)
- Use `fixture_usage` to find the scenarios that exercise the class. This includes Circuit and LineCode from the input scripts and LoadShape from the daily configuration. [Fixture catalog](../../opendss_altdss_library/references/fixtures.json)

For a deferred class such as `PVSystem`, the record gives the scope decision and available sources. Open those pointers for context and check the class status before relying on property-level or runtime evidence. [Deferred class decision](../phase_4/README.md#81-deferred-class-catalogs-decision-17)
