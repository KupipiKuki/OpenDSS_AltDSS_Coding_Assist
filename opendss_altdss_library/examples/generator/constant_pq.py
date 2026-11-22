"""Compare scheduled generation with its solved terminal power."""
from math import isclose, sqrt

from altdss import altdss, enums


def main():
    ctx = altdss.NewContext()
    ctx.Commands(
        "New Circuit.generator_pq BasekV=12.47 Bus1=source\n"
        "New Load.fixture Bus1=source.1.2.3.0 Phases=3 kV=12.47 kW=1500 kvar=500"
    )
    generator = ctx.Generator.new(
        "pq", Bus1="source.1.2.3.0", Phases=3, Conn="wye", kV=12.47,
        kW=1000, PF=0.95, Model=enums.GeneratorModel.ConstantPQ,
    )
    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise RuntimeError("The constant-PQ generator example did not converge")
    power, = generator.TotalPowers()
    scheduled_kvar = 1000 * sqrt(1 / 0.95**2 - 1)
    if not (isclose(power.real, -1000, rel_tol=1e-5) and isclose(power.imag, -scheduled_kvar, rel_tol=1e-5)):
        raise RuntimeError(f"Unexpected generator terminal power: {power}")
    print(f"Scheduled P={generator.kW:.2f} kW, Q={generator.kvar:.2f} kvar, rating={generator.kVA:.2f} kVA")
    print(f"Terminal 1 (negative means injection): P={power.real:.2f} kW, Q={power.imag:.2f} kvar")


if __name__ == "__main__":
    main()
