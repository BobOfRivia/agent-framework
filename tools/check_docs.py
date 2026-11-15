#!/usr/bin/env python3
"""Validate repository documentation; no product code or credentials required."""
import argparse
import copy
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]\n]*\]\((<?[^\s)]+>?)\)")


def check():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas", action="store_true")
    args = parser.parse_args()
    errors = []
    markdown = sorted(ROOT.rglob("*.md"))
    markdown = [p for p in markdown if ".git" not in p.parts and ".venv" not in p.parts]
    link_count = 0
    for path in markdown:
        body = path.read_text(encoding="utf-8")
        fence = None
        visible = []
        for line in body.splitlines():
            match = re.match(r"^\s*(`{3,}|~{3,})", line)
            if match:
                marker = match.group(1)[0]
                fence = None if fence == marker else marker
            elif fence is None:
                visible.append(line)
        if fence is not None:
            errors.append("Unclosed fence: " + str(path.relative_to(ROOT)))
        for target in LINK.findall("\n".join(visible)):
            target = target.strip("<>")
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            destination = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not destination:
                continue
            resolved = (path.parent / destination).resolve()
            link_count += 1
            if ROOT not in resolved.parents or not resolved.exists():
                errors.append("Broken local link: %s -> %s" % (path.relative_to(ROOT), target))
    json_files = sorted(list((ROOT / "schemas").glob("*.json")) + list((ROOT / "examples").rglob("*.json")))
    loaded = {}
    for path in json_files:
        try:
            loaded[path] = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            errors.append("Invalid JSON %s: %s" % (path.relative_to(ROOT), exc))

    for relative, prefix, first, last in (("docs/product-requirements.md", "R", 1, 14), ("docs/acceptance.md", "AC", 1, 27), ("docs/development-plan.md", "WP", 0, 13)):
        path = ROOT / relative
        if path.exists():
            found = set(re.findall(r"\b" + prefix + r"-\d{2}\b", path.read_text(encoding="utf-8")))
            expected = {"%s-%02d" % (prefix, number) for number in range(first, last + 1)}
            missing = expected - found
            if missing:
                errors.append("Missing contract IDs in %s: %s" % (relative, sorted(missing)))
    trace = (ROOT / "docs/traceability.md").read_text(encoding="utf-8")
    for number in range(1, 15):
        if "R-%02d" % number not in trace:
            errors.append("Missing requirement trace: R-%02d" % number)

    schema_examples = 0
    if args.schemas and len(loaded) == len(json_files):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError:
            errors.append("Install tools/requirements-docs.txt before --schemas")
        else:
            validators = {}
            for filename in ("agent-revision", "task-create", "task-event"):
                schema = loaded[ROOT / "schemas" / (filename + ".schema.json")]
                Draft202012Validator.check_schema(schema)
                validators[filename] = Draft202012Validator(schema, format_checker=FormatChecker())
            for folder, name in (("agents", "agent-revision"), ("tasks", "task-create")):
                for path in sorted((ROOT / "examples" / folder).glob("*.json")):
                    instance = loaded[path]
                    for error in validators[name].iter_errors(instance):
                        errors.append("Schema mismatch %s: %s" % (path.relative_to(ROOT), error.message))
                    if folder == "agents":
                        ids = [x["id"] for x in instance["capabilities"]]
                        if len(ids) != len(set(ids)):
                            errors.append("Duplicate capability id: " + str(path.relative_to(ROOT)))
                    schema_examples += 1
            cloud = loaded[ROOT / "examples/tasks/cloud-research.json"]
            invalid = []
            bad = copy.deepcopy(cloud)
            bad["execution"]["device_id"] = "device_unexpected"
            invalid.append(bad)
            bad = copy.deepcopy(cloud)
            bad["execution"]["target"] = "local"
            invalid.append(bad)
            bad = copy.deepcopy(cloud)
            bad["tenant_id"] = "injected_space"
            invalid.append(bad)
            for number, instance in enumerate(invalid, 1):
                if validators["task-create"].is_valid(instance):
                    errors.append("Negative task fixture unexpectedly valid: %d" % number)
            event = {"schema_version": "1", "event_id": "evt_01", "space_id": "space_demo", "task_id": "task_demo", "sequence": 1, "type": "task.created", "occurred_at": "2026-11-15T00:00:00Z", "payload": {"state": "queued"}}
            for error in validators["task-event"].iter_errors(event):
                errors.append("Event example mismatch: " + error.message)
    if errors:
        for error in errors:
            print("ERROR: " + error, file=sys.stderr)
        return 1
    print("PASS: %d Markdown files, %d local links, %d JSON files%s" % (len(markdown), link_count, len(json_files), ", %d schema examples + negative fixtures" % schema_examples if args.schemas else ""))
    return 0


if __name__ == "__main__":
    sys.exit(check())
