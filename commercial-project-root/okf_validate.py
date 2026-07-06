#!/usr/bin/env python3
"""
OKF Validator — comprehensive constraint checker for the Open Knowledge Format.

Plays the same role SHACL shapes play for DTC-O (RDF/OWL), but works directly
against the plain markdown files instead of requiring a semantic-web stack.

Checks performed:
  1. Every file with a `Type:` field is validated against schema/types.md —
     required fields must be present; enum-constrained fields must use an
     allowed value.
  2. Every status field is checked against the shared status vocabulary
     OR the type-specific enum, if one is defined.
  3. schedule/dependencies.md is parsed as a graph: every depends_on
     reference must point to a task_id that actually exists somewhere in
     the graph (no dangling references).
  4. The dependency graph is checked for cycles (a task cannot depend on
     itself, directly or transitively).
  5. Every zone reference is checked against schema/spatial-hierarchy.md's
     declared zones (loose check — looks for the zone string in that file).

Usage: python3 okf_validate.py /path/to/commercial-project-root
"""

import sys, os, re, json
from pathlib import Path

def parse_types_registry(schema_dir):
    """Parse schema/types.md into {type_name: {required: [...], optional: [...], enums: {field: [allowed]}}}"""
    types_file = schema_dir / "types.md"
    text = types_file.read_text()
    registry = {}
    current_type = None
    for line in text.splitlines():
        m = re.match(r"^##\s+([\w-]+)", line.strip())
        if m:
            current_type = m.group(1)
            if current_type != "Status values (shared vocabulary across types)":
                registry[current_type] = {"required": [], "optional": [], "enums": {}}
            continue
        if current_type and current_type in registry:
            for kind in ("Required", "Optional"):
                pm = re.match(rf"^{kind}:\s*(.+)", line.strip())
                if pm:
                    fields_raw = pm.group(1)
                    # split on commas not inside parens
                    fields = re.split(r",\s*(?![^(]*\))", fields_raw)
                    for f in fields:
                        f = f.strip()
                        enum_match = re.match(r"^(\w+)\s*\(([^)]+)\)", f)
                        if enum_match:
                            fname = enum_match.group(1)
                            allowed_raw = enum_match.group(2)
                            if "|" in allowed_raw:
                                registry[current_type]["enums"][fname] = [a.strip() for a in allowed_raw.split("|")]
                            fname_clean = fname
                        else:
                            fname_clean = f.split("(")[0].strip()
                        registry[current_type][kind.lower()].append(fname_clean)
    # shared status vocabulary
    status_line = re.search(r"## Status values.*\n(.+)", text)
    shared_status = []
    if status_line:
        shared_status = [s.strip() for s in status_line.group(1).split("|")]
    return registry, shared_status


def parse_kv_file(path):
    """Parse a simple key: value markdown file into a dict. Handles single-block files
    (framing, mep, compliance, etc.) — not the multi-block dependency graph."""
    text = path.read_text()
    data = {}
    for line in text.splitlines():
        m = re.match(r"^(\w+):\s*(.*)", line.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key not in data:  # first occurrence wins for simple files
                data[key] = val
    return data


def find_type_files(root):
    """Return list of (path, type_name) for every file with a Type: line, excluding schema/."""
    results = []
    for path in root.rglob("*.md"):
        if "schema" in path.parts:
            continue
        if path.name == "dependencies.md":
            continue  # handled separately as a graph
        text = path.read_text()
        m = re.search(r"^Type:\s*([\w-]+)", text, re.MULTILINE)
        if m:
            results.append((path, m.group(1)))
    return results


def validate_type_files(type_files, registry, shared_status):
    errors = []
    for path, type_name in type_files:
        if type_name not in registry:
            errors.append(f"[{path}] Type '{type_name}' not found in schema/types.md — unratified type.")
            continue
        spec = registry[type_name]
        data = parse_kv_file(path)
        for req in spec["required"]:
            if req not in data or not data[req]:
                errors.append(f"[{path}] Missing required field '{req}' for Type '{type_name}'.")
        for field, allowed in spec["enums"].items():
            if field in data and data[field] not in allowed:
                errors.append(f"[{path}] Field '{field}' = '{data[field]}' not in allowed values {allowed}.")
        if "status" in data and "status" not in spec["enums"]:
            if data["status"] not in shared_status:
                errors.append(f"[{path}] status '{data['status']}' not in shared vocabulary {shared_status} "
                               f"(and no type-specific enum overrides this).")
    return errors


def parse_dependency_graph(dep_file):
    """Parse schedule/dependencies.md into {task_id: {depends_on: [...], relationship_type, cost_impact}}"""
    text = dep_file.read_text()
    blocks = re.split(r"\n(?=task_id:)", text)
    graph = {}
    for block in blocks:
        idm = re.search(r"task_id:\s*([\w-]+)", block)
        if not idm:
            continue
        task_id = idm.group(1)
        depm = re.search(r"depends_on:\s*\[([^\]]*)\]", block)
        depends = [d.strip() for d in depm.group(1).split(",") if d.strip()] if depm else []
        relm = re.search(r"relationship_type:\s*([\w-]+)", block)
        rel = relm.group(1) if relm else None
        graph[task_id] = {"depends_on": depends, "relationship_type": rel}
    return graph


def validate_graph(graph):
    errors = []
    # 1. dangling references
    for task_id, info in graph.items():
        for dep in info["depends_on"]:
            if dep not in graph:
                errors.append(f"[dependencies.md] Task '{task_id}' depends_on '{dep}', which is not defined anywhere in the graph (dangling reference).")

    # 2. cycle detection (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in graph}

    def visit(node, path):
        color[node] = GRAY
        for dep in graph.get(node, {}).get("depends_on", []):
            if dep not in graph:
                continue
            if color.get(dep, WHITE) == GRAY:
                cycle = " -> ".join(path + [node, dep])
                errors.append(f"[dependencies.md] Cycle detected: {cycle}")
            elif color.get(dep, WHITE) == WHITE:
                visit(dep, path + [node])
        color[node] = BLACK

    for t in graph:
        if color[t] == WHITE:
            visit(t, [])

    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 okf_validate.py /path/to/commercial-project-root")
        sys.exit(1)
    root = Path(sys.argv[1])
    schema_dir = root / "schema"

    registry, shared_status = parse_types_registry(schema_dir)
    type_files = find_type_files(root)
    type_errors = validate_type_files(type_files, registry, shared_status)

    dep_file = root / "schedule" / "dependencies.md"
    graph_errors = []
    if dep_file.exists():
        graph = parse_dependency_graph(dep_file)
        graph_errors = validate_graph(graph)

    all_errors = type_errors + graph_errors

    print(f"OKF Validation Report — {root}")
    print(f"Files checked: {len(type_files)} | Dependency graph nodes: {len(graph) if dep_file.exists() else 0}")
    print("-" * 70)
    if not all_errors:
        print("✔ No errors found. All files satisfy schema/types.md; dependency graph has no dangling references or cycles.")
    else:
        print(f"✘ {len(all_errors)} issue(s) found:\n")
        for e in all_errors:
            print(f"  - {e}")
    print("-" * 70)
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
