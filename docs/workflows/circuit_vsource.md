# Create a Circuit and configure its Vsource

These examples use AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API 0.14.5. A Vsource is a two-terminal voltage source behind an impedance. The examples configure the built-in source and solve a small illustrative circuit. [EPRI Vsource overview](https://opendss.epri.com/Vsource.html) · [Python example](../../opendss_altdss_library/examples/circuit_source/circuit_and_vsource.py) · [DSS example](../../opendss_altdss_library/examples/circuit_source/circuit_and_vsource.dss)

## Create the circuit

1. Start from a fresh context. In Python, call `altdss.NewContext()` and use `ctx.Commands(...)` or `ctx(...)` for the command below.
2. Run `New Circuit.<name>`. The pinned Python distribution exposes a context and a Vsource collection. Circuit creation happens through the text command.
3. Supply source properties after the circuit name. The engine adds `Vsource.source` and forwards those properties to it. Configure that object in place for a single-source example.

```dss
New Circuit.source_demo Bus1=src BasekV=12.47 Phases=3 pu=0.98 Angle=5
Edit Vsource.source MVASC3=250 MVASC1=200 X1R1=4 X0R0=3
Solve
```

The Python example edits the same source with `ctx.Vsource["source"].edit(...)`. Use `ctx.Vsource.new(name, ...)` only to create an additional source in an existing circuit. A standalone allocation takes a name. Supply `Bus1` and `BasekV` to define the intended connection and voltage base. [Context commands](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/AltDSS.py#L426-L450) · [Engine command routing](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/DSSGlobals.pas#L426-L449)

## Choose an impedance specification

Use one coherent family per source. The engine lists these complete specification sets, some of which have defaults for omitted values. They describe sets of model inputs and do not define the minimum Python allocation signature.

| Family | Complete inputs | Units |
| --- | --- | --- |
| Short-circuit capacity | `MVASC3`, `MVASC1`, `X1R1`, `X0R0` | MVA and dimensionless ratios |
| Short-circuit current | `Isc3`, `Isc1`, `X1R1`, `X0R0` | A and dimensionless ratios |
| Scalar components | `R1`, `X1`, `R0`, `X0` | Ω |
| Complex components | `Z0`, `Z1`, `Z2` | Ω, in real/imaginary pairs in DSS text |
| Per-unit components | `BaseMVA`, `puZ0`, `puZ1`, `puZ2` | MVA base and complex per-unit values |

MVA writes select the MVA calculation, current writes select the current calculation, and direct impedance writes select the impedance calculation. An X/R ratio edit affects the active MVA or current calculation. It does not switch the calculation family. Within the impedance calculation, a previously specified `puZ1` can still control recalculation after an ohmic edit. The runtime probe confirmed that scalar ohmic writes were overwritten in that case, and that switching back to MVA could leave the stored per-unit readback unchanged. Use a fresh source definition when comparing families and check the ohmic readback. [Engine spec sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L228-L241) · [Family selection](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L446-L525) · [Recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L761-L800)

The pinned Python wrapper has no `Z1` or `Z0` member or creation keyword. Use DSS text to set or query them, for example `Edit Vsource.source Z1=[0.2,0.8] Z0=[0.3,0.9]` and `? Vsource.source.Z1`. Read the query result from `ctx.TextResult`, or inspect the scalar components on the Python object. Python supports `Z2` and the per-unit fields as complex values. [Wrapper keywords](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Vsource.py#L694-L727) · [Engine complex rows](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L284-L311)

## Voltage base, terminals, and frequency

- **Voltage and impedance.** `pu` scales voltage magnitude. `puZ1`, `puZ0`, and `puZ2` express impedance on `ZBase = BasekV² / BaseMVA` in ohms. Use the line-to-line voltage base for the three-phase example. For explicit per-unit input, the engine multiplies the complex values by ZBase. On a default MVA source, the calculated ohms also change with the voltage base. Read the calculated ohms after changes because constructor literals are overwritten when the source initializes. [Voltage and impedance calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L710-L772) · [Base setters](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L510-L523)
- **Terminals.** A bare Vsource allocation starts with generated terminal names. Without an explicit `Bus2`, assigning `Bus1=src` makes the second terminal `src.0.0.0` for three phases. Set `Phases` before `Bus1` when you need a different phase count and want the setter to size the automatic node list accordingly. Set `Bus2` explicitly for a different connection. [Terminal allocation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/CktElement.pas#L350-L376) · [Grounding rule](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L369-L395)
- **Frequency.** Set `DefaultBaseFrequency` before `New Circuit` to establish a different initial system fundamental. A circuit created with 50 Hz initializes the source's `Frequency` and inherited `BaseFreq` to 50 Hz. Changing `ctx.Solution.Frequency` later leaves those source fields at 50 Hz. Set each explicitly when the study requires it. [Circuit fundamental](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Common/Circuit.pas#L375-L395) · [Source initialization](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/VSource.pas#L637-L647)

## Read back the model

| What to check | AltDSS-Python readback |
| --- | --- |
| Circuit name | `ctx.Name` |
| Routed source values | `ctx.Vsource["source"]` fields such as `BasekV`, `Phases`, `Bus1`, `Bus2`, `pu`, and `Angle` |
| Source flags and options | `Enabled`, `BaseFreq`, and integer-backed `ScanType`, `Sequence`, and `Model` |
| Spectrum | `ctx.Vsource["source"].Spectrum.Name`, initially `defaultvsource` |
| Solution and bus | `ctx.Solution.Frequency` and `ctx.Solution.Converged`. Inspect `ctx.Bus["src"].Nodes` after solving or building the bus list. |

Run the recorded examples and probes from the repository root with the pinned validation environment active.

```powershell
python opendss_altdss_library/tools/run_examples.py
python opendss_altdss_library/tools/readback_circuit_vsource.py
```

[Property catalog](../../opendss_altdss_library/references/circuit/vsource_properties.json) · [Readback matrix](../audits/phase3b_circuit_vsource_readback.json) · [Source index](../../opendss_altdss_library/references/sources.json)
