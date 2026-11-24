#!/usr/bin/env python3
"""Search the OpenDSS catalogs and verify the object index and symbol aliases."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import get_close_matches
import json
from pathlib import Path
import re
import sys


LIBRARY = Path(__file__).resolve().parent.parent
OBJECTS = "references/opendss_objects.json"
API = "references/altdss_python_api.json"
ENGINE = "references/dss_capi.json"
EXAMPLES = "references/examples.json"
SOURCES = "references/sources.json"
FIXTURES = "references/fixtures.json"
INTERFACES = "references/python_interface_comparison.json"
ISSUES = "references/troubleshooting.json"
ALIASES = "references/symbol_aliases.json"
EVIDENCE = (
    "Official-current", "Official-versioned", "Observed-working", "Observed-export",
    "Example-only", "Inferred", "Unverified",
)
VERSION_FIELDS = ("version_range", "version_or_ref", "target_versions", "target_version")


def strings(value):
    if isinstance(value, str):
        if value:
            yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


@dataclass
class Entry:
    catalog: str
    record_id: str
    record: dict
    concept_fields: tuple[str, ...]
    symbol_fields: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()
    citations: list[dict] = field(default_factory=list)
    versions: tuple[str, ...] = ()
    details: dict = field(default_factory=dict)
    kind: str = ""

    def __post_init__(self):
        self.versions = self.versions or tuple(
            value for key in VERSION_FIELDS for value in strings(self.record.get(key))
        )

    @property
    def evidence(self):
        return self.record.get("evidence_label") or self.record.get("evidence_level")

    def matches(self, symbol, tokens):
        if symbol is not None:
            for key in self.symbol_fields:
                for value in strings(self.record.get(key)):
                    if value.casefold() == symbol:
                        yield key, value
            return
        fields = [(key, " ".join(strings(self.record.get(key)))) for key in self.concept_fields]
        combined = " ".join(value for _, value in fields).casefold()
        if all(token in combined for token in tokens):
            if tokens:
                yield next((item for item in fields if any(token in item[1].casefold() for token in tokens)))
            else:
                yield fields[0]


def read_data(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


def in_tree(root, path):
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path escapes {root}: {path}")
    return resolved


def citation(url, tag=None, date=None):
    return {"source_url": url, "tag": tag, "accessed": date}


class Corpus:
    def __init__(self, checking=False):
        self.objects = read_data(LIBRARY / OBJECTS)
        references = LIBRARY / "references"
        paths = {path.relative_to(LIBRARY).as_posix() for path in references.glob("*/*_properties.json")}
        linked_paths = {
            row["property_catalog"]["path"] for row in self.objects if row["property_catalog"] is not None
        }
        if not checking:
            paths.update(linked_paths)
        self.properties = {
            path: read_data(in_tree(references, Path(path).relative_to("references"))) for path in sorted(paths)
        }
        self.files = {OBJECTS: self.objects}
        self.files.update({path: read_data(LIBRARY / path) for path in ADAPTERS if path != OBJECTS})
        self.aliases = read_data(LIBRARY / ALIASES)
        self.sources = {row["id"]: row for row in self.files[SOURCES]}
        self.by_class = {row["element_class"].casefold(): row for row in self.objects}
        self.by_url = defaultdict(list)
        for row in self.files[SOURCES]:
            self.by_url[row["url"].split("#", 1)[0]].append(row)
        self.by_module = defaultdict(list)
        self.by_namespace = defaultdict(list)
        for row in self.objects:
            name = row["element_class"]
            if row["altdss"]:
                self.by_module[row["altdss"]["class_record"]].append(name)
            for namespace in row["engine"]["namespaces"]:
                self.by_namespace[namespace].append(name)

    def source_ids(self, ids):
        return [
            citation(row["url"], row.get("version_or_ref"), row.get("accessed"))
            for key in ids if (row := self.sources.get(key)) is not None
        ]

    def refs(self, refs, local=()):
        result = []
        for url in refs:
            base = url.split("#", 1)[0]
            candidates = [
                row for row in local if row["url"].split("#", 1)[0] == base
            ] + self.by_url[base]
            exact = next((row for row in candidates if row["url"] == url), {})
            meta = exact or (candidates[0] if candidates else {})
            pin = re.search(r"/(?:blob|tree|tag)/([^/]+)", base)
            result.append(citation(url, pin[1] if pin else meta.get("version_or_ref"), meta.get("accessed")))
        return result

    def text_classes(self, record, fields):
        words = set(re.findall(r"[a-z0-9]+", " ".join(
            value for key in fields for value in strings(record.get(key))
        ).casefold()))
        return tuple(self.by_class[key]["element_class"] for key in self.by_class if key in words)

    def entries(self):
        for path, adapter in ADAPTERS.items():
            for row in self.files[path]:
                yield from adapter(self, path, row)
        for path, rows in self.properties.items():
            for row in rows:
                yield from property_entries(self, path, row)

    def stats(self):
        api = self.files[API]
        elements = sum(map(len, self.properties.values()))
        properties = sum(len(row["properties"]) for rows in self.properties.values() for row in rows)
        counts = {path: len(rows) for path, rows in self.files.items()}
        counts.update({path: len(rows) for path, rows in self.properties.items()})
        methods = sum(len(row["methods"]) for row in api)
        api_properties = sum(len(row["properties"]) for row in api)
        addressable = sum(counts.values()) + properties
        return {
            "files": len(counts), "catalogs": counts, "element_classes": elements,
            "element_property_rows": properties, "api_methods": methods, "api_properties": api_properties,
            "addressable_records": addressable, "searchable_records": addressable + methods + api_properties,
        }


def source_entries(corpus, path, row):
    fields = ("title", "topics", "scope", "id", "kind", "publisher")
    yield Entry(path, row["id"], row, fields, classes=corpus.text_classes(row, fields),
                citations=corpus.source_ids([row["id"]]))


def example_entries(corpus, path, row):
    yield Entry(path, row["example_id"], row,
                ("task_description", "expected_result", "object_classes", "example_id"),
                classes=tuple(row["object_classes"]), citations=corpus.source_ids(row.get("source_ids", [])),
                details={"file": row.get("file")})


def api_entries(corpus, path, row):
    module = row["module_path"]
    key = f'{module}:{row["class_name"]}'
    common = dict(classes=tuple(corpus.by_module[module]),
                  citations=corpus.source_ids(["altdss-python-024-tree"]),
                  versions=tuple(strings(row.get("target_version"))))
    yield Entry(path, key, row, ("class_name", "description", "module_path"), ("class_name",), **common)
    for group, kind in (("methods", "api_method"), ("properties", "api_property")):
        for member in row[group]:
            yield Entry(path, f'{key}.{member["name"]}', member,
                        ("name", "description", "signature", "type_hint"), ("name",), **common, kind=kind)


def record_source(row):
    source = row.get("source", {})
    if not source.get("url_or_path"):
        return []
    return [{
        **citation(source["url_or_path"], row.get("version_range"), source.get("accessed_or_captured")),
        "section": source.get("section_or_record"),
    }]


def engine_entries(corpus, path, row):
    namespace = row["namespace_or_type"]
    yield Entry(path, row["id"], row,
                ("name", "namespace_or_type", "signature_or_shape", "arguments",
                 "returns_or_effects", "errors_or_edge_cases", "notes", "id"),
                ("name",), tuple(corpus.by_namespace[namespace]), record_source(row),
                details={"namespace": namespace})


def issue_entries(corpus, path, row):
    fields = ("title", "symptom", "cause", "safe_fix", "diagnostic_evidence", "notes", "id")
    yield Entry(path, row["id"], row, fields,
                classes=corpus.text_classes(row, (*fields, "source")), citations=record_source(row))


def interface_entries(corpus, path, row):
    fields = ("opendss_concept", "dss_text_command", "interfaces", "notes")
    yield Entry(path, row["opendss_concept"], row, fields, classes=corpus.text_classes(row, fields),
                citations=corpus.refs(row["source_refs"]))


def object_entries(corpus, path, row):
    name = row["element_class"]
    yield Entry(path, name, row, ("element_class", "status", "notes", "fixture_usage"),
                ("element_class",), (name,), corpus.source_ids(row["source_ids"]),
                details={key: row[key] for key in ("status", "property_catalog", "workflow_path", "altdss",
                                                   "engine", "example_ids", "readback_evidence", "fixture_usage")})


def fixture_entries(corpus, path, row):
    key = row["fixture_id"]
    classes = tuple(obj["element_class"] for obj in corpus.objects
                    if any(run.startswith(key + " ") for run in obj["fixture_usage"]))
    yield Entry(path, key, row, ("name", "fixture_id", "notes", "entry_script"),
                classes=classes, citations=[citation(row["upstream_repository"], row["upstream_commit"], row["retrieved"])],
                details={"golden_path": row["golden_path"]})


def property_entries(corpus, path, row):
    name = row["element_class"]
    local = row.get("sources", [])
    class_refs = corpus.refs([source["url"] for source in local], local)
    class_versions = tuple(strings(row.get("target_versions")))
    yield Entry(path, name, row, ("element_class", "altdss_mapping", "notes"), ("element_class",),
                (name,), class_refs)
    for prop in row["properties"]:
        refs = corpus.refs(prop.get("source_refs", []), local)
        yield Entry(path, f'{name}.{prop["name"]}', prop,
                    ("name", "altdss_keyword", "description", "units", "data_type", "notes"),
                    ("name", "altdss_keyword"), (name,), refs or class_refs, class_versions,
                    details={"dss": prop["name"], "python": prop.get("altdss_keyword")}, kind="element_property")


ADAPTERS = {
    SOURCES: source_entries, EXAMPLES: example_entries, API: api_entries,
    ENGINE: engine_entries, OBJECTS: object_entries, INTERFACES: interface_entries,
    ISSUES: issue_entries, FIXTURES: fixture_entries,
}


def hit(entry, key, value):
    primary = entry.citations[0] if entry.citations else citation(None)
    return {
        "catalog": entry.catalog, "record_id": entry.record_id, "field": key, "value": value,
        "evidence": entry.evidence, "version": list(entry.versions) or "unstated",
        **primary, "citations": entry.citations, **entry.details,
    }


def search(corpus, args, object_record):
    symbol = args.symbol.casefold() if args.symbol else None
    alias = next((row for row in corpus.aliases if row["alias"].casefold() == symbol), None)
    tokens = args.query.casefold().split() if args.query else []
    matches = []
    for entry in corpus.entries():
        if object_record:
            if object_record["element_class"] not in entry.classes:
                continue
            if not (symbol or tokens) and object_record["status"] == "deferred" and entry.catalog != OBJECTS:
                continue
        if args.version and entry.versions and not any(args.version.casefold() in v.casefold() for v in entry.versions):
            continue
        if args.evidence and entry.evidence != args.evidence:
            continue
        fields = list(entry.matches(symbol, tokens))
        # One hit per record. The fields array preserves both exact keyword matches.
        if fields:
            result = hit(entry, *fields[0])
            if len(fields) > 1:
                result["matched_fields"] = [key for key, _ in fields]
            matches.append((entry, result))
        elif alias and entry.record_id in alias["record_ids"] and alias["element_class"] in entry.classes:
            result = hit(entry, "alias", args.symbol)
            result["canonical_symbol"] = alias["canonical"]
            result["alias_sources"] = corpus.source_ids(alias["source_ids"])
            matches.append((entry, result))
    if symbol:
        matches = combine_keyword_matches(matches)
    return sorted((result for _, result in matches), key=lambda r: (r["catalog"], r["record_id"], r["field"]))


def combine_keyword_matches(matches):
    # Carry the generated accessor citation on a dual-spelling property hit.
    keywords = {
        f'{entry.classes[0]}.{result["python"]}': result for entry, result in matches
        if entry.kind == "element_property" and result["python"]
        and result["dss"].casefold() != result["python"].casefold()
    }
    retained = []
    for entry, result in matches:
        if entry.kind == "api_property":
            owner, _, prop = entry.record_id.partition(":")[2].rpartition(".")
            linked = keywords.get(f"{owner}.{prop}")
            if linked is not None:
                linked.setdefault("related_api", []).append(result)
                continue
        retained.append((entry, result))
    return retained


def fixture_classes(fixtures):
    scenarios = {}
    for row in fixtures:
        key = row["fixture_id"]
        entry_path = Path("examples/fixtures") / key / row["entry_script"]
        text = in_tree(LIBRARY, entry_path).read_text(encoding="utf-8")
        commands = re.sub(r"!.*", "", text)
        auxiliary = set()
        if re.search(r"^\s*new\s+(?:object\s*=\s*)?circuit\.", commands, re.M | re.I):
            auxiliary.add("Circuit")
        if re.search(r"\blinecode\s*=", commands, re.I):
            auxiliary.add("LineCode")
        snapshot = read_data(in_tree(LIBRARY, row["golden_path"]))
        scenarios[key + " snapshot"] = auxiliary | {name.partition(".")[0] for name in snapshot["elements"]}
        if daily := row.get("daily"):
            golden = read_data(in_tree(LIBRARY, daily["golden_path"]))
            assigned = {"LoadShape"} if daily["shape"]["assignment"] == "Load.daily" else set()
            elements = {name.partition(".")[0] for name in golden["peak_step"]["elements"]}
            scenarios[key + " daily"] = auxiliary | assigned | elements
    return scenarios


def check_index(corpus):
    errors = []
    engine = Counter(row["namespace_or_type"] for row in corpus.files[ENGINE])
    scenarios = fixture_classes(corpus.files[FIXTURES])

    def expect(name, key, actual, expected):
        if actual != expected:
            errors.append(f"{name}.{key}: recorded {actual!r}, derived {expected!r}")

    for row in corpus.objects:
        name = row["element_class"]
        if linked := row["property_catalog"]:
            records = corpus.properties.get(linked["path"])
            if records is None:
                errors.append(f'{name}.property_catalog.path: {linked["path"]!r} does not resolve')
            else:
                if name not in {record["element_class"] for record in records}:
                    errors.append(f'{name}.property_catalog.path: {linked["path"]} has no {name} record')
                expect(name, "property_catalog.record_count", linked["record_count"], len(records))
                expect(name, "property_catalog.property_row_count", linked["property_row_count"],
                       sum(len(record["properties"]) for record in records))
        for ns in row["engine"]["namespaces"]:
            if ns not in engine:
                errors.append(f"{name}.engine.namespaces: {ns!r} does not resolve")
        expect(name, "engine.record_count", row["engine"]["record_count"],
               sum(engine[ns] for ns in row["engine"]["namespaces"]))
        expect(name, "example_ids", sorted(row["example_ids"]),
               sorted(ex["example_id"] for ex in corpus.files[EXAMPLES] if name in ex["object_classes"]))
        expect(name, "fixture_usage", sorted(row["fixture_usage"]),
               sorted(run for run, classes in scenarios.items() if name in classes))
        paths = [("workflow_path", row["workflow_path"])]
        paths.extend(("readback_evidence", path) for path in row["readback_evidence"])
        for key, path in paths:
            if path:
                try:
                    exists = in_tree(LIBRARY.parent, path).is_file()
                except ValueError:
                    exists = False
                if not exists:
                    errors.append(f"{name}.{key}: {path!r} does not resolve")
        for source_id in row["source_ids"]:
            if source_id not in corpus.sources:
                errors.append(f"{name}.source_ids: {source_id!r} does not resolve")
        if row["epri_doc_url"] is not None and row["epri_doc_url"] not in {
            item["source_url"] for item in corpus.source_ids(row["source_ids"])
        }:
            errors.append(f"{name}.epri_doc_url: does not resolve through source_ids")
    return errors


def check_aliases(corpus):
    if not corpus.aliases:
        return [f"{ALIASES}: no aliases registered"]

    by_id = defaultdict(list)
    exact_symbols = set()
    for entry in corpus.entries():
        by_id[entry.record_id].append(entry)
        exact_symbols.update(value.casefold() for key in entry.symbol_fields
                             for value in strings(entry.record.get(key)))

    errors = []
    seen = set()
    for row in corpus.aliases:
        name = row["alias"]
        symbol = name.casefold()
        if symbol in seen:
            errors.append(f"{name}: duplicate alias")
        seen.add(symbol)
        if symbol in exact_symbols:
            errors.append(f"{name}: collides with an exact symbol")
        canonical = row["canonical"].casefold()
        signature_symbol = re.compile(rf"(?<!\w){re.escape(canonical)}(?!\w)")
        for record_id in row["record_ids"]:
            candidates = by_id.get(record_id, ())
            entries = [entry for entry in candidates if row["element_class"] in entry.classes]
            if not candidates:
                errors.append(f"{name}.record_ids: {record_id!r} does not resolve")
            elif not entries:
                errors.append(f"{name}.record_ids: {record_id!r} does not belong to {row['element_class']}")
            # Engine behavior records can carry the symbol in the signature instead of the name.
            elif not any(
                any(entry.matches(canonical, ()))
                or (entry.catalog == ENGINE and signature_symbol.search(
                    (entry.record.get("signature_or_shape") or "").casefold()
                ))
                for entry in entries
            ):
                errors.append(f"{name}.record_ids: {record_id!r} does not carry {row['canonical']!r}")
        for source_id in row["source_ids"]:
            if source_id not in corpus.sources:
                errors.append(f"{name}.source_ids: {source_id!r} does not resolve")
    return errors


def print_stats(stats):
    for name, count in sorted(stats["catalogs"].items()):
        print(f"{name}  {count}")
    print(f'{stats["element_classes"]} element classes / {stats["element_property_rows"]} property rows')
    print(f'{stats["api_methods"]} API methods / {stats["api_properties"]} API properties')
    print(f'{stats["addressable_records"]} addressable records across {stats["files"]} files '
          f'({stats["searchable_records"]} including API members)')


def print_hit(result):
    value = " ".join(result["value"].split())
    labels = []
    if "dss" in result:
        labels.append(f'dss={result["dss"]} python={result["python"] or "unstated"}')
    if "status" in result:
        labels.append(f'status: {result["status"]}')
        if result["property_catalog"]:
            labels.append(result["property_catalog"]["path"])
    if "canonical_symbol" in result:
        labels.append(f'canonical={result["canonical_symbol"]}')
    if result["version"] == "unstated":
        labels.append("version=unstated")
    suffix = "  " + "  ".join(labels) if labels else ""
    print(f'{result["catalog"]}  {result["record_id"]}  {result["field"]}={value}  '
          f'{result["source_url"] or "unstated"}  {result["tag"] or "unstated"}  '
          f'{result["accessed"] or "unstated"}{suffix}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="concept query, as one quoted argument")
    parser.add_argument("--symbol", help="exact DSS or Python symbol")
    parser.add_argument("--class", dest="class_name")
    parser.add_argument("--version")
    parser.add_argument("--evidence")
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--stats", action="store_true")
    args = parser.parse_args(argv)
    if args.query is not None and args.symbol is not None:
        parser.error("choose either QUERY or --symbol")
    filters = (args.query, args.symbol, args.class_name, args.version, args.evidence)
    if any(value is not None and not value.strip() for value in filters):
        parser.error("empty queries or filters are not supported")
    if (args.check or args.stats) and any(value is not None for value in filters):
        parser.error("--check and --stats do not accept query filters")
    if not (args.check or args.stats or args.query or args.symbol or args.class_name):
        parser.error("provide QUERY, --symbol, --class, --stats or --check")
    if args.evidence:
        labels = {value.casefold(): value for value in EVIDENCE}
        if args.evidence.casefold() not in labels:
            parser.error("unknown evidence label. Choose from " + ", ".join(EVIDENCE))
        args.evidence = labels[args.evidence.casefold()]
    try:
        corpus = Corpus(checking=args.check)
        stats = corpus.stats()
        if args.check:
            index_errors = check_index(corpus)
            alias_errors = check_aliases(corpus)
            failures = index_errors + alias_errors
    except (KeyError, TypeError, OSError, ValueError) as exc:
        if args.check:
            print(f"Catalog check failed: {exc}", file=sys.stderr)
            return 1
        parser.error(str(exc))
    if args.check or args.stats:
        if args.json:
            report = {"corpus": stats}
            if args.check:
                report["errors"] = failures
                report["aliases"] = {"records": len(corpus.aliases), "errors": alias_errors}
            print(json.dumps(report, sort_keys=True))
        else:
            print_stats(stats)
            if args.check:
                for failure in failures:
                    print(failure, file=sys.stderr)
                print(f"Object index check: {'FAIL' if index_errors else 'PASS'}")
                print(f"Symbol alias check: {'FAIL' if alias_errors else 'PASS'} ({len(corpus.aliases)} registered)")
        return int(args.check and bool(failures))
    object_record = None
    if args.class_name:
        key = args.class_name.casefold()
        object_record = corpus.by_class.get(key)
        if object_record is None:
            nearby = get_close_matches(key, sorted(corpus.by_class), n=3, cutoff=0.2)
            choices = nearby or sorted(corpus.by_class)[:3]
            parser.error(f"unknown class {args.class_name!r}. Did you mean "
                         + ", ".join(corpus.by_class[name]["element_class"] for name in choices) + "?")
    matches = search(corpus, args, object_record)
    if args.json:
        print(json.dumps({"query": {"concept": args.query, "symbol": args.symbol},
                          "filters": {"class": object_record["element_class"] if object_record else None,
                                      "version": args.version, "evidence": args.evidence},
                          "corpus": stats, "hits": matches}, sort_keys=True))
    else:
        for result in matches:
            print_hit(result)
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
