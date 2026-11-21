#!/usr/bin/env python3
"""Print the Circuit/Vsource constructor readbacks and focused probes as JSON."""
from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from importlib.resources import files
from math import isclose, sqrt

from altdss import altdss

from run_examples import LIBRARY_ROOT, environment_block, expected_targets, installed

CATALOG = LIBRARY_ROOT / "references/circuit/vsource_properties.json"
DSS_EXAMPLE = LIBRARY_ROOT / "examples/circuit_source/circuit_and_vsource.dss"


def new_circuit(command="New Circuit.vsource_probe"):
    ctx = altdss.NewContext()
    ctx.Commands(command)
    return ctx, ctx.Vsource["source"]


def normalize(value):
    if isinstance(value, IntEnum):
        return int(value)
    if isinstance(value, complex):
        return [value.real, value.imag]
    return getattr(value, "Name", value)


def near(actual, expected, label):
    if not isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def sequence_impedance(source):
    return [source.R1, source.X1, source.R0, source.X0]


def read_defaults():
    records = json.loads(CATALOG.read_text(encoding="utf-8"))
    ctx, _ = new_circuit("New Circuit.defaults")
    source = ctx.Vsource.new("readback_default", begin_edit=False)
    result = {"Circuit": {"name": {"status": "read back", "value": ctx.Name}}, "Vsource": {}}
    for row in records[1]["properties"]:
        key, keyword = row["name"], row.get("altdss_keyword")
        if key == "name":
            entry = {"status": "read back", "value": source.Name}
        elif keyword == "Like":
            entry = {"status": "action", "note": "Creation keyword and method with no getter."}
        elif key in ("z1", "z0"):
            equal(hasattr(source, key.upper()), False, f"Python attribute {key}")
            ctx.Commands(f"? Vsource.{source.Name}.{key}")
            entry = {"status": "DSS text readback", "value": json.loads(ctx.TextResult)}
        else:
            raw = getattr(source, keyword)
            value = normalize(raw)
            if row["default_value"] is not None:
                equal(value, row["default_value"], f"Vsource.{keyword}")
            entry = {"status": "read back", "value": value}
            if isinstance(raw, IntEnum):
                entry["enum_member"] = raw.name
            if keyword == "Spectrum":
                entry["object_repr"] = repr(raw)
        result["Vsource"][key] = entry
    return result


def check_routing_and_ground():
    ctx, src = new_circuit("New Circuit.routed BasekV=12.47 Phases=3 Bus1=src pu=0.98 Angle=5")
    equal(hasattr(ctx, "Circuit"), False, "Circuit member")
    equal(files("altdss").joinpath("Circuit.py").is_file(), False, "Circuit module")
    equal(len(ctx.Vsource), 1, "Built-in source count")
    equal(ctx.Name, "routed", "Circuit identifier")
    equal(
        (src.Name, src.Bus1, src.Bus2, src.Phases, src.BasekV, src.pu, src.Angle, src.NumTerminals()),
        ("source", "src", "src.0.0.0", 3, 12.47, 0.98, 5.0, 2),
        "Routed source properties",
    )
    ctx.Solution.Solve()
    equal(ctx.Solution.Converged, True, "Routed circuit solve")
    bus = {"name": ctx.Bus["src"].Name, "nodes": [int(node) for node in ctx.Bus["src"].Nodes]}
    equal(bus["nodes"], [1, 2, 3], "Source bus nodes")
    routed = {field: getattr(src, field) for field in ("Name", "Bus1", "Bus2", "Phases", "BasekV", "pu", "Angle")}
    src.Bus1 = "another.1.2.3"
    equal(src.Bus2, "another.0.0.0", "Grounded secondary after Bus1 edit")
    src.Bus2 = "explicit.1.2.3"
    src.Bus1 = "new_primary"
    equal(src.Bus2, "explicit.1.2.3", "Explicit secondary survives")
    return {
        "circuit": ctx.Name, "source_count": len(ctx.Vsource), "source": routed,
        "source_terminals": src.NumTerminals(), "solved_bus": bus,
        "explicit_bus2_after_bus1_edit": src.Bus2,
        "circuit_python_member_present": hasattr(ctx, "Circuit"),
        "circuit_python_module_present": files("altdss").joinpath("Circuit.py").is_file(),
    }


def check_base_scaling():
    ctx, _ = new_circuit()
    src = ctx.Vsource.new("base_probe", Bus1="b2", BasekV=115, Phases=3)
    old = sequence_impedance(src)
    old_pu = src.puZ1
    old_base = src.BasekV**2 / src.BaseMVA
    near(old[0], old_pu.real * old_base, "Initial R1 on base")
    near(old[1], old_pu.imag * old_base, "Initial X1 on base")
    src.BasekV = 12.47
    new = sequence_impedance(src)
    new_base = src.BasekV**2 / src.BaseMVA
    for index, (before, after) in enumerate(zip(old, new, strict=True)):
        near(after, before * new_base / old_base, f"Base scaling component {index}")
    near(src.puZ1.real, old_pu.real, "R1 per unit after base edit")
    near(src.puZ1.imag, old_pu.imag, "X1 per unit after base edit")
    return {
        "owner": "standalone base_probe, unsolved",
        "constructor_ohm_literals": [1.65, 6.6, 1.9, 5.7],
        "ohms_at_115_kv": old, "ohms_at_12_47_kv": new,
        "ZBase_ohms": [old_base, new_base],
        "puZ1_at_115_kv": normalize(old_pu), "puZ1_at_12_47_kv": normalize(src.puZ1),
    }


def check_specifications():
    ctx, src = new_circuit()
    results = {}
    src.edit(MVASC3=600.0, MVASC1=500.0, X1R1=3.0, X0R0=2.0)
    near(src.Isc3, 600.0 * 1000 / (sqrt(3) * src.BasekV), "MVA family")
    results["mva"] = {"MVASC3": src.MVASC3, "MVASC1": src.MVASC1, "Isc3": src.Isc3}

    src.edit(Isc3=3000.0, Isc1=2500.0, X1R1=4.0, X0R0=3.0)
    near(src.MVASC3, sqrt(3) * src.BasekV * 3000 / 1000, "Current family")
    src.X1R1 = 10.0
    near(src.X1 / src.R1, 10.0, "Ratio edit applies to active current family")
    near(src.Isc3, 3000.0, "Ratio edit keeps current family")
    results["current"] = {
        "Isc3": src.Isc3, "Isc1": src.Isc1, "MVASC3": src.MVASC3,
        "X1_over_R1_after_ratio_edit": src.X1 / src.R1,
    }

    src.edit(R1=0.50, X1=1.50, R0=0.90, X0=1.70)
    equal(sequence_impedance(src), [0.50, 1.50, 0.90, 1.70], "Scalar ohmic family")
    results["scalar_ohms"] = sequence_impedance(src)

    ctx.Commands("Edit Vsource.source Z1=[0.2,0.8] Z0=[0.3,0.9] Z2=[0.25,0.85]")
    equal(sequence_impedance(src), [0.2, 0.8, 0.3, 0.9], "Complex ohmic family")
    queried = {}
    for field, expected in (("Z1", [0.2, 0.8]), ("Z0", [0.3, 0.9])):
        equal(hasattr(src, field), False, field + " Python property")
        ctx.Commands(f"? Vsource.source.{field}")
        queried[field] = json.loads(ctx.TextResult)
        equal(queried[field], expected, field + " DSS text readback")
    equal(normalize(src.Z2), [0.25, 0.85], "Z2 Python readback")
    results["complex_ohms"] = {**queried, "Z2": normalize(src.Z2), "python_Z1_Z0_present": False}

    src.edit(BaseMVA=100.0, puZ1=0.02 + 0.08j, puZ0=0.03 + 0.09j, puZ2=0.025 + 0.085j)
    zbase = src.BasekV**2 / src.BaseMVA
    per_unit_ohms = sequence_impedance(src)
    for index, (observed, pu) in enumerate(zip(per_unit_ohms, [0.02, 0.08, 0.03, 0.09], strict=True)):
        near(observed, pu * zbase, f"Explicit per-unit conversion {index}")
    results["explicit_per_unit"] = {"ZBase_ohms": zbase, "ohms": per_unit_ohms}

    src.edit(R1=0.50, X1=1.50, R0=0.90, X0=1.70)
    equal(sequence_impedance(src), per_unit_ohms, "Previously specified puZ1 remains active")
    results["scalar_edit_after_per_unit_ohms"] = sequence_impedance(src)
    src.BaseMVA = 200.0
    for index, (observed, old) in enumerate(zip(sequence_impedance(src), per_unit_ohms, strict=True)):
        near(observed, old / 2, f"BaseMVA edit in per-unit family {index}")
    results["per_unit_after_base_mva_edit"] = {"BaseMVA": src.BaseMVA, "ohms": sequence_impedance(src)}
    src.edit(MVASC3=600.0, MVASC1=500.0, X1R1=3.0, X0R0=2.0)
    near(src.Isc3, 600.0 * 1000 / (sqrt(3) * src.BasekV), "MVA family restored")
    equal(normalize(src.puZ1), [0.02, 0.08], "Previously specified per-unit display")
    results["mva_after_per_unit"] = {"Isc3": src.Isc3, "ohms": sequence_impedance(src), "puZ1_readback": normalize(src.puZ1)}
    return results


def check_frequency():
    ctx, src = new_circuit("Set DefaultBaseFrequency=50\nNew Circuit.fifty")
    initial = [ctx.Solution.Frequency, src.Frequency, src.BaseFreq]
    equal(initial, [50.0, 50.0, 50.0], "Circuit-dependent initialization")
    ctx.Solution.Frequency = 55.0
    solution_edit = [ctx.Solution.Frequency, src.Frequency, src.BaseFreq]
    equal(solution_edit, [55.0, 50.0, 50.0], "Existing source after solution frequency edit")
    src.BaseFreq = 48.0
    element_base_edit = [ctx.Solution.Frequency, src.Frequency, src.BaseFreq]
    equal(element_base_edit, [55.0, 50.0, 48.0], "Existing source after element base frequency edit")
    return {
        "columns": ["Solution.Frequency", "Vsource.Frequency", "Vsource.BaseFreq"],
        "after_creation_hz": initial, "after_solution_edit_hz": solution_edit,
        "after_element_base_edit_hz": element_base_edit,
    }


def check_dss_example():
    ctx, src = new_circuit(DSS_EXAMPLE.read_text(encoding="utf-8"))
    equal((len(ctx.Vsource), ctx.Solution.Converged, src.Bus2), (1, True, "src.0.0.0"), "DSS example")
    equal((src.BasekV, src.MVASC3, src.pu, src.Angle), (12.47, 250.0, 0.98, 5.0), "DSS example source")
    nodes = [int(node) for node in ctx.Bus["src"].Nodes]
    equal(nodes, [1, 2, 3], "DSS example bus nodes")
    return {"circuit": ctx.Name, "source": src.Name, "bus_nodes": nodes}


def main():
    for package, target in expected_targets().items():
        equal(installed(package), target, package + " version")
    print(json.dumps({
        "environment": {**environment_block(), "date": date.today().isoformat()},
        "defaults": read_defaults(),
        "circuit_routing": check_routing_and_ground(),
        "base_scaling": check_base_scaling(),
        "specifications": check_specifications(),
        "frequency": check_frequency(),
        "dss_example": check_dss_example(),
    }, indent=2))


if __name__ == "__main__":
    main()
