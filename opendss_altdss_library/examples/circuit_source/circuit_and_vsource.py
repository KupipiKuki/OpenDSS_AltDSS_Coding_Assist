"""Create a circuit, configure its built-in source, then solve and read it back."""

from math import isclose

from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.source_demo Bus1=src BasekV=12.47 Phases=3 pu=0.98 Angle=5")
    source = ctx.Vsource["source"]
    source.edit(MVASC3=250.0, MVASC1=200.0, X1R1=4.0, X0R0=3.0)
    ctx.Solution.Solve()

    if (
        not ctx.Solution.Converged
        or len(ctx.Vsource) != 1
        or not isclose(source.BasekV, 12.47)
        or not isclose(source.pu, 0.98)
        or not isclose(source.Angle, 5.0)
        or not isclose(source.MVASC3, 250.0)
        or source.Bus2 != "src.0.0.0"
        or list(ctx.Bus["src"].Nodes) != [1, 2, 3]
    ):
        raise ValueError("Unexpected circuit or built-in source readback")

    print(f"circuit={ctx.Name}, source={source.Name}, phases={source.Phases}")
    print(f"BasekV={source.BasekV:g}, pu={source.pu:g}, Angle={source.Angle:g}")
    print(f"Bus1={source.Bus1}, Bus2={source.Bus2}, MVASC3={source.MVASC3:g}")
    print(f"solution frequency={ctx.Solution.Frequency:g} Hz")


if __name__ == "__main__":
    main()
