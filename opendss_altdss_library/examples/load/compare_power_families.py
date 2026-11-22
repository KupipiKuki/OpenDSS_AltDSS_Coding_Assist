"""Compare equivalent kW/PF and kW/kvar inputs on a solved circuit."""
from math import isclose, sqrt

from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.load_family_demo BasekV=12.47 Bus1=source")
    common = {"Bus1": "source.1.2.3.0", "kV": 12.47, "Phases": 3, "Conn": "wye"}
    kw, pf = 60.0, 0.95
    kvar = kw * sqrt(1 / pf**2 - 1)
    by_pf = ctx.Load.new("by_pf", **common, kW=kw, PF=pf)
    by_kvar = ctx.Load.new("by_kvar", **common, kW=kw, kvar=kvar)
    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise RuntimeError("The load family comparison did not converge")

    for load in (by_pf, by_kvar):
        served = load.TotalPowers()[0]
        if not (isclose(served.real, kw, rel_tol=1e-6) and isclose(served.imag, kvar, rel_tol=1e-6)):
            raise RuntimeError(f"Unexpected served power for {load.Name}: {served}")
        print(f"{load.Name}: PF={load.PF:.4f}, base kVA={load.kVA:.4f}, served={served:.4f} kVA")


if __name__ == "__main__":
    main()
