# OpenDSS and AltDSS library release record

**Version** `v1.0.0`, accepted by the owner (decision 25) and tagged at the acceptance commit. This record describes that release; it is the release's front door and its limits are part of what it ships. [Changelog](../../CHANGELOG.md) · [Build audit](../audits/phase5_release_audit.md)

## Package versions

The manifest's `support_targets` object appears below verbatim. [Manifest](../../opendss_altdss_library/manifest.json)

```json
{
  "opendss": "EPRI OpenDSS; online documentation is mixed-version",
  "altdss_python": "0.2.4",
  "dss_python": "0.15.7",
  "dss_python_backend": "0.14.5",
  "dss_capi": "0.14.5",
  "opendssdirect_py": "0.9.4"
}
```

Validated on Python 3.14.6, Windows 11 AMD64, with DSS C-API 0.14.5 revision `87d85c2622c8281b92255335bc7c09b11191b21d`. AltDSS-Python 0.3.0b2 and later are documented for future compatibility and remain unvalidated. [Validation environment and results](../audits/phase5_release_audit.md)

## Source check date

The manifest records `2026-11-21` for the pinned source inventory. Individual citations carry their own access dates and release or revision when available. EPRI online documentation does not state a single OpenDSS version. Cite a pinned release for version-sensitive claims. [Pinned source index](../../opendss_altdss_library/references/sources.json) · [Version reconciliation](../phase_1/PHASE_1_SOURCE_INVENTORY.md)

## Validation levels

The handoff tally covers the element property rows, generated wrapper members, engine records, examples, troubleshooting records, and observed object-index records. The full corpus includes every labeled record exposed by retrieval. [Counting procedure](../audits/phase5_release_audit.md#evidence-counts)

| Evidence | Handoff tally | Full corpus | What the label supports |
| --- | ---: | ---: | --- |
| `Official-current` | 0 | 0 | Claim backed by current official material verified for the stated scope. |
| `Official-versioned` | 1878 | 2012 | Claim traceable to a pinned release, source file and line, or tagged package. |
| `Observed-working` | 51 | 53 | Result reproduced in the recorded target environment. |
| `Observed-export` | 0 | 0 | Value or field captured from an actual export or runtime inspection. |
| `Example-only` | 0 | 0 | Inspected example suitable as an illustration, pending execution evidence. |
| `Inferred` | 0 | 0 | Provisional interpretation that still needs primary evidence or a run. |
| `Unverified` | 1 | 1 | Open question to retain for follow-up. Exclude it from generated calls to the pinned target. |

The 17-file search corpus deliberately excludes the legacy Line/LineCode catalog, the repository's sole catalog with `Official-current` labels, which is retained for provenance and remains outside schema validation and search. [Legacy catalog](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties_legacy.json)

- The `Official-versioned` handoff total is 460 element property rows + 180 wrapper methods + 1094 wrapper properties + 144 engine records. The full corpus also includes 99 wrapper classes, 16 element class records, eight deferred object pointers, and 11 interface records with that label.
- The `Observed-working` handoff total is 19 examples + 16 troubleshooting records + 16 object-index records. Two interface records bring the full total to 53.
- The only `Unverified` record is `Line.epsrmedium`, retained from the Line/LineCode starter catalog. It is marked unsupported on the target. [Line/LineCode catalog](../../opendss_altdss_library/references/lines/opendss_line_linecode_properties.json)

## Known gaps

- **Index and record status.** The manifest's empty `opendss_objects` entry predates the accepted Phase 5.1 index, which has 16 catalogued and eight deferred entries. Phase 4.5 populated the 16-record troubleshooting catalog, and Phase 4.4 populated the 13-record interface comparison catalog. [Object index](../../opendss_altdss_library/references/opendss_objects.json) · [Troubleshooting](../workflows/troubleshooting.md) · [Interface catalog](../../opendss_altdss_library/references/python_interface_comparison.json)
- **Wrapper and engine surfaces.** The generated AltDSS-Python catalog covers object and collection classes and the AltDSS context. Non-element context interfaces, context batch proxies, and internal `_str` proxies are outside scope. The manifest describes C-API coverage through Generator (Line, LineCode, LineGeometry, LineSpacing, WireData, CNData, TSData, Circuit creation, Vsource, Transformer, XfmrCode, Load, Capacitor, and Generator, including inherited fields used by those packages). Phase 4 added RegControl, LoadShape and the fixture/comparison namespaces used by the runtime checks. [Engine catalog](../../opendss_altdss_library/references/dss_capi.json)
- **Windings and shapes.** Transformer and XfmrCode coverage is for two and three windings. The Load package covers the element and shape assignment. LoadShape has a Phase 4.3 catalog, and GrowthShape and AutoTrans remain deferred. [Transformer workflow](../workflows/transformer.md) · [LoadShape workflow](../workflows/loadshape.md)
- **Source coverage and provenance.** Line/LineCode property `source_refs` remain partial (E-3 deferred). Later element packages require per-row citations. The legacy line catalog and builder are retained for provenance only. EPRI version-sensitive behavior requires release-specific evidence. The beta package line has future compatibility notes and no recorded validation. [Implementation plan](../implementation_plan.md) · [Archive](../../archive/README.md)
- **Shared schema metadata.** The manifest names `enum_type`, `reference_class`, and `dss_text_keyword` as declared and carries forward the Capacitor O-1 gap for optional array and write-path metadata. Phase 4 preparation commit `f8fac0c` subsequently declared the seven remaining row fields and recorded the disposition of O-1. [Element property schema](../../opendss_altdss_library/schemas/catalogs/element_properties.schema.json)
- **Capacitor and generator behavior.** The Capacitor catalog covers the element and its `States` hook. The element has no `Spectrum` property. Generator built-in dispatch settings and the separate GenDispatcher control are source-reviewed. Model 3 snapshots use the default `PVFactor`, and sensitivity to changing it is source-reviewed. Compiled models, dynamic studies, harmonics, and fuel consumption are outside the runtime scope. [Capacitor workflow](../workflows/capacitor.md) · [Generator workflow](../workflows/generator.md)
- **Deferred classes (decision 17).** GrowthShape, CapControl, GenDispatcher, AutoTrans, PVSystem, Storage, InvControl, and ExpControl await an owner scope decision. Existing element packages cover their own behavior and control hooks only. [Decision log](../implementation_plan.md#11-owner-decisions)
- **Fixture coverage.** Revision 1 goldens cover IEEE 13 and IEEE 34 snapshots and one 24-step IEEE 13 daily profile. The architect reproduced all three byte-for-byte. Scope excludes year-long QSTS, harmonic studies, and unbalanced-fault studies. All three Python interfaces in the snapshot comparison share DSS C-API 0.14.5. Agreement establishes consistency of the tested wrapper accessors. Independent engine numerics are outside that comparison. [Phase 4 design](../phase_4/README.md) · [Cross-interface audit](../audits/phase4_cross_interface_audit.md)

## Supported tasks

The table cites the workflow and the example IDs or fixture runs that exercise each task on the pinned stack. [Example catalog](../../opendss_altdss_library/references/examples.json) · [Fixture catalog](../../opendss_altdss_library/references/fixtures.json)

| Task | Workflow | Executed evidence |
| --- | --- | --- |
| Create and inspect Lines and shared LineCodes | [Line and LineCode](../workflows/line_linecode.md) | `line-linecode-altdss`, `line-linecode-dss-text` |
| Build overhead lines from conductor data, geometry, and spacing | [Line geometry and conductors](../workflows/line_geometry_wires.md) | `line-geometry-spacing-altdss`, `line-geometry-spacing-dss-text` |
| Create a circuit and configure its built-in Vsource | [Circuit and Vsource](../workflows/circuit_vsource.md) | `circuit-vsource-altdss`, `circuit-vsource-dss-text` |
| Configure two- and three-winding transformers and reuse an XfmrCode | [Transformer and XfmrCode](../workflows/transformer.md) | `transformer-two-winding-altdss`, `transformer-three-winding-xfmrcode-dss` |
| Compare load power-specification families and solve a ZIPV load | [Load](../workflows/load.md) | `load-power-family-comparison-altdss`, `load-zipv-snapshot-dss` |
| Configure a shunt capacitor and verify step states | [Capacitor](../workflows/capacitor.md) | `capacitor-wye-shunt-altdss`, `capacitor-stepped-shunt-dss` |
| Solve scheduled PQ and voltage-target Generator models | [Generator](../workflows/generator.md) | `generator-constant-pq-altdss`, `generator-pv-voltage-target-dss` |
| Set a regulator's voltage target and verify a manual or controlled tap | [RegControl](../workflows/regcontrol.md) | `regcontrol-controlled-voltage-altdss`, `regcontrol-fixed-tap-voltage-dss` |
| Apply a LoadShape and check hourly results against the daily golden | [LoadShape](../workflows/loadshape.md) | `loadshape-daily-steps-altdss`, `loadshape-daily-monitor-dss`, `ieee13 daily` |
| Reproduce and compare snapshot readbacks across the pinned Python interfaces | [Snapshot comparison](../workflows/cross_interface.md) | `ieee13-snapshot-cross-interface`, `ieee13 snapshot`, `ieee34 snapshot` |

**Outside the release claims**

- Independent numerical validation of the engine.
- Property or runtime coverage of the eight deferred classes.
- Using the catalog as a substitute for pinned primary sources.
