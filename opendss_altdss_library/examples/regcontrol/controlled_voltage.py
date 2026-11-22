"""Run a static controlled solve and check its selected tap and PT voltage."""
from altdss import altdss
from dss.enums import ControlModes


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.regulator_demo BasekV=12.47 Bus1=source")
    transformer = ctx.Transformer.new(
        "stepdown", Phases=3, Windings=2, Buses=["source.1.2.3.0", "secondary.1.2.3.0"],
        Conns=["wye", "wye"], kVs=[12.47, 4.16], kVAs=[1000, 1000], XHL=5,
    )
    ctx.Commands("New Load.fixture Bus1=secondary.1.2.3.0 Phases=3 Conn=wye kV=4.16 kW=100 kvar=20")
    control = ctx.RegControl.new("regulator", Transformer=transformer, Winding=2, VReg=123, Band=2, PTRatio=20)
    if control.TapNum != 0:
        raise RuntimeError(f"Expected a neutral initial tap, got {control.TapNum}")

    ctx.Solution.ControlMode = ControlModes.Static
    ctx.Solution.Solve()
    pt_volts = abs(transformer.WindingVoltages(control.Winding)[0]) / control.PTRatio
    if not ctx.Solution.Converged or control.TapNum != 3 or not 122 <= pt_volts <= 124:
        raise RuntimeError(f"Unexpected controlled result: tap {control.TapNum}, PT voltage {pt_volts:.5f} V")
    print(f"Static controlled solve: tap={control.TapNum}, PT voltage={pt_volts:.5f} V")


if __name__ == "__main__":
    main()
