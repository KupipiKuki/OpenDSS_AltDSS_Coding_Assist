# Changelog

Dates follow the repository commit history. Decision numbers refer to the [implementation plan](docs/implementation_plan.md#11-owner-decisions).

## Phase 1 — Foundation (2026-11-20)

- The source and version review pinned the stable Python target and retained the beta line as future compatibility (`c8edd43`, `7d1bb90`, both 2026-11-13). [Source inventory](docs/phase_1/PHASE_1_SOURCE_INVENTORY.md) · [Audit disposition](docs/phase_1/PHASE_1_AUDIT_DISPOSITION.md)
- The completed Phase 1 branch landed the library layout, reusable schemas, starter Line/LineCode catalog, handoffs, and external audit (`3263daa`). [Phase 1 documents](docs/phase_1/README.md)

## Phase 2 — Line/LineCode pilot (2026-11-20)

- The pilot delivered the remediated property catalog, source index, line creation workflow, AltDSS and DSS text examples, and schema and example harnesses (`1d4088f`). Decision 1 recorded owner acceptance in the Phase 3A planning history. [Workflow](docs/workflows/line_linecode.md)

## Phase 3A — API and engine catalogs (2026-11-21)

- Generated `altdss_python_api.json` from the pinned wheel and populated `dss_capi.json` with pinned engine citations (`45a004d`). Follow-up commits applied independent QA/QC corrections (`2a0fa39`, `0b5469e`). [QA/QC](docs/audits/phase3a_api_catalogs_qaqc.md)

## Phase 3B — Element packages 1–6 (2026-11-21)

- Decisions 2 and 4 set the six-package scope, order, and review roles. Decisions 5–12 recorded package acceptance and handoff timing. Packages landed for LineGeometry, LineSpacing and conductors (`2cd9b33`), Circuit and Vsource (`555f4f6`), Transformer and XfmrCode (`a7b485d`), Load (`37854f6`), Capacitor (`d7fc55c`), and Generator (`0a88ad3`). Each delivered property data, a workflow, executed examples, and readback evidence. Decision 12 closed Phase 3 (`c85065c`).

## Phase 4 — Fixture validation and exit (2026-11-22)

- **4.1** vendored the pinned IEEE 13 and IEEE 34 circuits and delivered their snapshot goldens and runner (`9736d46`, `d1acffc`). Decisions 3 and 13 set the stop gate and input pin. Decision 16 froze the fixture pin and both revision 1 snapshots.
- **4.2** delivered the RegControl catalog, workflow, examples, and readback matrix (`35a2b7c`) under decisions 14 and 18. **4.3** added the LoadShape catalog and IEEE 13 daily run and recorded the PTPhase readback (`2e4d92b`). Decision 17 scoped LoadShape in and deferred eight classes. Decision 19 froze the daily golden at revision 1.
- **4.4** added the cross-interface snapshot tool, accessor catalog, and comparison report (`159fce0`) under decisions 15 and 20. **4.5** added the troubleshooting catalog and exit evidence (`75c6e1c`, `0187ded`). Decision 21 closed the eight-check Phase 4 stop gate (`29386e9`). [Exit checklist](docs/phase_4/exit_checklist.md)

## Phase 5 — Retrieval and release record (2026-11-22 to 2026-11-23)

- **5.1** landed on 2026-11-22 (`4f78c26`). Decisions 22 and 23 established and accepted the thin index for 16 catalogued and eight deferred classes. [Object index workflow](docs/workflows/object_index.md)
- **5.2** landed on 2026-11-23 (`4b4430b`). Decision 24 accepted the retrieval CLI, citation-bearing results, and index checks (`8ee36b7`). [Retrieval workflow](docs/workflows/retrieval.md)
- **5.3** was issued on 2026-11-23 (`8ee36b7`) and delivered as a candidate that day. It adds the release record, the schema-validated symbol alias registry, and current phase guidance in `skill.md`. [Release record](docs/release/README.md) · [Coder handoff](docs/handoffs/Phase_5_Release_Record_Coder_handoff.md)
