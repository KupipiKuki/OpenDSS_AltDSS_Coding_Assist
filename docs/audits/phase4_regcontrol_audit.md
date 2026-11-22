# Phase 4.2 RegControl build audit

- **Validation date** 2026-11-22
- **Inputs revision** `eb7aca4aac119b1c4478efd958a2aae10fd9d463` on `wp/phase4`
- **Result** Coder validation passed. [Package scope](../handoffs/Phase_4_RegControl_Catalog_Coder_handoff.md) · [Readback matrix](phase4_regcontrol_readback.json) · [Workflow](../workflows/regcontrol.md)

## Environment and sources

| Item | Recorded value |
| --- | --- |
| Platform | Windows 11 AMD64 |
| Python | 3.14.6 |
| AltDSS-Python | 0.2.4 |
| DSS-Python | 0.15.7 |
| DSS-Python backend / DSS C-API | 0.14.5 |
| jsonschema | 4.26.0 |

Validation used a fresh virtual environment referencing the already installed pinned libraries. The tools queried the package versions before execution.

The EPRI element and property pages supplied RegControl terminology. The AltDSS documentation banner reported 0.2.3. The current stable repository release was 0.2.4, whose notes describe the engine synchronization and a Bus collection change. The DSS C-API 0.14.5 changes cover LineGeometries and C headers. The pinned 0.2.4 wrapper, 0.14.5 Pascal source, and runtime readbacks resolved defaults, exact spellings, and guards. [EPRI RegControl](https://opendss.epri.com/RegControl.html) · [EPRI Properties23](https://opendss.epri.com/Properties23.html) · [AltDSS documentation and changelog](https://dss-extensions.org/AltDSS-Python/changelog.html) · [AltDSS-Python releases](https://github.com/dss-extensions/AltDSS-Python/releases) · [DSS C-API 0.14.5 release and changelog](https://github.com/dss-extensions/dss_capi/releases/tag/0.14.5)

The catalog's 35 exact keys match `RegControlProperties`, with 32 local engine properties plus `BaseFreq`, `Enabled`, and `Like`. The object name is the separate first argument. `Transformer` is required for a valid controller. All 177 row citation occurrences use tag-pinned paths and line ranges within the fetched source. [Catalog](../../opendss_altdss_library/references/regcontrols/regcontrol_properties.json) · [Wrapper keyword surface](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/RegControl.py#L607-L642) · [Engine property enum](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L69-L103)

## Commands and results

Run from the repository root with the environment active.

~~~powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B opendss_altdss_library/tools/validate_catalogs.py
python -B opendss_altdss_library/tools/run_examples.py
python -B opendss_altdss_library/tools/run_fixtures.py
$observed = (& python -B opendss_altdss_library/tools/readback_regcontrol.py) -join "`n"
if ($LASTEXITCODE -ne 0) { throw 'RegControl readback failed.' }
$expected = (Get-Content -LiteralPath docs/audits/phase4_regcontrol_readback.json) -join "`n"
if ($observed -cne $expected) { throw 'RegControl matrix differs.' }
git diff --check
~~~

The readback command records the day it ran. For a later rerun, compare after substituting the original capture date on the matrix's `environment.date` line. Compare all remaining fields on the same pinned Windows stack, including the exception strings and JSON-escaped line breaks.

| Check | Result |
| --- | --- |
| Catalog schema validation | 17 of 17 pairs passed. The new RegControl pair uses the existing schema. |
| Catalogued examples | All 16 ran successfully. Both RegControl entries carry the measured environment and `Observed-working`. |
| Standalone tap and voltage assertions | Static Python model reached tap 3 at 122.16480 V. The dedicated runner executed the DSS example with `ControlMode=Off`, verified its query returned 4, and measured 122.91429 V. |
| Matrix reproduction | Two complete readback runs produced identical text after normalizing line endings. All 33 getters and both action entries are populated. |
| Frozen fixture comparisons | IEEE 13 and IEEE 34 both passed against their revision 1 goldens. |
| Repository scope | Shared source, engine, and example catalogs retained their existing records and appended 10, 15, and 2 records respectively. Prior catalog files, Phase 4.1 fixture files and goldens, and the fixture harness matched the input revision. |

## Edge cases and coverage

- IEEE 13 controlled `Solve()` restored tap 9 from manual tap 5. Off and `SolveNoControl()` held 5. `SolveNoControl()` kept the selected Static mode and the previous control-iteration count.
- Immediate writes of 99 and −99 clamped to 16 and −16. With `Winding=2` and `TapWinding=1`, a manual write of 4 changed winding 1 to 1.025 pu while winding 2 stayed at 1.05625 pu. A subsequent `Winding=2` assignment restored `TapWinding=2`.
- The one-step limit raised `#485` from tap zero with a budget of ten control iterations. The default limit of 16 reached tap 9 in 12 total iterations. The exact message and event-log hint are in the matrix.
- `PTRatio=50` overwrote an explicit `RemotePTRatio=10`. Writing the remote value last preserved distinct ratios. The local positive `PTPhase` index read as `int`. The `min` and `max` strings read back as enum members. The three-phase controller became one phase with two conductors when a remote node was specified. Remote IEEE 13 sensing at bus 634 resulted in tap 16.
- `Enabled=False` held tap 9 after writing `VReg=100`. IEEE 13 `RegControl.reg1.TotalPowers()` returned zero kW and kvar, and its associated transformer carried power.
- Both `Like` paths copied the selected voltage settings. Both `Reset` paths kept manual tap 4 on immediate readback. The matrix captures the exact Python errors for using either method as a keyword and for `Vreg` and `RevVreg`.
- `#124` covers the supported constructor paths with omitted, unknown, or wrong-class names, including DSS text with a Line name. Bare Python creation first raised `#482` on solve. Out-of-range monitored winding 5 raised `#122`. The supported-path matrix marks the engine's `#123` branch source-only. An exploratory direct injection of a Python `Line` object did reach that guard, outside the declared `str | Transformer | AutoTrans` input type.

Reverse and cogen transitions, nonzero line-drop compensation, time-driven delays, and diagnostic logging have pinned source coverage. Runtime behavior probes cover forward snapshot regulation and manual-tap scenarios with a standard Transformer. Package 4.5 owns the implementation plan and manifest reconciliation.
