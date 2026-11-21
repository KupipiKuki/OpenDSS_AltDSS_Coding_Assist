#!/usr/bin/env python3
"""Execute catalogued example files with the pinned target stack.

Usage (from the repository root, with the validation environment active):

    python opendss_altdss_library/tools/run_examples.py

Reads references/examples.json, runs every record that names a ``file``, and
prints per-example output plus an environment block. Exit code 0 when every
example exits cleanly, 1 otherwise.

Recording policy: after a successful run, copy the environment block into the
example record (``environment``) and set ``execution_status`` and
``evidence_label`` to ``Observed-working``. Do not record a run you did not do.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

LIBRARY_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_CATALOG = LIBRARY_ROOT / "references" / "examples.json"
MANIFEST = LIBRARY_ROOT / "manifest.json"

# Generic driver for DSS text examples: compile the file in a fresh context and
# print a small readback so failures are visible in the captured output.
DSS_DRIVER = """
import sys
from pathlib import Path
from altdss import altdss

ctx = altdss.NewContext()
ctx.Commands(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("circuit elements:", ctx.NumCircuitElements)
print("lines:", len(ctx.Line), "linecodes:", len(ctx.LineCode))
for line in ctx.Line:
    print(f"line {line.Name}: bus1={line.Bus1} bus2={line.Bus2} length={line.Length}")
"""


def installed(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def environment_block() -> dict:
    return {
        "python_version": platform.python_version(),
        "altdss_version": installed("altdss"),
        "dss_python_version": installed("dss-python"),
        "backend_version": installed("dss-python-backend"),
        "platform": f"{platform.system()} {platform.release()} {platform.machine()}",
    }


def expected_targets() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    targets = manifest.get("support_targets", {})
    return {
        "altdss": targets.get("altdss_python"),
        "dss-python": targets.get("dss_python"),
        "dss-python-backend": targets.get("dss_python_backend"),
    }


def run_entry(entry: dict) -> tuple[bool, str]:
    file_rel = entry.get("file")
    if not file_rel:
        return True, "skipped (code snippet only)"
    path = LIBRARY_ROOT / file_rel
    if not path.exists():
        return False, f"missing file: {file_rel}"

    if entry.get("language") == "dss":
        cmd = [sys.executable, "-c", DSS_DRIVER, str(path)]
    else:
        cmd = [sys.executable, str(path)]

    proc = subprocess.run(
        cmd, cwd=LIBRARY_ROOT, capture_output=True, text=True, timeout=300
    )
    output = (proc.stdout or "").strip()
    error = (proc.stderr or "").strip()
    detail = output if proc.returncode == 0 else f"{output}\n{error}".strip()
    return proc.returncode == 0, detail


def main() -> int:
    entries = json.loads(EXAMPLES_CATALOG.read_text(encoding="utf-8"))
    env = environment_block()
    expected = expected_targets()

    print("Example execution")
    print("=================")
    failures = 0
    for entry in entries:
        ok, detail = run_entry(entry)
        status = entry.get("execution_status", "?")
        print(f"\n{'PASS' if ok else 'FAIL'}  {entry['example_id']}  (recorded: {status})")
        for line in detail.splitlines():
            print(f"      {line}")
        if not ok:
            failures += 1

    print("\nEnvironment")
    print("-----------")
    print(json.dumps(env, indent=1))

    drift = []
    for package, want in expected.items():
        have = installed(package)
        if want and have and have != want:
            drift.append(f"{package}: installed {have}, manifest target {want}")
    if drift:
        print("\nWARNING version drift against manifest support_targets:")
        for item in drift:
            print(f"      {item}")

    print()
    print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures} example(s))")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
