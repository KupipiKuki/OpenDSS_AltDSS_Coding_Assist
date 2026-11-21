#!/usr/bin/env python3
"""Print the Phase 3B package 1 property readback and side effect checks as JSON."""
from __future__ import annotations

import json
from datetime import date
from enum import Enum
from math import isclose

from altdss import altdss

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/lines/line_geometry_wires_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/line_geometry/geometry_and_spacing.dss"


def normalize(value):
    if isinstance(value, Enum):
        return value.name
    if hasattr(value, "tolist"):
        return normalize(value.tolist())
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def read_defaults(records):
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.geometry_defaults")
    matrix = {}
    for record in records:
        element = record["element_class"]
        obj = getattr(ctx, element).new("readback_default", begin_edit=False)
        values = {}
        for row in record["properties"]:
            name = row["name"]
            keyword = row.get("altdss_keyword")
            if name == "name":
                result = {"status": "read back", "value": obj.Name}
            elif keyword == "Like":
                result = {"status": "action", "note": "Creation keyword and method with no getter."}
            elif (element, keyword) == ("LineGeometry", "Units"):
                result = {
                    "status": "unavailable",
                    "note": "The constructor allocates no coordinate slots. The scalar Python accessor can raise ValueError even after allocation.",
                }
            else:
                value = normalize(getattr(obj, keyword))
                expected = row["default_value"]
                if expected is not None and value != expected:
                    raise ValueError(f"{element}.{keyword}: expected {expected!r}, observed {value!r}")
                result = {"status": "read back", "value": value}
            values[name] = result
        matrix[element] = values
    return matrix


def check_side_effects():
    ctx = altdss.NewContext()
    ctx.Commands(DSS_EXAMPLE.read_text(encoding="utf-8"))
    geometry = ctx.LineGeometry["demo_geometry"]
    spacing = ctx.LineSpacing["demo_spacing"]
    geom_line = ctx.Line["by_geometry"]
    spaced_line = ctx.Line["by_spacing"]
    if not (
        ctx.Solution.Converged
        and geometry.NConds == spacing.NConds == len(spaced_line.Conductors) == 4
        and geometry.Reduce
        and geom_line.Phases == spaced_line.Phases == 3
        and isclose(geom_line.Length, 1.0)
        and isclose(spaced_line.Length, 1.0)
        and normalize(geometry.X) == normalize(spacing.X)
        and normalize(geometry.H) == normalize(spacing.H)
    ):
        raise ValueError("Unexpected geometry or spacing example readback")
    if (geometry.NormAmps, geometry.EmergAmps) != (300.0, 450.0):
        raise ValueError("Geometry did not take the first conductor's positive ampacities")

    # The Line retains its matrix at the same frequency after a rho edit.
    initial_r = normalize(geom_line.RMatrix)
    geom_line.rho = 1000.0
    ctx.Solution.Solve()
    same_frequency_r = normalize(geom_line.RMatrix)
    ctx.Solution.Frequency = 50.0
    ctx.Solution.Solve()
    new_frequency_r = normalize(geom_line.RMatrix)
    if len(initial_r) != 9 or same_frequency_r != initial_r or new_frequency_r == initial_r:
        raise ValueError("Unexpected geometry resistance matrix cache behavior")

    spacing_probe = ctx.LineSpacing.new("spacing_probe", Units="m")
    spacing_probe.NConds = 4
    conductor = ctx.WireData.new("conductor_probe", RDC=0.30, Diam=0.018, NormAmps=300.0)
    cable = ctx.CNData.new("cn_probe", DiaStrand=0.002)
    if not (
        normalize(spacing_probe.Units) == "ft"
        and isclose(conductor.RAC, 0.306)
        and isclose(conductor.Radius, 0.009)
        and isclose(conductor.CapRadius, 0.009)
        and isclose(conductor.GMRAC, 0.7788 * 0.009)
        and isclose(conductor.EmergAmps, 450.0)
        and isclose(cable.GMRStrand, 0.7788 * 0.001)
    ):
        raise ValueError("Unexpected spacing or conductor setter readback")
    return {
        "geometry_and_spacing": {
            "conductors": geometry.NConds,
            "retained_phases": geom_line.Phases,
            "length_km": geom_line.Length,
            "reduce": geometry.Reduce,
            "spacing_positions_copied": True,
            "first_conductor_ampacities": [geometry.NormAmps, geometry.EmergAmps],
        },
        "geometry_rho_edit": {
            "rho_after_edit_ohm_m": geom_line.rho,
            "r_matrix_changed_at_60_hz": same_frequency_r != initial_r,
            "r_matrix_changed_after_switching_to_50_hz": new_frequency_r != initial_r,
        },
        "spacing_units_after_nconds_edit": normalize(spacing_probe.Units),
        "wire_derived_values": {
            "RAC": conductor.RAC,
            "Radius": conductor.Radius,
            "CapRadius": conductor.CapRadius,
            "GMRAC": conductor.GMRAC,
            "EmergAmps": conductor.EmergAmps,
        },
        "cn_derived_gmrstrand": cable.GMRStrand,
    }


def check_cable_spacing():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.cable_spacing Bus1=source BasekV=12.47 Phases=3")
    shared = {
        "RDC": 0.23, "RAC": 0.24, "RUnits": "km",
        "GMRAC": 0.005, "GMRUnits": "m", "Radius": 0.007, "RadUnits": "m",
        "EpsR": 2.3, "InsLayer": 0.004, "DiaIns": 0.022, "DiaCable": 0.030,
    }
    cn = ctx.CNData.new(
        "demo_cn", **shared, k=12, DiaStrand=0.002, GMRStrand=0.0007788, RStrand=2.4
    )
    ts = ctx.TSData.new(
        "demo_ts", **shared, DiaShield=0.024, TapeLayer=0.0002, TapeLap=20
    )
    spacing = ctx.LineSpacing.new(
        "underground", NConds=3, NPhases=3, Units="m",
        X=[-0.2, 0.0, 0.2], H=[-1.0, -1.0, -1.0],
    )
    for cable in (cn, ts):
        ctx.Line.new(
            cable.Name, Bus1="source.1.2.3", Bus2=f"{cable.Name}_end.1.2.3",
            Spacing=spacing, Conductors=[cable] * 3, Length=1.0, Units="km",
        )
    ctx.Solution.Solve()
    if not ctx.Solution.Converged:
        raise ValueError("Cable spacing circuit did not converge")
    results = {}
    for cable in (cn, ts):
        line = ctx.Line[cable.Name]
        conductors = line.Conductors
        if (
            line.Phases != 3
            or len(conductors) != 3
            or any(type(item) is not type(cable) for item in conductors)
            or len(line.RMatrix) != 9
        ):
            raise ValueError(f"Unexpected cable readback for {line.Name}")
        results[type(cable).__name__] = {
            "phases": line.Phases,
            "conductor_count": len(conductors),
            "resistance_matrix_size": len(line.RMatrix),
        }
    return results


def main():
    for package, target in expected_targets().items():
        if installed(package) != target:
            raise ValueError(f"{package} must be installed at {target}")
    records = json.loads(CATALOG.read_text(encoding="utf-8"))
    environment = {**environment_block(), "date": date.today().isoformat()}
    print(json.dumps({
        "environment": environment,
        "defaults": read_defaults(records),
        "side_effects": check_side_effects(),
        "cable_spacing": check_cable_spacing(),
    }, indent=2))


if __name__ == "__main__":
    main()
