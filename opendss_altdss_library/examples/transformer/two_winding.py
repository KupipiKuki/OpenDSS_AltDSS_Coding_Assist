"""Solve a loaded two-winding transformer and inspect its winding results."""
from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.transformer_demo BasekV=12.47 Bus1=source")
    transformer = ctx.Transformer.new(
        "stepdown",
        Phases=3,
        Windings=2,
        Buses=["source.1.2.3.0", "secondary.1.2.3.0"],
        Conns=["wye", "wye"],
        kVs=[12.47, 4.16],
        kVAs=[1000, 1000],
        pctR=[0.2, 0.2],
        XHL=7,
    )
    ctx.Commands("New Load.demo Bus1=secondary.1.2.3.0 Phases=3 Conn=wye kV=4.16 kW=100 PF=1")
    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise RuntimeError("The transformer demo did not converge")

    currents = transformer.WindingCurrents()
    primary_voltages = transformer.WindingVoltages(1)
    total, load, no_load = transformer.LossesByType()
    print(f"Winding current samples: {len(currents)}")
    print(f"Primary winding voltages (V): {primary_voltages}")
    print(f"Losses (VA): total={total}, load={load}, no-load={no_load}")


if __name__ == "__main__":
    main()
