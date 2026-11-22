#!/usr/bin/env python3
"""Compare snapshot readbacks through three Python interfaces to DSS C-API 0.14.5.

All three interfaces run the same engine. A pass demonstrates wrapper agreement.
Independent numerical validation requires a separate reference.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory

INTERFACES = ("altdss", "dss_python", "opendssdirect")
ENGINE_PIN = "0.14.5"
SCOPE = (
    f"AltDSS-Python, DSS-Python and OpenDSSDirect.py share DSS C-API {ENGINE_PIN}. "
    "A pass demonstrates wrapper agreement only. Independent numerical validation is outside this comparison."
)


def verify_engine(version):
    if f"DSS C-API Library version {ENGINE_PIN} " not in version:
        raise ValueError(f"Expected DSS C-API {ENGINE_PIN}, observed {version!r}")


def altdss_snapshot(entry, settings):
    from altdss import altdss

    from run_fixtures import collect_snapshot, configure_solver, verify_source_frequency

    ctx = altdss.NewContext()
    version = ctx.Version()
    verify_engine(version)
    ctx.Commands(f'Redirect "{entry}"')
    solver = configure_solver(ctx.Solution, settings)
    verify_source_frequency(ctx, solver)
    ctx.Solution.Solve()
    return version, solver, collect_snapshot(ctx)


def call_reader(obj, name):
    return getattr(obj, name)()


def call_writer(obj, name, value):
    getattr(obj, name)(value)


def classic_solver(solution, settings, read, write, tolerance_attr):
    from dss.enums import ControlModes, SolveModes

    options = {
        "mode": ("Mode", SolveModes[settings["mode"]]),
        "max_iterations": ("MaxIterations", settings["max_iterations"]),
        "tolerance": (tolerance_attr, settings["tolerance"]),
        "control_mode": ("ControlMode", ControlModes[settings["control_mode"]]),
        "max_control_iterations": ("MaxControlIterations", settings["max_control_iterations"]),
        "base_freq": ("Frequency", settings["base_freq"]),
    }
    for attr, expected in options.values():
        # Setting Mode again can reset the upstream script's already solved state.
        if read(solution, attr) != expected:
            write(solution, attr, expected)
        if read(solution, attr) != expected:
            raise ValueError(f"DSS did not apply solver option {attr}={expected!r}")
    return {
        "mode": SolveModes(read(solution, "Mode")).name,
        "max_iterations": int(read(solution, "MaxIterations")),
        "tolerance": float(read(solution, tolerance_attr)),
        "control_mode": ControlModes(read(solution, "ControlMode")).name,
        "max_control_iterations": int(read(solution, "MaxControlIterations")),
        "base_freq": float(read(solution, "Frequency")),
    }


def classic_buses(circuit, bus, read):
    buses = {}
    for name in read(circuit, "AllBusNames"):
        if circuit.SetActiveBus(name) < 0 or read(bus, "Name").casefold() != name.casefold():
            raise ValueError(f"Could not select bus {name!r}")
        nodes = [int(node) for node in read(bus, "Nodes")]
        values = read(bus, "puVmagAngle")
        if len(values) != 2 * len(nodes):
            raise ValueError(f"{name}: voltage array does not match bus nodes")
        buses[name] = {
            "nodes": nodes,
            "pu_vmag": [float(value) for value in values[::2]],
            "pu_vangle_deg": [float(value) for value in values[1::2]],
        }
    return buses


def classic_elements(circuit, element, capacitors, read, write, query):
    elements = {}
    controls = {}
    for name in read(circuit, "AllElementNames"):
        if circuit.SetActiveElement(name) < 0 or read(element, "Name").casefold() != name.casefold():
            raise ValueError(f"Could not select element {name!r}")
        powers = read(element, "TotalPowers")
        # TotalPowers is already kW/kvar. Losses is W/var.
        loss_w, loss_var = read(element, "Losses")
        elements[name] = {
            "powers_kw_kvar": [[float(p), float(q)] for p, q in zip(powers[::2], powers[1::2], strict=True)],
            "losses_kw_kvar": [float(loss_w) * 0.001, float(loss_var) * 0.001],
        }
        kind, object_name = name.split(".", 1)
        if kind.casefold() == "regcontrol":
            controls[name] = {"tap": int(query(f"? {name}.TapNum"))}
        elif kind.casefold() == "capacitor":
            write(capacitors, "Name", object_name)
            if read(capacitors, "Name").casefold() != object_name.casefold():
                raise ValueError(f"Could not select capacitor {name!r}")
            controls[name] = {"states": [int(state) for state in read(capacitors, "States")]}
    return elements, controls


def classic_snapshot(interface, entry, settings):
    if interface == "dss_python":
        from dss import dss

        version = dss.Version
        circuit = dss.ActiveCircuit
        solution, bus, element = circuit.Solution, circuit.ActiveBus, circuit.ActiveCktElement
        capacitors, sources, text = circuit.Capacitors, circuit.Vsources, dss.Text
        read, write = getattr, setattr
        total_iterations = "Totaliterations"
        tolerance_attr = "Tolerance"
    else:
        from opendssdirect import dss as odd

        version = odd.Version()
        circuit, solution, bus, element = odd.Circuit, odd.Solution, odd.Bus, odd.CktElement
        capacitors, sources, text = odd.Capacitors, odd.Vsources, odd.Text
        read, write = call_reader, call_writer
        total_iterations = "TotalIterations"
        tolerance_attr = "Convergence"

    def query(command):
        write(text, "Command", command)
        return read(text, "Result").strip()

    verify_engine(version)
    write(text, "Command", f'Redirect "{entry}"')
    solver = classic_solver(solution, settings, read, write, tolerance_attr)
    for name in read(sources, "AllNames"):
        if float(query(f"? Vsource.{name}.BaseFreq")) != solver["base_freq"]:
            raise ValueError(f"Vsource.{name}: base frequency differs from the solve frequency")
    solution.Solve()
    if not read(solution, "Converged"):
        raise ValueError(f"Snapshot did not converge after {read(solution, total_iterations)} total iterations")

    source_kw, source_kvar = read(circuit, "TotalPower")
    loss_w, loss_var = read(circuit, "Losses")
    buses = classic_buses(circuit, bus, read)
    elements, controls = classic_elements(circuit, element, capacitors, read, write, query)
    if (len(buses), len(elements)) != (read(circuit, "NumBuses"), read(circuit, "NumCktElements")):
        raise ValueError("Duplicate or missing names in the solved bus or element collection")
    load = sum(complex(p, q) for name, values in elements.items() if name.casefold().startswith("load.")
               for p, q in values["powers_kw_kvar"])
    return version, solver, {
        "solution": {
            "converged": True,
            "iterations": int(read(solution, "Iterations")),
            "total_iterations": int(read(solution, total_iterations)),
            "control_iterations": int(read(solution, "ControlIterations")),
        },
        "totals": {
            "load_kw": load.real,
            "load_kvar": load.imag,
            "source_kw": float(source_kw),
            "source_kvar": float(source_kvar),
            "losses_kw": float(loss_w) * 0.001,
            "losses_kvar": float(loss_var) * 0.001,
        },
        "buses": buses,
        "elements": elements,
        "controls": controls,
    }


def verify_loss_scale(totals):
    # On these loaded feeders the passive active loss must be smaller than the source supply.
    # An unconverted W value fails this kW-scale check, even if both classic facades made the same mistake.
    losses_kw = totals["losses_kw"]
    supplied_kw = abs(totals["source_kw"])
    if not 0.0 <= losses_kw < supplied_kw:
        raise ValueError(f"Expected active losses below source supply in kW, observed {losses_kw} vs {supplied_kw}")


def run_worker(interface, request):
    entry, settings = request["entry"], request["solver"]
    if interface == "altdss":
        version, solver, snapshot = altdss_snapshot(entry, settings)
    else:
        version, solver, snapshot = classic_snapshot(interface, entry, settings)
    verify_loss_scale(snapshot["totals"])
    for group in ("buses", "elements", "controls"):
        normalized = {name.casefold(): value for name, value in snapshot[group].items()}
        if len(normalized) != len(snapshot[group]):
            raise ValueError(f"Duplicate case-insensitive names in {group}")
        snapshot[group] = normalized
    return {"version": version, "engine_version": version.splitlines()[0].strip(), "solver": solver, **snapshot}


def collect_in_subprocess(interface, record, files):
    # Give every process its own verified redirect tree and working directory.
    with TemporaryDirectory(prefix=f"dss-{interface}-") as directory:
        root = Path(directory)
        for relative, data in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        request = {"entry": (root / record["entry_script"]).as_posix(), "solver": record["solver"]}
        proc = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", interface],
            input=json.dumps(request), cwd=root, capture_output=True, text=True, timeout=60,
        )
        if proc.returncode:
            detail = (proc.stderr or proc.stdout).strip()
            raise ValueError(f"{interface} subprocess exited {proc.returncode}: {detail}")
        return json.loads(proc.stdout)


def comparison_pair(reference, candidate, expected, actual, tolerances):
    from run_fixtures import compare

    # Wrapper identification lines differ by design. The actual engine build line must agree.
    left = {key: value for key, value in expected.items() if key != "version"}
    right = {key: value for key, value in actual.items() if key != "version"}
    zero_tolerances = dict.fromkeys(tolerances.keys() - {"reason"}, 0)
    diffs = list(compare(left, right, tolerances))
    nonzero_deltas = []
    for change in compare(left, right, zero_tolerances):
        old, new = change.get("expected"), change.get("actual")
        if change["kind"] == "value" and type(old) in (int, float) and type(new) is type(old) and new != old:
            nonzero_deltas.append({"path": change["path"], "expected": old, "actual": new, "delta": new - old})
    return {
        "reference": reference,
        "candidate": candidate,
        "status": "fail" if diffs else "pass",
        "total_deltas": {
            key: actual["totals"][key] - expected["totals"][key]
            for key in expected["totals"].keys() & actual["totals"].keys()
        },
        "nonzero_deltas": nonzero_deltas,
        "diffs": diffs,
    }


def compare_fixture(record, environment):
    from run_fixtures import checked_inputs, summarize, verify_stack

    result = {"fixture": record["fixture_id"], "scenario": "snapshot", "status": "fail",
              "tolerances": record["tolerances"], "interfaces": {}, "pairs": []}
    try:
        verify_stack(record, environment)
        files = checked_inputs(record)
        readbacks = {}
        for interface in INTERFACES:
            snapshot = collect_in_subprocess(interface, record, files)
            readbacks[interface] = snapshot
            result["interfaces"][interface] = {
                "version": snapshot["version"],
                "solver": snapshot["solver"],
                "summary": summarize(snapshot),
                "totals": snapshot["totals"],
                "controls": snapshot["controls"],
            }
        result["pairs"] = [
            comparison_pair(ref, cand, readbacks[ref], readbacks[cand], record["tolerances"])
            for ref, cand in combinations(INTERFACES, 2)
        ]
        if all(pair["status"] == "pass" for pair in result["pairs"]):
            result["status"] = "pass"
    except (KeyError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result["error"] = str(exc)
    return result


def print_results(report):
    for fixture in report["fixtures"]:
        print(f"{fixture['status'].upper()} {fixture['fixture']} snapshot")
        if "error" in fixture:
            print(f"  {fixture['error']}", file=sys.stderr)
        for interface, result in fixture["interfaces"].items():
            stats = result["summary"]
            taps = {name: obj["tap"] for name, obj in result["controls"].items() if "tap" in obj}
            print(f"  {interface}: {stats['buses']} buses, {stats['elements']} elements, "
                  f"{stats['total_iterations']} total and {stats['control_iterations']} control iterations, "
                  f"taps {', '.join(f'{name}={tap}' for name, tap in sorted(taps.items()))}")
        for pair in fixture["pairs"]:
            print(f"  {pair['candidate']} vs {pair['reference']}: "
                  f"{len(pair['diffs'])} out-of-tolerance differences, "
                  f"{len(pair['nonzero_deltas'])} nonzero numeric deltas")
            for change in pair["diffs"][:5]:
                path = "/".join(map(str, change["path"]))
                print(f"    {path}: {change['kind']}, "
                      f"expected {change.get('expected')!r}, actual {change.get('actual')!r}", file=sys.stderr)
    if "error" in report:
        print(report["error"], file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], epilog=SCOPE)
    parser.add_argument("--fixture", help="compare only the named snapshot fixture")
    parser.add_argument("--report", type=Path, help="write the comparison report as JSON")
    parser.add_argument("--worker", choices=INTERFACES, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker is not None:
        print(json.dumps(run_worker(args.worker, json.load(sys.stdin)), allow_nan=False))
        return 0

    from run_examples import MANIFEST, environment_block, installed
    from run_fixtures import CATALOG, FIXTURE_ROOT, json_bytes, read_json, validate_catalog, write_atomic

    if args.report:
        args.report = args.report.resolve()
        if args.report.is_relative_to(FIXTURE_ROOT) or args.report == CATALOG:
            parser.error("--report must be outside the fixture tree and fixture catalog")

    print(SCOPE, flush=True)
    environment = {**environment_block(), "opendssdirect_version": installed("opendssdirect.py")}
    report = {"scope": SCOPE, "environment": environment, "fixtures": [], "status": "fail"}
    try:
        pin = read_json(MANIFEST)["support_targets"]["opendssdirect_py"]
        if environment["opendssdirect_version"] != pin:
            raise ValueError(f"Expected OpenDSSDirect.py {pin}, observed {environment['opendssdirect_version']!r}")
        records = validate_catalog(read_json(CATALOG))
        if args.fixture and args.fixture not in records:
            raise ValueError(f"Unknown fixture {args.fixture!r}. Available: {', '.join(sorted(records))}")
        selected = [records[args.fixture]] if args.fixture else records.values()
        report["fixtures"] = [compare_fixture(record, environment) for record in selected]
        if all(fixture["status"] == "pass" for fixture in report["fixtures"]):
            report["status"] = "pass"
    except (KeyError, OSError, ValueError) as exc:
        report["error"] = str(exc)

    print_results(report)
    if args.report:
        try:
            write_atomic(args.report, json_bytes(report))
        except OSError as exc:
            print(f"Could not write report: {exc}", file=sys.stderr)
            return 1
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
