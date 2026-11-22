"""Solve a grounded-wye bank and report complex power at each terminal."""
from math import isclose

from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.capacitor_demo BasekV=12.47 Bus1=source")
    bank = ctx.Capacitor.new("shunt", Phases=3, Conn="wye", Bus1="source.1.2.3", kV=12.47, kvar=[600])
    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise RuntimeError("The capacitor demo did not converge")

    powers = bank.TotalPowers()
    if len(powers) != 2 or not isclose(powers[0].imag, -600, rel_tol=0.01) or abs(powers[1]) > 1e-8:
        raise RuntimeError(f"Unexpected terminal powers: {powers}")
    for terminal, power in enumerate(powers, start=1):
        print(f"Terminal {terminal}: P={power.real:.4f} kW, Q={power.imag:.4f} kvar")


if __name__ == "__main__":
    main()
