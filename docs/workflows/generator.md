# Generator workflow

Use this workflow for Generator on AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. [Property catalog](../../opendss_altdss_library/references/generators/generator_properties.json) · [Runtime matrix](../audits/phase3b_generator_readback.json)

## Wire and specify the machine

Give the generator a name, `Bus1`, and a positive rated `kV`. Use line-to-line kV for two or three phases and branch voltage for one phase. Specify `Phases`, `Conn`, and bus nodes together. Generator has one terminal. Three-phase wye uses four conductors, three-phase delta uses three, and both one-phase connections use two. [Engine property flags](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L553-L637) · [Connection topology](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L664-L731)

The two scheduled-power families are `kW` with `PF` and `kW` with `kvar`. Either a kW or PF write synchronizes scheduled kvar. For the second family, write `kvar` after `kW` to derive PF from both. With positive kW, negative PF schedules reactive absorption. A bare generator reports 1000 kW, 60 kvar, and PF 0.88 as independently initialized values. Its kW and kvar imply PF about 0.9982. Specify a complete power pair when creating a model. [Specification sets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L510-L517) · [Defaults](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L945-L953) · [Power updates](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L732-L765)

`kVA` is the machine rating. It automatically follows 1.2 times signed kW until an explicit rating is given. Setting `kVA` leaves scheduled kW and kvar alone. DSS text `MVA=3` writes a 3000 kVA rating with the same effect. In Python use `kVA=3000` since the pinned wrapper has no MVA keyword or attribute. The negative-kW probe drew about 500 kW and 242.16 kvar while automatically storing a rating of −600 kVA. [Rating alias](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L620-L643) · [Explicit rating flag](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L815-L818) · [Automatic rating](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L2880-L2897)

## Choose a model and inspect terminal power

| Model | Use | Validation on the pinned stack |
|---|---|---|
| 1 `ConstantPQ` | Schedule constant P and Q in the normal voltage range. | Solved and checked against the scheduled pair. |
| 2 `ConstantZ` | Represent generation as constant admittance. | Near-rated-voltage snapshot passed. |
| 3 `ConstantPV` | Hold P and request a voltage within reactive limits. | Target and achieved voltage checked under two limit settings. |
| 4 `ConstantP_fixedQ` | Keep Q fixed while P can follow dispatch scaling. | Near-rated-voltage snapshot passed. |
| 5 `ConstantP_fixedX` | Represent Q by a fixed reactance while scheduling P. | Near-rated-voltage snapshot passed. |
| 6 `Usermodel` | Use a configured electrical user model. | Guard errors reproduced. Compiled-model execution was outside scope. |
| 7 `Approximateinvertermodel` | Use current-limited PQ. The solver derives the limit using `VMinpu`. | Near-rated-voltage snapshot passed. The current-limiting regime was source reviewed. |

Use the exact Python enum spellings in the table. `TotalPowers()` returns complex kW and kvar into the generator at its single terminal. Negative P or Q indicates injection of the corresponding quantity. Read the real and imaginary parts separately. The Model 1 example reports about −1000 kW and −328.68 kvar. The properties `kW`, `kvar` and `PF` read back the schedule. [Python enum spellings](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/enums.py#L286-L305) · [Engine model dispatch](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L2110-L2145) · [Runnable Python example](../../opendss_altdss_library/examples/generator/constant_pq.py)

### Validate the voltage target and reactive limits

For Model 3, set `Vpu`, `Minkvar` and `Maxkvar` after the final power edit. A scheduled kW, PF or kvar write can reset the limits. `Vpu` is the target. Compare it with the solved mean phase-to-neutral voltage divided by the rated phase-to-neutral voltage for the balanced wye case. [Limit resets](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L732-L765) · [Voltage target and clamp](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1635-L1692)

| Requested Vpu | Reactive limits (kvar) | Achieved voltage (pu) | Terminal Q (kvar) |
|---|---:|---:|---:|
| 1.00 | ±120 | 0.99473 | −120.00 |
| 1.03 | ±120 | 0.99473 | −120.00 |
| 1.00 | ±3000 | 1.00000 | −1677.56 |
| 1.03 | ±3000 | 1.00443 | −3000.00 |

In the 1.03 pu cases the generator hit its positive `Maxkvar` injection limit, shown with a negative sign by the terminal-power convention. Scheduled `kvar` remained about 431.79 and PF remained 0.88. `PVFactor` scales each reactive correction inside Model 3. The tests used the default 0.1. [Runnable DSS example](../../opendss_altdss_library/examples/generator/pv_voltage_target.dss) · [Solved cases](../audits/phase3b_generator_readback.json)

## Assign shapes and interpret dispatch inputs

`Daily`, `Yearly`, and `Duty` take a LoadShape name or object and return a typed reference. Assigning Daily leaves the other references independent. During a duty solve an unset Duty can fall back to Daily. `DutyStart` offsets the duty shape time in hours. Assigning a `UseActual` shape to any of the three can replace scheduled kW and kvar with peak values. Read the schedule again after assignment. [Shape assignment](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L782-L792) · [Shape evaluation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1069-L1106)

The Generator engine evaluates `DispMode` and `DispValue` against the load-level or price reference for the corresponding mode. `ForceOn` bypasses those checks. `Status=Fixed` selects constant scaling when the machine is on. Use valid `GeneratorDispatchMode` members. Reading an invalid numeric value through the Python enum getter raised `ValueError`. A separate GenDispatcher can edit scheduled kW and kvar and request another solve. The dispatch behavior and controller were source reviewed. [Generator dispatch logic](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1108-L1183) · [GenDispatcher updates](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/Controls/GenDispatcher.pas#L302-L345)

## Use actions and registers

- `UseFuel` enables the fuel model. `FuelkWh` is capacity and `pctFuel` and `pctReserve` are percentages. Call `generator.Refuel()` or use DSS `Refuel=yes` to restore the fuel level to 100%. The action preserves fuel capacity and reserve. The Python creation keyword raised `AttributeError`. [Fuel action](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L483-L487) · [Fuel properties](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L613-L647)
- Use `generator.Like("source")` or DSS `Like=source` to copy parameters. The Python creation keyword raised `AttributeError`. The copy can keep the target bus and conductor count while changing `Conn`. Reconfigure and verify wiring and conductor layout before solving. [Copy routine](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L844-L897)
- Access `kWh`, `kvarh`, `Max kW`, `Max kVA`, `Hours`, and `$` via `RegisterNames()`, `RegisterValues()`, or `RegistersDict()`. The matrix includes a one-hour daily sample. Its `Max kVA` comes from the sampled power and is distinct from the machine rating. [Register methods](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/CircuitElement.py#L525-L549) · [Sample integration](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L2213-L2258)

The `UserModel`, `UserData`, `ShaftModel`, and `ShaftData` defaults are empty strings. A Model 6 solve without a configured library raised `#567`. Choosing an explicitly missing library raised `#570` on construction. `DynamicEq` refers to an existing DynamicExp and its `DynOut` list is initially empty. The two output names belong in shaft-speed, then shaft-angle order. Dynamic and harmonic simulations, compiled model execution, and fuel-consumption studies are outside package scope. [User model solve guard](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/generator.pas#L1816-L1836) · [Library selection](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/GenUserModel.pas#L140-L174) · [DynOut wrapper](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/Generator.py#L809-L826)
