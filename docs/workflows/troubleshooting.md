# Troubleshoot OpenDSS and AltDSS readbacks

These wrapper and engine behaviors were reproduced on AltDSS-Python 0.2.4, DSS-Python 0.15.7, OpenDSSDirect.py 0.9.4, and DSS C-API 0.14.5. Other failure modes may occur. Use the interface comparison catalog for accessor mappings and this index for symptoms. [Interface comparison catalog](../../opendss_altdss_library/references/python_interface_comparison.json) · [Troubleshooting catalog](../../opendss_altdss_library/references/troubleshooting.json)

## Control state

- TapNumber follows the active regulator. [`ts-tapnumber-not-indexed`](../../opendss_altdss_library/references/troubleshooting.json#L3)
- A controlled solve can move a manually written tap. [`ts-controlled-solve-retaps`](../../opendss_altdss_library/references/troubleshooting.json#L185)
- Out-of-range local PTPhase reads back as 1. [`ts-ptphase-out-of-range`](../../opendss_altdss_library/references/troubleshooting.json#L215)

## Units

- Losses returns W/var alongside kW/kvar power accessors. [`ts-losses-watts-vs-kilowatts`](../../opendss_altdss_library/references/troubleshooting.json#L151)

## Accessor shape and spelling

- DSS-Python Text.Command is a string property. [`ts-dss-text-command-property`](../../opendss_altdss_library/references/troubleshooting.json#L33)
- DSS-Python solution lives on the active circuit. [`ts-dss-solution-via-active-circuit`](../../opendss_altdss_library/references/troubleshooting.json#L62)
- Total iteration accessor spelling differs by wrapper. [`ts-totaliterations-accessor-casing`](../../opendss_altdss_library/references/troubleshooting.json#L91)
- DSS-Python ActiveClass.First is an integer property. [`ts-active-class-first-property`](../../opendss_altdss_library/references/troubleshooting.json#L121)
- The Capacitor wrapper has no Spectrum field. [`ts-capacitor-no-spectrum`](../../opendss_altdss_library/references/troubleshooting.json#L245)
- LoadShape construction uses lowercase new. [`ts-loadshape-lowercase-new`](../../opendss_altdss_library/references/troubleshooting.json#L338)

## Interface and context behavior

- Default classic contexts can share circuit and cursor state. [`ts-python-context-isolation`](../../opendss_altdss_library/references/troubleshooting.json#L276)

## Creation and data errors

- LoadShape.new creates a shape when one already has that name. [`ts-loadshape-new-duplicates`](../../opendss_altdss_library/references/troubleshooting.json#L308)
- A missing LoadShape CSV fails at the file assignment. [`ts-loadshape-missing-csv`](../../opendss_altdss_library/references/troubleshooting.json#L367)
- Empty LoadShape statistics can leave a pending error. [`ts-loadshape-empty-statistics`](../../opendss_altdss_library/references/troubleshooting.json#L397)
- PMult typed writes require exactly NPts samples. [`ts-loadshape-pmult-length`](../../opendss_altdss_library/references/troubleshooting.json#L428)
- NPts alone does not create sample values. [`ts-loadshape-npts-without-array`](../../opendss_altdss_library/references/troubleshooting.json#L460)
