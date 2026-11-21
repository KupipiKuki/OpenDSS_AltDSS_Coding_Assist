"""Build two overhead lines from the same positions and conductor data."""

from math import isclose

from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.geometry_demo Bus1=source BasekV=12.47 Phases=3")

    wire = ctx.WireData.new(
        "demo_wire",
        RDC=0.30,
        RAC=0.31,
        RUnits="km",
        GMRAC=0.007,
        GMRUnits="m",
        Radius=0.009,
        RadUnits="m",
        NormAmps=300.0,
        EmergAmps=450.0,
    )
    spacing = ctx.LineSpacing.new(
        "demo_spacing",
        NConds=4,
        NPhases=3,
        Units="m",
        X=[-1.0, 0.0, 1.0, 0.0],
        H=[10.0, 10.0, 10.0, 8.0],
    )
    conductors = [wire] * 4
    geometry = ctx.LineGeometry.new(
        "demo_geometry",
        NConds=4,
        NPhases=3,
        Spacing=spacing,
        Conductors=conductors,
        Reduce=True,
    )

    from_geometry = ctx.Line.new(
        "by_geometry",
        Bus1="source.1.2.3",
        Bus2="geometry_end.1.2.3",
        Geometry=geometry,
        Length=1.0,
        Units="km",
    )
    from_spacing = ctx.Line.new(
        "by_spacing",
        Bus1="source.1.2.3",
        Bus2="spacing_end.1.2.3",
        Spacing=spacing,
        Conductors=conductors,
        Length=1.0,
        Units="km",
    )

    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise RuntimeError("The illustrative circuit did not converge")
    for line in (from_geometry, from_spacing):
        if line.Phases != 3 or not isclose(line.Length, 1.0):
            raise RuntimeError(f"Unexpected line dimensions for {line.Name}")
        print(f"{line.Name}: {line.Phases} phases, {line.Length:g} km")
    print(f"geometry: {geometry.NConds} conductors, Reduce={geometry.Reduce}")
    print(f"spacing: {spacing.NConds} positions, {len(from_spacing.Conductors)} conductors")


if __name__ == "__main__":
    main()
