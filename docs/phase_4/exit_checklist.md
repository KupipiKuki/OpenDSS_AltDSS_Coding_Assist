# Phase 4 exit checklist

Coder validation is complete. Gate 5 awaits independent QA/QC and the architect's manifest reconciliation. Owner acceptance of Package 4.5 follows that review. [Implementation plan §6.5](../implementation_plan.md#65-acceptance-stop-gate) · [Exit build audit](../audits/phase4_exit_audit.md) · [QA/QC handoff](../handoffs/Phase_4_Exit_QAQC_handoff.md)

Run the checks from the repository root in a clean environment installed from the validation requirements. [Pinned requirements](../../opendss_altdss_library/tools/requirements-validation.txt)

~~~powershell
$library = 'opendss_altdss_library'
$interfaceReport = Join-Path ([IO.Path]::GetTempPath()) 'phase4-exit-interface-report.json'
$goldens = @(
    "$library/examples/fixtures/ieee13/golden.json"
    "$library/examples/fixtures/ieee13/golden_daily.json"
    "$library/examples/fixtures/ieee34/golden.json"
)
~~~

| Plan item | Verification command | Recorded result and evidence |
| --- | --- | --- |
| 1. Match pinned fixtures to goldens | `python -B "$library/tools/run_fixtures.py"` | PASS for both snapshots and the IEEE 13 daily profile. [Exit build audit](../audits/phase4_exit_audit.md#validation-commands-and-output) |
| 2. Compare all wrapper pairs within tolerance | `python -B "$library/tools/compare_interfaces.py" --report $interfaceReport` | PASS for three pairs per snapshot with zero numeric deltas on DSS C-API 0.14.5. [Result summary](../audits/phase4_cross_interface_report.json) · [Exit build audit](../audits/phase4_exit_audit.md#validation-commands-and-output) |
| 3. Record source, checksums, license, engine, solver, date and revision | `Get-Content -LiteralPath $goldens -Raw` and `Get-FileHash -LiteralPath $goldens -Algorithm SHA256` | All three revision 1 files carry the metadata and match the baseline hashes. [Fixture catalog](../../opendss_altdss_library/references/fixtures.json) · [Hash proof](../audits/phase4_exit_audit.md#baseline-preservation) |
| 4. Publish observed failure modes and resolutions | `python -B "$library/tools/validate_catalogs.py"` and `(Get-Content "$library/references/troubleshooting.json" -Raw \| ConvertFrom-Json).Count` | PASS for 18 schema pairs and 16 confirmed records. The audit records the runtime observation supporting each entry. [Symptom index](../workflows/troubleshooting.md) · [Rechecks](../audits/phase4_exit_audit.md#troubleshooting-rechecks) |
| 5. Record QA/QC sign-off and runtime scope | `Get-Content docs/audits/phase4_exit_qaqc.md` and `(Get-Content "$library/manifest.json" -Raw \| ConvertFrom-Json).validation.runtime` | Package 4.5 QA/QC and the final manifest update are pending. [QA/QC handoff](../handoffs/Phase_4_Exit_QAQC_handoff.md) · [Manifest](../../opendss_altdss_library/manifest.json) |
| 6. Require approval for a new golden revision | In a disposable tree, run `python -B "$library/tools/run_fixtures.py" --fixture ieee13 --update-golden`. Repeat with `--reason "Unapproved QA probe"`. | The accepted guard checks rejected missing and unapproved reasons. The targeted approved-update check verified an independent revision increment. [Snapshot approval checks](../audits/phase4_fixture_harness_qaqc.md#negative-and-governance-checks-disposable-clones-at-the-pinned-commit-committed-goldens-untouched--sha-256-verified-beforeafter) · [Daily approval checks](../audits/phase4_loadshape_daily_audit.md#commands-and-results) |

## Validation scope

- The recorded runs cover the IEEE 13 and IEEE 34 snapshots and a 24-step, one-hour daily profile on IEEE 13. Year-long QSTS, harmonic analysis, and unbalanced-fault studies are outside the recorded runtime scope.
- The cross-interface result demonstrates wrapper agreement on the shared DSS C-API 0.14.5 binary. Independent numerical validation requires a separate reference.
- Decision 17 defers the GrowthShape, CapControl, GenDispatcher, AutoTrans, PVSystem, Storage, InvControl, and ExpControl catalogs. [Deferred classes](README.md#81-deferred-class-catalogs-decision-17)
- `opendss_objects` remains empty for Phase 5 retrieval. [Object catalog](../../opendss_altdss_library/references/opendss_objects.json)
