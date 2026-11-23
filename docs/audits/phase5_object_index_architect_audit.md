# Phase 5.1 thin object index — Architect/Auditor Review

**Reviewed branch:** `wp/phase5`, tip `5d0d637` (QA/QC report), clean working tree at review start.
**Package revision under review:** `4f78c264a5f4ad81a09dd5b4d4cc4c23fe0360c9` (index, thin schema, workflow, sources, README, build audit).
**Inputs/baseline revision:** `5c7797e29d6d4e24e9ad4aa7b3c82d387e6df0c1` (decision 22, package issued).
**Review date:** 2026-11-22 (local). **Reviewer environment:** Windows 11 AMD64, Python 3.14.6, `altdss 0.2.4`, `dss-python 0.15.7`, `dss-python-backend 0.14.5` (engine `DSS C-API 0.14.5`), `opendssdirect.py 0.9.4`, `jsonschema 4.26.0`.

**STATUS:** PASS — no required corrections, four observations.

## The acceptance test was that I could re-derive every number, so I did

I wrote an independent checker against the committed files, not against the build audit. It re-derives, per record: the property-file record count and the summed `properties` row count; the `dss_capi.json` record count over the listed namespaces; the example set from `object_classes`; path existence for workflow and readback; source-id membership; `epri_doc_url` equality with one of the record's own source URLs; wrapper pointers against `altdss_python_api.json`; and `fixture_usage` from the goldens and the fixture scripts.

```text
records: 24   catalogued: 16   deferred: 8
engine namespaces referenced: 23
example ids referenced: 19 of 19
source ids referenced: 67 of 132
ALL DERIVED VALUES MATCH
```

Sixteen catalogued classes match the `element_class` set of the property catalogs exactly, in both directions. The eight deferred classes are exactly decision 17's list. `validate_catalogs.py` passes 18/18 with the index at 24 records; 19 examples and 3 fixture runs still pass; `git diff --check` is clean.

## My first checker run failed nine records, and all nine were my error

Worth recording, because the coder was right in both cases and a less careful review would have filed findings:

1. **`fixture_usage`.** I derived class usage from the snapshot goldens' `elements` maps only, which flagged eight records for claiming `ieee13 daily`. The daily golden's `peak_step.elements` holds the same 38 elements, so the daily run genuinely exercises Capacitor, Line, Load, RegControl, Transformer and Vsource. My derivation was narrow, not theirs.
2. **`Circuit` → `ctx.Commands`.** I asserted `context_accessor == ctx.<class>` and flagged `Circuit`. At runtime `altdss` has **no** `Circuit` class, no `ctx.Circuit`, and no `ctx.ActiveCircuit`; the context exposes `ctx.Commands` and `ctx.Name`. So `ctx.Commands` with the `altdss.AltDSS` record is the accurate pointer, and the record's note says so. I verified all 23 other `ctx.<Class>` accessors exist on a fresh context. This is a **commendable deviation**: the coder did not invent a uniform shape for a class that has none, and documented the exception in the record and the workflow instead.

`Circuit` and `LineCode` are also correctly claimed for all three runs although neither appears in any golden `elements` map — I confirmed the entry scripts create a circuit (`new circuit.IEEE13Nodeckt`, `New object=circuit.ieee34-1`) and define or redirect line codes.

## The schema enforces thinness, and cannot enforce truth

Independent negative tests against the registered schema:

| Seeded change | Result |
|---|---|
| the committed index | valid |
| same records in reverse order | valid — the set is order-independent |
| duplicate class replacing another | rejected — `Too many items match the given schema (expected at most 1)` |
| record carrying a `properties` array | rejected — `Additional properties are not allowed ('properties' was unexpected)` |
| record carrying `name`, or `units` | rejected |
| nested `description` inside `engine` | rejected |
| 23 records | rejected — the 24-set is pinned by `minItems`/`maxItems` and 24 `contains` clauses |
| deferred record carrying a catalog | rejected |
| catalogued record with `property_catalog: null` | rejected |
| inflated `engine.record_count` | **valid** — not expressible in JSON Schema |
| wrong `fixture_usage` | **valid** — not expressible in JSON Schema |

The last two rows are the honest limit of the guard: the schema proves the index is thin and complete, and the mechanical re-derivation is what proves it is true. Both were applied.

No property detail leaked into the file: the strings `properties`, `data_type`, `default_value`, `units` and `description` appear nowhere in `opendss_objects.json`, and `additionalProperties: false` on both the record and each nested pointer object closes the door on a later "just one convenient field" edit.

## Sources, checked live rather than trusted

`sources.json` grew 127 → 132 with five new EPRI pointers and no existing record touched. I fetched every one:

| URL | Status | Title |
|---|---|---|
| `PVSystem.html` | 200 | `PVSystem` |
| `Storage.html` | 200 | `Storage` |
| `InvControl.html` | 200 | `InvControl` |
| `ExpControl.html` | 200 | `ExpControl` |
| `CableModelinginOpenDSS.html` | 200 | `Cable Modeling in OpenDSS` |

The name-form trap is real and the catalog navigates it correctly: `CapControl.html` 404 / `CapControl1.html` 200, `RegControl.html` 200 / `RegControl1.html` 404, `GenDispatcher.html` and `GenDispatcher1.html` both 404 (hence `epri_doc_url: null` with three implementation pointers retained), and `TSData.html` plus `TSData1.html` both 404, which is why TSData cites the cable-modeling technote. All five new records carry `version_or_ref: null` and `accessed: 2026-11-22`, consistent with the other 27 EPRI records.

Evidence labels follow the status: all 16 catalogued classes are `Observed-working`, all 8 deferred are `Official-versioned`. A deferred record claiming observed runtime behaviour would have been a misstatement, and none does.

## Scope

`git diff 5c7797e..HEAD` touches eight files: the index, its schema, the workflow, `sources.json`, the library README, and the three audit/QA documents. No element catalog, example, fixture, golden, tool, `manifest.json` or plan changed. The README line that said `opendss_objects` remains empty for Phase 5 is gone, which is now true.

## Observations (no action requested)

- **O-1** `Circuit` is the only non-uniform row in the file (`ctx.Commands`, `altdss.AltDSS`, null interface). That is correct; anyone writing the 5.2 tool must not assume `altdss.class_record` splits into a collection accessor for every class.
- **O-2** The two properties the schema cannot check — count accuracy and fixture usage — are exactly the ones a human will eventually get wrong by hand. Package 5.2 should expose the derivation as a `--check` mode so a stale count fails a command instead of waiting for a reviewer with a script.
- **O-3** `minItems: 24` / `maxItems: 24` is a useful tripwire now and a speed bump later: adding any class in Phase 6 requires the schema and the catalog to change in the same commit. That is the intent, but it should be written into the 5.2/5.3 handoff so nobody "fixes" the schema by relaxing it.
- **O-4** `CNData` and `TSData` have runtime readbacks in `phase3b_line_geometry_wires_readback.json` yet zero tagged examples, so their `example_ids` are legitimately empty while `readback_evidence` is not. Retrieval by example will miss them; retrieval by readback will not.

## Where the package lands

The thin rule from decision 22 is now enforced by schema, demonstrated by negative test, and checked by re-derivation. `opendss_objects` is no longer empty, which means every catalog the charter names now holds content — the first time that has been true.
