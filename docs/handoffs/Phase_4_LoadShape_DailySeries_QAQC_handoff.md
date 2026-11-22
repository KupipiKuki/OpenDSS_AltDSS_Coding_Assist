# Phase 4.3 LoadShape and daily profile QA/QC handoff

- **Reviewer** Mistral 4
- **Architect and auditor** DeepSeek
- **Branch** `wp/phase4`
- **Inputs revision** `5efeaf1a97f4a63b5f4ec828cc63df71ded4ee2e`
- **Package revision** `2e4d92b40b799280ed23429314b2ddddae75de7a`. Review the package artifacts at this commit. The follow-up commit supplies the handoff pin.

Review the LoadShape catalog, daily fixture, and RegControl F-1 rider. Record the reviewed revision and working-tree state. [Coder handoff](Phase_4_LoadShape_DailySeries_Coder_handoff.md) · [Build audit and commands](../audits/phase4_loadshape_daily_audit.md) · [Readback matrix](../audits/phase4_loadshape_readback.json)

## Verify

- Use the pinned runtime to reproduce 18 schema checks, 18 example runs, three fixture comparisons and the LoadShape matrix. Confirm the two new examples pair hours 1–3 with 50, 100 and 150 kW.
- Compare the catalog's 22 keys, units, defaults and pinned row citations against the wrapper and engine. Review the deferred statistics error, buffer sizing, exact array length, actual values, both normalization paths, and the Python and DSS time setters.
- Independently integrate the 24 recorded hourly load powers, select the maximum kW step, and confirm full bus and element capture at that hour. Check 15 shaped loads, all three regulator taps and both fixed capacitor states, the actual named fixture selector, and the golden tolerance application.
- In a disposable Git tree, reproduce the byte-identical daily golden from the initial approval. Verify missing or incorrect approval, a corrupted energy record, a wrong peak hour, and an out-of-tolerance step voltage fail. Check the existing named snapshot update path separately.
- Hash both snapshot goldens against the baseline blobs. Verify upstream fixture inputs and prior catalog records. Review the RegControl path-filtered diff for only the F-1 wording in the catalog and workflow.

Record the verdict, reviewed commit, environment, numerical checks, regeneration results, and any required corrections in `docs/audits/phase4_loadshape_daily_qaqc.md`.
