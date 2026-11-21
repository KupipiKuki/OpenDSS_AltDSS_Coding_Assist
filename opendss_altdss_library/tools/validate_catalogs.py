#!/usr/bin/env python3
"""Validate the library manifest and every catalog against its JSON Schema.

Usage (from the repository root, with the validation environment active):

    python opendss_altdss_library/tools/validate_catalogs.py

Exit code 0 when every pair passes, 1 otherwise. Every manifest catalog must
have a declared schema pairing here; adding a catalog without a schema fails
the run on purpose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError as exc:  # pragma: no cover - environment guard
    sys.exit(
        f"Missing validation dependency ({exc}). Install with:\n"
        "  python -m pip install -r tools/requirements-validation.txt"
    )

LIBRARY_ROOT = Path(__file__).resolve().parent.parent

# Catalog file (relative to the library root) -> schema file (relative to root).
SCHEMA_PAIRS = {
    "manifest.json": "schemas/catalogs/manifest.schema.json",
    "references/lines/opendss_line_linecode_properties.json": (
        "schemas/catalogs/line_linecode_properties.schema.json"
    ),
    "references/line_linecode_sources.json": (
        "schemas/catalogs/line_linecode_sources.schema.json"
    ),
    "references/examples.json": "schemas/catalogs/examples.schema.json",
    "references/opendss_objects.json": "schemas/catalogs/opendss_objects.schema.json",
    "references/altdss_python_api.json": "schemas/catalogs/altdss_python_api.schema.json",
    "references/dss_capi.json": "schemas/catalogs/dss_capi.schema.json",
    "references/python_interface_comparison.json": (
        "schemas/catalogs/python_interface_comparison.schema.json"
    ),
    "references/troubleshooting.json": "schemas/catalogs/troubleshooting.schema.json",
}


def build_registry(root: Path) -> Registry:
    """Register every schema under schemas/ so relative $refs resolve."""
    registry = Registry()
    for path in sorted((root / "schemas").rglob("*.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        registry = registry.with_resource(path.as_uri(), resource)
    return registry


def main() -> int:
    root = LIBRARY_ROOT
    registry = build_registry(root)
    checker = FormatChecker()

    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    declared = [
        entry
        for section in manifest.get("catalogs", {}).values()
        for entry in section
    ]

    failures = 0
    results: list[tuple[str, bool, str]] = []

    for target, schema_rel in SCHEMA_PAIRS.items():
        target_path = root / target
        if not target_path.exists():
            results.append((target, False, "missing catalog file"))
            failures += 1
            continue
        try:
            instance = json.loads(target_path.read_text(encoding="utf-8"))
            schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))
            validator = Draft202012Validator(
                schema, registry=registry, format_checker=checker
            )
            errors = sorted(
                validator.iter_errors(instance), key=lambda e: list(e.absolute_path)
            )
        except Exception as exc:  # schema load or reference resolution failed
            results.append((target, False, f"{type(exc).__name__}: {exc}"))
            failures += 1
            continue
        if errors:
            detail = "; ".join(
                f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
                for e in errors[:5]
            )
            more = f" (+{len(errors) - 5} more)" if len(errors) > 5 else ""
            results.append((target, False, detail + more))
            failures += 1
        else:
            count = len(instance) if isinstance(instance, list) else 1
            results.append((target, True, f"{count} record(s)"))

    # Every catalog declared in the manifest must be schema-paired and present.
    unpinned = [entry for entry in declared if entry not in SCHEMA_PAIRS]
    missing = [entry for entry in declared if not (root / entry).exists()]

    print("Schema validation")
    print("=================")
    for target, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {target}  ({detail})")

    if unpinned:
        print("\nFAIL  manifest catalogs without a schema pairing:")
        for entry in unpinned:
            print(f"      {entry}")
        failures += len(unpinned)

    if missing:
        print("\nFAIL  manifest catalogs missing on disk:")
        for entry in missing:
            print(f"      {entry}")
        failures += len(missing)

    passed = sum(1 for _, ok, _ in results if ok)
    print()
    print(f"{passed}/{len(results)} schema pairs passed")
    print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures} problem(s))")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
