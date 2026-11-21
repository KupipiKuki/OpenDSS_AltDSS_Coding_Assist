# Phase 1 External Audit Disposition

**Evidence snapshot:** This disposition uses the DeepSeek source checks dated 2026-11-13/14. [External audit report](PHASE_1_EXTERNAL_AUDIT_REPORT.md)
**Project target selected afterward:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, DSS C-API/backend 0.14.5.

## Documentation, release, and change-history comparison

| Source family | Documentation state | Stable target / source ref | Beta or untagged channel | Change-history state at audit | Disposition |
|---|---|---|---|---|---|
| AltDSS-Python | Docs banner 0.2.3 | [Release 0.2.4](https://github.com/dss-extensions/AltDSS-Python/releases/tag/0.2.4) | [Tag 0.3.0b2](https://github.com/dss-extensions/AltDSS-Python/releases/tag/0.3.0b2), on `fastdss` | [Docs changelog](https://dss-extensions.org/AltDSS-Python/changelog.html) stops at 0.2.3; tagged repo changelog has no 0.3.0 entry | Use 0.2.4 as stable target; disclose docs lag and missing beta notes. |
| DSS-Python | Docs banner 0.15.4 | [Release/tag 0.15.7](https://github.com/dss-extensions/DSS-Python/releases/tag/0.15.7), code on branch `0.15.x` | PyPI 0.16.0b2; PyPI 0.15.8a1 has no matching GitHub tag | [Tagged changelog](https://github.com/dss-extensions/DSS-Python/blob/0.15.7/docs/changelog.md) stops at 0.15.6; 0.15.7 detail is in release notes | Pin 0.15.7 as a runtime dependency and document the `dss` interface in the comparison catalog. |
| OpenDSSDirect.py | Docs banner 0.9.1 | [Release/tag v0.9.4](https://github.com/dss-extensions/OpenDSSDirect.py/releases/tag/v0.9.4) | Tags v0.10.0b1/b2, not published to PyPI | No changelog file; [GitHub Releases](https://github.com/dss-extensions/OpenDSSDirect.py/releases) is the release history | Keep 0.9.4 as comparison-only; use release notes as the change history. |
| DSS C-API | Doxygen docs do not identify one release | [Stable 0.14.5](https://github.com/dss-extensions/dss_capi/releases/tag/0.14.5) | [0.15.0b4](https://github.com/dss-extensions/dss_capi/releases/tag/0.15.0b4) | `master` was 263 commits behind the beta tag; changelog and known-differences content vary by ref | Pin engine claims to 0.14.5; do not cite mutable `master` for target-specific behavior. |
| DSS-Python backend | No independent docs banner | Stable 0.14.5, paired with the selected stable packages | Beta backend 0.15.0b4 is coupled to the beta Python package line | Backend is a separate versioned engine artifact | Keep backend version explicit in the manifest and runtime records. |
| EPRI OpenDSS | [What's New](https://opendss.epri.com/Whatsnew.html) displayed 10.0.0.1 | No EPRI release tag was established in the audit | SourceForge listed installer 11.0.0.1 dated 2026-01-30 | The installer was not inspected; the web page is stale relative to that listing | Treat EPRI pages as page-specific evidence; do not infer installer behavior from the page. |

## Finding disposition

| Audit finding | Status | Where addressed |
|---|---|---|
| H1 AltDSS stable/beta source split | Recorded; stable target selected | This table, manifest, source inventory |
| H2 AltDSS changelog URL and missing beta entry | Correct URL recorded; beta changelog gap disclosed | Source inventory ALT-03 and this table |
| H3 DSS-Python docs/changelog lag and untagged 0.15.8a1 | Stable target selected; beta and untagged artifact separated | This table and source inventory |
| H4 OpenDSSDirect.py has no changelog file | GitHub Releases recorded as release history | This table and source inventory ODD-03 |
| H5 DSS C-API branch/ref staleness | Target claims pinned to 0.14.5; branch staleness documented | This table and package manifest |
| H6 EPRI web/install version mismatch | Mixed-version limitation and uninspected installer disclosed | This table and source inventory EPRI-08/09 |
| M1 Stable/beta dependency coupling | Backend recorded as a distinct manifest target | This table and package manifest |
| M2 GitHub/PyPI channel conflation | Separate stable and prerelease columns retained in inventory | Source inventory version matrix |
| M3 Inconsistent checklist state | Current inventory checklist and phase status reconciled | Source inventory exit checklist |
| M4 Mutable/stale default branches | Target tags/branches are distinguished in the inventory | This table and source inventory |

## Phase 1 closure and deferred work

The Phase 1 audit trail includes the source inventory, this disposition, the external report, the selected target, the package schemas, and the Line/LineCode starter catalog. The starter catalog passed schema validation and its source review is partial. Phase 2 covers source remediation and example indexing. Engine execution belongs to the later validation phase in the charter.

This evidence snapshot is historical. Refresh release and changelog status before making new version-sensitive claims or changing the support target.
