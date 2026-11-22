#!/usr/bin/env python3
"""Check pinned IEEE snapshot fixtures or generate an approved golden revision."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from altdss import altdss
from dss import DSSException
from dss.enums import ControlModes, SolveModes
from jsonschema import Draft202012Validator, FormatChecker

from run_examples import LIBRARY_ROOT, environment_block, expected_targets

REPO_ROOT = LIBRARY_ROOT.parent
FIXTURE_ROOT = LIBRARY_ROOT / "examples/fixtures"
CATALOG = LIBRARY_ROOT / "references/fixtures.json"
SCHEMA = LIBRARY_ROOT / "schemas/catalogs/fixtures.schema.json"
SOURCE_INDEX = LIBRARY_ROOT / "references/sources.json"
GENERATOR_COMMAND = "tools/run_fixtures.py --update-golden"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def reject_constant(value):
    raise ValueError(f"Invalid JSON number: {value}")


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes {root}: {relative}")
    return path


def validate_catalog(records):
    validator = Draft202012Validator(read_json(SCHEMA), format_checker=FormatChecker())
    error = next(validator.iter_errors(records), None)
    if error is not None:
        raise ValueError(f"fixtures.json {error.json_path}: {error.message}")
    source_ids = {source["id"] for source in read_json(SOURCE_INDEX)}
    by_id = {}
    for record in records:
        fixture_id = record["fixture_id"]
        if fixture_id in by_id:
            raise ValueError(f"Duplicate fixture ID: {fixture_id}")
        unknown = set(record["source_ids"]) - source_ids
        if unknown:
            raise ValueError(f"{fixture_id}: unknown source IDs: {', '.join(sorted(unknown))}")
        revisions = [entry["revision"] for entry in record["golden_updates"]]
        current = record["golden_revision"]
        if revisions not in (list(range(1, current + 1)), list(range(1, current + 2))):
            raise ValueError(f"{fixture_id}: expected ordered approval history and at most one pending revision")
        expected_golden = f"examples/fixtures/{fixture_id}/golden.json"
        if record["golden_path"] != expected_golden:
            raise ValueError(f"{fixture_id}: golden_path must be {expected_golden}")
        by_id[fixture_id] = record
    return by_id


def verify_stack(record, environment):
    pins = record["engine_versions"]
    mappings = (
        ("altdss", "altdss_python", "altdss_version"),
        ("dss-python", "dss_python", "dss_python_version"),
        ("dss-python-backend", "dss_python_backend", "backend_version"),
    )
    targets = expected_targets()
    for package, pin_key, env_key in mappings:
        expected = pins[pin_key]
        actual = environment[env_key]
        if actual != expected or expected != targets[package]:
            raise ValueError(f"{package}: installed {actual!r}, fixture {expected!r}, manifest {targets[package]!r}")
    manifest_capi = read_json(LIBRARY_ROOT / "manifest.json")["support_targets"]["dss_capi"]
    if pins["dss_capi"] != manifest_capi:
        raise ValueError(f"DSS C-API manifest target {manifest_capi!r} differs from fixture pin {pins['dss_capi']!r}")


def verified_bytes(root, record):
    path = checked_path(root, record["path"])
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    if len(data) != record["bytes"] or digest != record["sha256"]:
        raise ValueError(
            f"Checksum mismatch for {path}: expected {record['bytes']} bytes and {record['sha256']}, "
            f"observed {len(data)} bytes and {digest}"
        )
    return data


def checked_inputs(record):
    verified_bytes(LIBRARY_ROOT, record["license"])
    base = checked_path(FIXTURE_ROOT, record["fixture_id"])
    files = {}
    for entry in record["files"]:
        path = entry["path"]
        if path in files:
            raise ValueError(f"Duplicate fixture file: {path}")
        files[path] = verified_bytes(base, entry)
    if record["entry_script"] not in files:
        raise ValueError("Entry script is missing from the checksummed file list")
    return files


def configure_snapshot(solution, settings):
    options = {
        "Mode": SolveModes[settings["mode"]],
        "MaxIterations": settings["max_iterations"],
        "Tolerance": settings["tolerance"],
        "ControlMode": ControlModes[settings["control_mode"]],
        "MaxControlIterations": settings["max_control_iterations"],
        "Frequency": settings["base_freq"],
    }
    # Writing Mode again can reinitialize a solution the entry script already ran.
    for attribute, expected in options.items():
        if getattr(solution, attribute) != expected:
            setattr(solution, attribute, expected)
        if getattr(solution, attribute) != expected:
            raise ValueError(f"DSS did not apply solver option {attribute}={expected!r}")
    return {
        "mode": solution.Mode.name,
        "max_iterations": solution.MaxIterations,
        "tolerance": solution.Tolerance,
        "control_mode": solution.ControlMode.name,
        "max_control_iterations": solution.MaxControlIterations,
        "base_freq": solution.Frequency,
    }


def power_pair(power, scale=1.0):
    return [float(power.real) * scale, float(power.imag) * scale]


def bus_readback(bus):
    nodes = [int(node) for node in bus.Nodes]
    values = bus.puVMagAngle
    if len(values) != 2 * len(nodes):
        raise ValueError(f"{bus.Name}: voltage array does not match bus nodes")
    return {
        "nodes": nodes,
        "pu_vmag": [float(value) for value in values[::2]],
        "pu_vangle_deg": [float(value) for value in values[1::2]],
    }


def collect_snapshot(ctx):
    solution = ctx.Solution
    if not solution.Converged:
        raise ValueError(f"Snapshot did not converge after {solution.TotalIterations} total iterations")
    load = sum(complex(power) for element in ctx.Load for power in element.TotalPowers())
    source = ctx.TotalPower()
    losses = ctx.Losses()
    buses = {bus.Name: bus_readback(bus) for bus in ctx.Bus}
    elements = {
        element.FullName(): {
            "powers_kw_kvar": [power_pair(power) for power in element.TotalPowers()],
            "losses_kw_kvar": power_pair(element.Losses(), scale=0.001),
        }
        for element in ctx.Element
    }
    controls = {reg.FullName(): {"tap": reg.TapNum} for reg in ctx.RegControl}
    controls.update({cap.FullName(): {"states": [int(state) for state in cap.States]} for cap in ctx.Capacitor})
    if len(buses) != ctx.NumBuses or len(elements) != ctx.NumCircuitElements:
        raise ValueError("Duplicate or missing names in the solved bus or element collection")
    return {
        "solution": {
            "converged": True,
            "iterations": solution.Iterations,
            "total_iterations": solution.TotalIterations,
            "control_iterations": solution.ControlIterations,
        },
        "totals": {
            "load_kw": load.real,
            "load_kvar": load.imag,
            "losses_kw": losses.real * 0.001,
            "losses_kvar": losses.imag * 0.001,
            "source_kw": source.real,
            "source_kvar": source.imag,
        },
        "buses": buses,
        "elements": elements,
        "controls": controls,
    }


def run_snapshot(record, approval, environment):
    verify_stack(record, environment)
    files = checked_inputs(record)
    # Preserve the full redirect closure and isolate any engine output from the repository.
    with TemporaryDirectory(prefix="dss-fixture-") as directory:
        root = Path(directory)
        for relative, data in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        ctx = altdss.NewContext()
        version = record["engine_versions"]["dss_capi"]
        if f"DSS C-API Library version {version} " not in ctx.Version():
            raise ValueError(f"Loaded DSS C-API library does not match fixture pin {version!r}")
        entry = root / record["entry_script"]
        ctx.Commands(f'Redirect "{entry.as_posix()}"')
        solver = configure_snapshot(ctx.Solution, record["solver"])
        if any(source.BaseFreq != solver["base_freq"] for source in ctx.Vsource):
            raise ValueError("Source base frequency differs from the snapshot solve frequency")
        ctx.Solution.Solve()
        snapshot = collect_snapshot(ctx)
    return {
        "fixture": record["fixture_id"],
        "scenario": "snapshot",
        "golden_revision": approval["revision"],
        "revision_date": approval["date"],
        "source": {
            "repository": record["upstream_repository"],
            "commit": record["upstream_commit"],
            "retrieved": record["retrieved"],
            "license": record["license"],
            "files": record["files"],
        },
        "environment": environment,
        "solver": solver,
        **snapshot,
        "generated_by": GENERATOR_COMMAND,
        "update_reason": approval["reason"],
    }


def exact_or_close(expected, actual, path, tolerances):
    if type(expected) is not type(actual):
        return False
    if type(actual) is float:
        section = path[0] if path else ""
        if section == "buses" and len(path) >= 3:
            if path[2] == "pu_vmag":
                return math.isclose(expected, actual, rel_tol=0, abs_tol=tolerances["voltage_pu_abs"])
            if path[2] == "pu_vangle_deg":
                return math.isclose(expected, actual, rel_tol=0, abs_tol=tolerances["angle_deg_abs"])
        if section in ("elements", "totals"):
            return math.isclose(expected, actual, rel_tol=tolerances["power_rel"],
                                abs_tol=tolerances["power_kw_kvar_abs"])
    return expected == actual


def compare(expected, actual, tolerances, path=()):
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(expected.keys() - actual.keys()):
            yield {"path": [*path, key], "kind": "missing", "expected": expected[key]}
        for key in sorted(actual.keys() - expected.keys()):
            yield {"path": [*path, key], "kind": "extra", "actual": actual[key]}
        for key in sorted(expected.keys() & actual.keys()):
            # Python/platform drift is visible in the report. Backend and wrapper pins remain exact.
            if path == ("environment",) and key in ("python_version", "platform"):
                continue
            yield from compare(expected[key], actual[key], tolerances, (*path, key))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            yield {"path": list(path), "kind": "length", "expected": len(expected), "actual": len(actual)}
        for i, (old, new) in enumerate(zip(expected, actual)):
            yield from compare(old, new, tolerances, (*path, i))
    elif not exact_or_close(expected, actual, path, tolerances):
        yield {"path": list(path), "kind": "value", "expected": expected, "actual": actual}


def summarize(snapshot):
    lowest, bus = min((value, name) for name, entry in snapshot["buses"].items() for value in entry["pu_vmag"])
    return {
        **snapshot["solution"],
        "buses": len(snapshot["buses"]),
        "elements": len(snapshot["elements"]),
        "lowest_pu_bus": bus,
        "lowest_pu_voltage": lowest,
    }


def require_clean_inputs():
    status = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all", "--", str(FIXTURE_ROOT.relative_to(REPO_ROOT))],
        check=True, capture_output=True, text=True,
    )
    if status.stdout:
        raise ValueError(f"Golden update requires committed, clean fixture files:\n{status.stdout.rstrip()}")


def golden_approval(record, reason):
    current = record["golden_revision"]
    updates = record["golden_updates"]
    if reason is None:
        if current == 0:
            raise ValueError("No recorded golden revision. Run an approved initial golden update.")
        return updates[current - 1]
    if len(updates) != current + 1 or updates[-1]["reason"] != reason:
        raise ValueError(f"Record owner approval for revision {current + 1} with the exact --reason before updating")
    return updates[-1]


def write_atomic(path, data):
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix="." + path.name, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_update(catalog, catalog_before, changes):
    # Publish all selected results only after every solver run and input check succeeded.
    outputs = [(path, json_bytes(snapshot)) for _, path, snapshot in changes]
    for record, _, snapshot in changes:
        record["golden_revision"] = snapshot["golden_revision"]
    catalog_data = (json.dumps(catalog, indent=2, allow_nan=False) + "\n").encode("utf-8")
    lock = CATALOG.with_suffix(".json.lock")
    with lock.open("x"):
        pass
    try:
        require_clean_inputs()
        if CATALOG.read_bytes() != catalog_before:
            raise ValueError("Fixture catalog changed while the golden update was running")
        written = []
        try:
            for path, data in [*outputs, (CATALOG, catalog_data)]:
                previous = path.read_bytes() if path.exists() else None
                write_atomic(path, data)
                written.append((path, previous))
        except OSError:
            for path, previous in reversed(written):
                if previous is None:
                    path.unlink()
                else:
                    write_atomic(path, previous)
            raise
    finally:
        lock.unlink()


def run(args, report):
    if args.update_golden:
        require_clean_inputs()
    catalog_before = CATALOG.read_bytes()
    catalog = json.loads(catalog_before.decode("utf-8"), parse_constant=reject_constant)
    by_id = validate_catalog(catalog)
    if args.fixture and args.fixture not in by_id:
        raise ValueError(f"Unknown fixture {args.fixture!r}. Available: {', '.join(sorted(by_id))}")
    selected = [by_id[args.fixture]] if args.fixture else catalog
    changes = []
    for record in selected:
        result = {"fixture": record["fixture_id"], "status": "fail"}
        report["fixtures"].append(result)
        try:
            path = checked_path(LIBRARY_ROOT, record["golden_path"])
            approval = golden_approval(record, args.reason)
            current = record["golden_revision"]
            golden = read_json(path) if current else None
            if current and (not isinstance(golden, dict) or golden.get("golden_revision") != current):
                raise ValueError("Golden file revision differs from fixtures.json")
            if current == 0 and path.exists():
                raise ValueError("Unregistered golden file already exists")
            snapshot = run_snapshot(record, approval, report["environment"])
            json_bytes(snapshot)  # Reject nonfinite readbacks before comparing or reporting.
            result["summary"] = summarize(snapshot)
            if args.update_golden:
                changes.append((record, path, snapshot))
                result["status"] = "ready"
            else:
                result["golden_environment"] = golden["environment"]
                result["diffs"] = list(compare(golden, snapshot, record["tolerances"]))
                if not result["diffs"]:
                    result["status"] = "pass"
        except (DSSException, KeyError, OSError, ValueError) as exc:
            result["error"] = str(exc)
    if args.update_golden and all(result["status"] == "ready" for result in report["fixtures"]):
        write_update(catalog, catalog_before, changes)
        for result, (_, _, snapshot) in zip(report["fixtures"], changes, strict=True):
            result.update(status="pass", golden_revision=snapshot["golden_revision"])
    return all(result["status"] == "pass" for result in report["fixtures"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", help="run only the named fixture")
    parser.add_argument("--report", type=Path, help="write a machine-readable JSON diff")
    parser.add_argument("--update-golden", action="store_true", help="generate the recorded owner-approved revision")
    parser.add_argument("--reason", help="the exact reason recorded in fixtures.json for the next revision")
    args = parser.parse_args(argv)
    if args.update_golden and not (args.reason and args.reason.strip()):
        parser.error("--update-golden requires a nonblank --reason")
    if args.reason is not None and not args.update_golden:
        parser.error("--reason requires --update-golden")
    if args.report and (args.report.resolve().is_relative_to(FIXTURE_ROOT) or args.report.resolve() == CATALOG):
        parser.error("--report must be outside the fixture tree and fixture catalog")

    report = {"operation": "update" if args.update_golden else "compare",
              "environment": environment_block(), "fixtures": []}
    try:
        passed = run(args, report)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        report["error"] = str(exc)
        passed = False
    report["status"] = "pass" if passed else "fail"
    for result in report["fixtures"]:
        print(f"{result['status'].upper()} {result['fixture']}")
        if "summary" in result:
            s = result["summary"]
            print(f"  {s['buses']} buses, {s['elements']} elements, {s['total_iterations']} total iterations, "
                  f"{s['control_iterations']} control iterations, lowest {s['lowest_pu_bus']} at {s['lowest_pu_voltage']:.6f} pu")
        if "error" in result:
            print(f"  {result['error']}", file=sys.stderr)
        for diff in result.get("diffs", [])[:5]:
            print(f"  {'/'.join(map(str, diff['path']))}: {diff['kind']}, "
                  f"expected {diff.get('expected')!r}, actual {diff.get('actual')!r}", file=sys.stderr)
    if "error" in report:
        print(report["error"], file=sys.stderr)
    if args.report:
        try:
            write_atomic(args.report, json_bytes(report))
        except OSError as exc:
            print(f"Could not write report: {exc}", file=sys.stderr)
            return 1
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
