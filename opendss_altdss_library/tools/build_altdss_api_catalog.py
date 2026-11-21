#!/usr/bin/env python3
"""Build the AltDSS-Python API catalog from a pinned source tree.

Usage (from the repository root):

    python tools/build_altdss_api_catalog.py --source-dir /path/to/altdss --out references/altdss_python_api.json

The source directory must contain the ``altdss`` package modules for the pinned
version (extract the wheel from PyPI, for example ``altdss==0.2.4``). The script
parses the modules with the standard library ``ast`` module; it never imports
the package, so nothing is executed.

Records contain the object classes that subclass ``DSSObj`` plus the ``AltDSS``
context class. Properties come from the class bodies (``X = property(...)``)
with type hints from ``# type:`` comments or the matching ``*Properties``
TypedDict. Methods are limited to ``new``, ``batch_new``, and ``edit`` on object
classes, and public methods/properties on the context class.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

TARGET_VERSION = "0.2.4"
METHOD_NAMES = {"new", "batch_new", "edit"}
SKIP_MODULES = {"__init__.py", "enums.py", "_version.py", "types.py", "common.py"}


def doc_text(node: ast.AST) -> str | None:
    text = ast.get_docstring(node)
    if not text:
        return None
    return text.strip()


def summary(text: str | None, limit: int | None = None) -> str | None:
    """First paragraph or sentence of a docstring, with parameter lists removed."""
    if not text:
        return None
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(":param") or stripped.startswith(":return"):
            break
        if stripped:
            lines.append(stripped)
        elif lines:
            break
    if not lines:
        return None
    result = " ".join(lines)
    if limit:
        result = result[:limit].rstrip()
    return result or None


def clean_property_doc(text: str | None) -> str | None:
    if not text:
        return None
    keep = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("DSS property name:"):
            continue
        keep.append(stripped)
    return " ".join(keep) or None


def unparse_signature(node: ast.FunctionDef) -> str:
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"def {node.name}({args}){returns}"


def typed_dict_types(tree: ast.Module, class_name: str) -> dict[str, str]:
    """Return ordered {property: type} from <class_name>Properties if present."""
    target = f"{class_name}Properties"
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == target:
            out: dict[str, str] = {}
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    out[item.target.id] = ast.unparse(item.annotation)
            return out
    return {}


def parse_object_class(node: ast.ClassDef, tree: ast.Module, module: str) -> dict | None:
    dss_class = None
    for item in node.body:
        if (
            isinstance(item, ast.Assign)
            and len(item.targets) == 1
            and isinstance(item.targets[0], ast.Name)
            and item.targets[0].id == "_cls_name"
            and isinstance(item.value, ast.Constant)
        ):
            dss_class = item.value.value

    types = typed_dict_types(tree, node.name)
    properties: list[dict] = []
    methods: list[dict] = []

    body = node.body
    for index, item in enumerate(body):
        if isinstance(item, ast.Assign) and len(item.targets) == 1:
            target = item.targets[0]
            if (
                isinstance(target, ast.Name)
                and isinstance(item.value, ast.Call)
                and isinstance(item.value.func, ast.Name)
                and item.value.func.id == "property"
            ):
                if target.id.endswith("_str"):
                    continue  # internal string proxy for object-reference properties
                description = None
                if index + 1 < len(body):
                    nxt = body[index + 1]
                    if isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant):
                        if isinstance(nxt.value.value, str):
                            description = clean_property_doc(nxt.value.value)
                prop = {
                    "name": target.id,
                    "evidence_label": "Official-versioned",
                }
                type_hint = item.type_comment or types.get(target.id)
                if type_hint:
                    prop["type_hint"] = type_hint
                if description:
                    prop["description"] = description
                properties.append(prop)
        elif isinstance(item, ast.FunctionDef) and item.name in METHOD_NAMES:
            method = {
                "name": item.name,
                "signature": unparse_signature(item),
                "evidence_label": "Official-versioned",
            }
            text = summary(doc_text(item))
            if text:
                method["description"] = text
            if item.name == "batch_new":
                method["batch_behavior"] = (
                    "Creates a batch of objects from names, count, or a dataframe. "
                    "Array properties align with the batch order; scalar properties apply to every object."
                )
            elif item.name == "new":
                method["batch_behavior"] = "Creates one object; the name is a required positional argument."
            methods.append(method)

    if not properties and not methods:
        return None

    description = summary(doc_text(node))
    if not description:
        description = f"Wrapper for the DSS {dss_class or node.name} object."
    record = {
        "module_path": f"altdss.{module}",
        "class_name": node.name,
        "target_version": TARGET_VERSION,
        "description": description,
        "methods": methods,
        "properties": properties,
        "evidence_label": "Official-versioned",
    }
    if dss_class:
        record["dss_class_name"] = dss_class
    return record


def parse_context_class(node: ast.ClassDef, module: str) -> dict:
    methods: list[dict] = []
    properties: list[dict] = []
    for item in node.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if item.name.startswith("_"):
            continue
        decorators = {ast.unparse(d) for d in item.decorator_list}
        if "property" in decorators:
            prop = {"name": item.name, "evidence_label": "Official-versioned"}
            if item.returns:
                prop["type_hint"] = ast.unparse(item.returns)
            text = summary(doc_text(item))
            if text:
                prop["description"] = text
            properties.append(prop)
        else:
            method = {
                "name": item.name,
                "signature": unparse_signature(item),
                "evidence_label": "Official-versioned",
            }
            text = summary(doc_text(item))
            if text:
                method["description"] = text
            methods.append(method)
    return {
        "module_path": f"altdss.{module}",
        "class_name": node.name,
        "target_version": TARGET_VERSION,
        "description": summary(doc_text(node)) or "AltDSS engine context.",
        "methods": methods,
        "properties": properties,
        "evidence_label": "Official-versioned",
    }


def parse_collection_class(node: ast.ClassDef, module: str) -> dict:
    """Collection interface class (``I<Name>``) that exposes the context member."""
    methods: list[dict] = []
    for item in node.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if item.name in {"new", "batch_new"}:
            method = {
                "name": item.name,
                "signature": unparse_signature(item),
                "evidence_label": "Official-versioned",
            }
            text = summary(doc_text(item))
            if text:
                method["description"] = text
            if item.name == "batch_new":
                method["batch_behavior"] = (
                    "Creates a batch of objects from names, count, or a dataframe. "
                    "Array properties align with the batch order; scalar properties apply to every object."
                )
            else:
                method["batch_behavior"] = "Creates one object; the name is a required positional argument."
            methods.append(method)
    element = node.name[1:]
    return {
        "module_path": f"altdss.{module}",
        "class_name": node.name,
        "target_version": TARGET_VERSION,
        "description": (
            summary(doc_text(node))
            or f"Collection interface for {element} objects; the exported context member is altdss.{element}."
        ),
        "methods": methods,
        "properties": [],
        "evidence_label": "Official-versioned",
    }


def base_names(node: ast.ClassDef) -> set[str]:
    names = set()
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.add(base.id)
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path, help="Directory containing the altdss package modules")
    parser.add_argument("--out", required=True, type=Path, help="Output catalog path")
    args = parser.parse_args()

    source = args.source_dir
    if not source.is_dir():
        raise SystemExit(f"source directory not found: {source}")

    records: list[dict] = []
    for path in sorted(source.glob("*.py")):
        if path.name in SKIP_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), type_comments=True)
        module = path.stem
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bases = base_names(node)
            if "DSSObj" in bases:
                record = parse_object_class(node, tree, module)
                if record:
                    records.append(record)
            elif "IDSSObj" in bases and node.name.startswith("I"):
                records.append(parse_collection_class(node, module))
            elif node.name == "AltDSS":
                records.append(parse_context_class(node, module))

    records.sort(key=lambda r: (r["module_path"], r["class_name"]))
    args.out.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    n_props = sum(len(r["properties"]) for r in records)
    n_methods = sum(len(r["methods"]) for r in records)
    print(f"wrote {args.out} ({len(records)} classes, {n_props} properties, {n_methods} methods)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
