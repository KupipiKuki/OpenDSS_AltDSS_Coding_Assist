# OpenDSS AltDSS Library Package

**Status:** Phase 1 structure and Line/LineCode starter catalog established; remediation is planned for Phase 2  
**Target:** AltDSS-Python 0.2.4, DSS-Python 0.15.7, backend 0.14.5

## Contents

- `manifest.json`: support targets, catalog paths, validation state, and open gaps
- `skill.md`: instructions for agents using or extending the library
- `schemas/records/`: reusable evidence, property, API, example, and issue record schemas
- `schemas/catalogs/`: manifest and catalog schemas
- `references/`: Phase 1 source catalogs and reference materials
- `references/lines/`: Phase 1 Line and LineCode starter catalog; Phase 2 remediation target
- `tools/archive/` and `references/lines/*legacy.json`: retained historical extraction artifacts, not active sources

The Phase 1 catalogs that are still pending extraction contain valid empty JSON arrays. Their coverage is tracked in the manifest. The Line/LineCode starter catalog is only partially source reviewed and is not runtime validated; its remediation is planned for Phase 2.
