# Load workflow

Use this workflow for the `Load` element on AltDSS-Python 0.2.4, DSS-Python 0.15.7, and DSS C-API backend 0.14.5. [Property catalog](../../opendss_altdss_library/references/loads/load_properties.json) · [Runtime matrix](../audits/phase3b_load_readback.json)

## Wire and rate the load

Create the circuit, then supply the load name, `Bus1`, and rated `kV`. Specify `Phases`, `Conn`, and bus node order to match the actual connection. A load has one terminal and models balanced phases. For separately modeled unbalanced phase loads, create individual one-phase loads. [EPRI Load element](https://opendss.epri.com/Load1.html) · [Engine registration](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L402-L457)

For two- and three-phase loads enter line-to-line kV. The engine divides it by √3 for the internal wye voltage base. Delta uses the entered voltage directly. For a one-phase load enter the actual kV across the two conductors. The pinned engine allocates four conductors for three-phase wye and three for three-phase delta. Both one-phase connections use two, and both two-phase connections use three. Editing `kV` updates voltage scaling while the specified nominal power stays the same. [Connection and voltage-base implementation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L479-L560)

## Choose one base-power family

Power values are totals across the load phases. Use kW for active power, kvar for reactive power, and kVA for apparent power.

| Family | Inputs | Calculation and order |
|---|---|---|
| Direct real power and PF | `kW`, `PF` | Sets kvar and kVA from kW and signed PF. |
| Direct real and reactive power | `kW`, `kvar` | Supply kvar after kW to select this family. It derives kVA and PF. |
| Apparent power and PF | `kVA`, `PF` | Sets kW to kVA × abs(PF) and derives kvar. |
| Connected transformer capacity | `XfkVA`, `AllocationFactor`, `PF` | Enter PF before the allocation inputs. The allocation write calculates kW as XfkVA × AllocationFactor × abs(PF). |
| Billed energy | `kWh`, `kWhDays`, `CFactor`, `PF` | kW = kWh ÷ (24 × kWhDays) × CFactor. Use a positive billing duration. |

The engine displays the billing family with PF last and registers its members in the order `kWh, PF, kWhDays, CFactor`. That member order describes the set. When constructing or editing a load, follow the application order appropriate to the selected family. For positive kW, use negative PF to specify leading kvar. [Specification sets and flags](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L368-L457) · [Power and PF recalculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1152-L1198) · [Allocation calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L2167-L2191)

### Confirm the active family after an edit

- The last family-selecting write sets the active calculation. A PF write alone leaves the family in place. After setting `kvar=20` on a 50 kW load, an edit of `PF=0.8` still reads about 0.9285. A later `kVA=100` write uses that derived PF and yields about 92.85 kW.
- Put `PF` before `XfkVA` and `AllocationFactor` in Python and DSS text. The matrix got 44 kW with PF last and 45 kW with PF first for 100 kVA and an allocation factor of 0.5. The earlier calculation used the starting PF of 0.88. Reapplying the allocation factor used the new PF of 0.9. The `Ordering_Last` registration does not describe the execution order seen in these text commands. [Property registration and side effects](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L448-L618)
- Use one `new(...)`, one `edit(...)`, or one DSS command for the family. On a bare load left in edit mode, separate `kW=50` and `PF=0.9` writes left kvar and kVA at the constructor values until `end_edit()`. Finalization gave about 24.2161 kvar and 55.5556 kVA. A bare load created with `begin_edit=False` also showed stale derived reads through the separate attributes. A load previously constructed with completed kwargs refreshed those fields on individual writes in the probe. Read all four values after completing the edit. [Wrapper edit handling](https://github.com/dss-extensions/AltDSS-Python/blob/0.2.4/altdss/DSSObj.py#L414-L432) · [Engine EndEdit](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L725-L737)
- `kVA` read zero on fresh allocation-family examples with explicit PF. An energy-family edit following a 50 kW, 20 kvar definition kept about 53.85 kVA even though the billed energy calculation yielded about 166.67 kW. Use `hypot(kW, kvar)` for the magnitude implied by the current nominal power, and `TotalPowers()` for actual solved per-terminal kW and kvar. [Engine reference-based kVA calculation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1189-L1198) · [Solved Python comparison](../../opendss_altdss_library/examples/load/compare_power_families.py)

## Assign shapes

Assign `Daily`, `Yearly`, `Duty`, and `CVRCurve` by LoadShape name or object, and `Growth` by GrowthShape name or object. Python getters return the referenced objects or `None`. Assigning Daily fills an unset Yearly. Set Yearly explicitly for a distinct profile. An unset Duty can fall back to Daily during duty-cycle evaluation.

Assigning a `UseActual` Daily, Yearly, or Duty shape can replace nominal kW and kvar with peak power from the shape. The probe set a 10 kW load to 1.5 kW. With explicit PF of 0.9, kvar derived to about 0.7265. With the kW/kvar family and explicit peak Q data, kvar read 0.6. Inspect nominal power after assigning the shape. [Shape registration and assignment](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L425-L433) · [Assignment side effects](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L620-L643) · [Power family on assignment](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L989-L1014)

## Specify and solve a ZIPV load

Use `Model=8` with seven explicit `ZIPV` values. Supply the impedance, current, and power weights for kW, the same three weights for kvar, and the per-unit voltage cutoff. Each triplet should sum to one. A bare load reads seven zeros. The engine tracks whether ZIPV was explicitly set, validates the array length, and checks the flag during a ZIPV solve. At low voltage the pinned implementation uses separate fallbacks and a smooth cutoff branch. [ZIPV property and flag](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L396-L400) · [Model implementation](https://github.com/dss-extensions/dss_capi/blob/0.14.5/src/PCElements/Load.pas#L1525-L1652) · [Runnable DSS example](../../opendss_altdss_library/examples/load/zipv_snapshot.dss)

The three accessible enum readbacks are `LoadModel`, `Connection`, and `LoadStatus`. `Class` is the integer load class and `NumCust` is the customer count. `pctMean`, `pctStdDev` and `pctSeriesRL` take percent values. Their default readbacks of 50, 10, and 50 represent internal fractions of 0.5, 0.1, and 0.5. `VMinNorm=0` and `VMinEmerg=0` use the circuit criteria. The default Spectrum object is `Spectrum.defaultload`. [Property catalog](../../opendss_altdss_library/references/loads/load_properties.json)
