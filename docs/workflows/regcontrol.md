# Configure and verify a RegControl

Create the circuit and transformer before adding the regulator. In AltDSS use `ctx.RegControl.new(name, Transformer=transformer, ...)`. A transformer name also works if it resolves to the existing transformer. With DSS text, define the transformer before `New RegControl.name Transformer=stepdown ...`. Use `VReg` and `RevVReg` in Python. The spellings `Vreg` and `RevVreg` raise `AttributeError` on both attribute reads and constructor keyword assignment. [AltDSS-Python 0.2.4 wrapper](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/RegControl.py#L607-L642) · [Property catalog](../../opendss_altdss_library/references/regcontrols/regcontrol_properties.json)

Set the one-based `Winding` to select the monitored terminal. It assigns `TapWinding` to the same winding, so write a separate `TapWinding` after `Winding`. With local sensing, configure `VReg` as volts on the PT secondary, `Band` as the total width in volts, and `PTRatio` for the monitored voltage. For example, `VReg=123 Band=2` sets a band of 122–124 V. [Winding and ratio setters](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L406-L420) · [Voltage target and band](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L1060-L1084)

Leave `Bus` empty for local sensing. A remote bus can specify a node, for example `Bus="secondary.1"`. The control then uses one phase and two conductors and scales the remote sample with `RemotePTRatio`. A `PTRatio` write copies its value into `RemotePTRatio`. Set `PTRatio` first and a distinct `RemotePTRatio` last. The IEEE 13 probe with `Bus="634"` and the default ratio reached the upper tap bound. [Remote topology](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L589-L605) · [Remote voltage scaling](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L992-L1018)

`PTPhase` selects an entry in the voltage sample buffer. Use an index in range for local sensing, or use `"min"` or `"max"` to select by magnitude. Positive indices read back as plain integers, including the default `1`. The AltDSS enum has the two sentinel members `min=-3` and `max=-2`. Use buffer index 1 for the single-phase remote path. [Engine selection](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L639-L680) · [Wrapper enum](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/enums.py#L440-L443)

## Choose how to solve after a manual tap write

`TapNum` reads and writes the signed step count about the tapped winding's midrange. Read it immediately after writing to detect clamping by the transformer's `PresentTap` setter. On the IEEE 13 fixture the winding has 32 steps over 0.9–1.1 pu, so requests of 99 and −99 read back as 16 and −16. [Tap setter](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L1245-L1262) · [Transformer bounds](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PDElements/Transformer.pas#L1391-L1426)

| Solve path | When to use it | IEEE 13 result after writing tap 5 |
| --- | --- | --- |
| `ctx.Solution.Solve()` or DSS `Solve` with `ControlMode=Static` | Let the enabled controllers regulate. | Returned to tap 9 after 12 total iterations. |
| DSS `Set ControlMode=Off` followed by `Solve` | Keep the manual tap and bypass the circuit's control actions until the mode is restored. | Held tap 5. |
| `ctx.Solution.SolveNoControl()` | Keep the manual tap for one power flow and preserve the selected mode. | Held tap 5 with Static still selected. The control-iteration counter retained its previous value. |

Read back the tap and voltage after the solve. For a local wye winding, use the magnitude of the selected winding-voltage sample divided by `PTRatio`. The Python example uses a controlled Static solve and asserts tap 3 and voltage within the band. The DSS example uses `ControlMode=Off` and queries tap 4. The dedicated readback verifies the DSS tap and about 122.91429 V on the phase-1 PT secondary. [Python example](../../opendss_altdss_library/examples/regcontrol/controlled_voltage.py) · [DSS example](../../opendss_altdss_library/examples/regcontrol/fixed_tap_voltage.dss) · [Readback matrix](../audits/phase4_regcontrol_readback.json)

Set `Enabled=False` to stop this controller while leaving the transformer energized. The IEEE 13 probe held tap 9 after disabling the controller and changing `VReg` to 100. A RegControl is a non-injecting circuit element. Its `TotalPowers()` values are zero by design. Read the transformer for kW and kvar and the regulator for the tap. [Enabled sampling](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/Solution.pas#L1974-L1985) · [Control currents](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/ControlElem.pas#L166-L178)

Use `reg.Like("source")` or DSS `Like=source` to copy settings. Use `reg.Reset()` or DSS `Reset=yes` to clear the pending tap change and disarm the control. Immediate readback in the reset probe held the manually set tap 4. Passing either method as a Python constructor keyword raises `AttributeError`. [Copy implementation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L441-L484) · [Reset implementation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L1233-L1237)

## Diagnose creation and solve errors

| Error | Observed path | Check |
| --- | --- | --- |
| `#122` | A two-winding transformer was given `Winding=5`. | Select an existing monitored terminal. |
| `#124` | Creation with other properties and no transformer, an unknown transformer name, or a Line name in the transformer field. | Create the transformer first and check the reference. |
| `#482` | Bare Python `new(name)` succeeded, then the first solve aborted with the transformer unset. | Supply `Transformer` at creation. |
| `#485` | IEEE 13 started at tap 0 with `MaxTapChange=1` and ran out of control iterations. It reached tap 9 in 12 total iterations with the default 16. | Check the initial tap and control-iteration budget when setting a per-iteration step limit. |

The engine also defines `#123` for a controlled object of the wrong type. The supported string-reference probes resolved to `#124`. The matrix labels `#123` source-only for the supported reference paths and preserves the complete observed exception strings. [Binding and winding guards](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/RegControl.pas#L567-L637) · [Readback matrix](../audits/phase4_regcontrol_readback.json)
