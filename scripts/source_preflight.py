#!/usr/bin/env python3
"""Validate the local component checkouts used by the lineage POC.

The fork manifest is intentionally small and human-readable.  This script
parses only the fields required by that manifest and fails closed when an
entry is incomplete or a checkout is not a Git repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sources" / "forks.yaml"
LOCK = ROOT / "sources" / "component-commits.lock.json"


class ManifestError(ValueError):
    """Raised when the constrained fork manifest is malformed."""


def parse_manifest(path: Path, fork_root_override: Path | None) -> tuple[Path, list[dict[str, str]]]:
    """Read the small, deliberately constrained subset used by forks.yaml."""

    fork_root: Path | None = None
    components: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        root_match = re.fullmatch(r"fork_root:\s*(.+)", line.strip())
        if root_match:
            fork_root = Path(root_match.group(1).strip().strip("'\""))
            continue

        if line.strip() == "components:":
            continue

        component_match = re.fullmatch(r"\s*-\s+name:\s*([^\s]+)", line)
        if component_match:
            if current is not None:
                components.append(current)
            current = {"name": component_match.group(1)}
            continue

        field_match = re.fullmatch(r"\s+(local_path|role|source_scope):\s*(.+)", line)
        if field_match and current is not None:
            key, value = field_match.groups()
            current[key] = value.strip().strip("'\"")
            continue

        raise ManifestError(f"unsupported manifest syntax at {path}:{number}: {raw_line}")

    if current is not None:
        components.append(current)
    if fork_root is None:
        raise ManifestError(f"{path} does not define fork_root")
    if not components:
        raise ManifestError(f"{path} does not define any components")

    names = [component.get("name", "") for component in components]
    if len(names) != len(set(names)):
        raise ManifestError("component names must be unique")
    for component in components:
        missing = {"name", "local_path", "role"} - component.keys()
        if missing:
            raise ManifestError(
                f"component {component.get('name', '<unnamed>')} is missing: "
                + ", ".join(sorted(missing))
            )

    if fork_root_override is not None:
        fork_root = fork_root_override
    if not fork_root.is_absolute():
        fork_root = (ROOT / fork_root).resolve()
    return fork_root, components


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return result.stdout.rstrip()


def dirty_paths(repo: Path, scope: str | None = None) -> list[str]:
    command = ["status", "--porcelain=v1", "--untracked-files=all"]
    if scope is not None:
        command.extend(["--", scope])
    return [line[3:] for line in git(repo, *command).splitlines() if line]


def inspect_component(
    fork_root: Path,
    component: dict[str, str],
    pin: dict[str, str],
    checkout_override: Path | None,
) -> dict[str, object]:
    relative_path = Path(component["local_path"])
    path = checkout_override or (relative_path if relative_path.is_absolute() else fork_root / relative_path)
    path = path.resolve()
    scope = component.get("source_scope", ".")
    result: dict[str, object] = {
        "name": component["name"],
        "role": component["role"],
        "path": str(path),
        "source_scope": scope,
        "pinned_commit": pin.get("commit", ""),
    }

    scope_path = Path(scope)
    if scope_path.is_absolute() or ".." in scope_path.parts:
        result.update({"state": "invalid", "error": "source_scope must stay inside the checkout"})
        return result
    if pin.get("source_scope", ".") != scope:
        result.update({"state": "invalid", "error": "manifest and lock source_scope differ"})
        return result

    if not path.is_dir():
        result.update({"state": "missing", "error": "checkout directory does not exist"})
        return result

    try:
        git_root = Path(git(path, "rev-parse", "--show-toplevel")).resolve()
        commit = git(path, "rev-parse", "HEAD")
        branch = git(path, "branch", "--show-current") or "DETACHED"
        remotes = git(path, "remote").splitlines()
        remote = git(path, "remote", "get-url", "origin") if "origin" in remotes else ""
        source_dirty = dirty_paths(path, scope)
        checkout_dirty = dirty_paths(path)
    except RuntimeError as error:
        result.update({"state": "invalid", "error": str(error)})
        return result

    if git_root != path:
        result.update(
            {
                "state": "invalid",
                "error": f"Git root resolves to {git_root}, not the configured checkout",
            }
        )
        return result

    source_path = path / scope_path
    if not source_path.exists():
        result.update({"state": "invalid", "error": f"source_scope does not exist: {scope}"})
        return result

    mismatches = []
    if commit != pin.get("commit"):
        mismatches.append("HEAD differs from pinned commit")
    if remote != pin.get("repository_url"):
        mismatches.append("origin URL differs from pinned repository URL")

    state = "mismatch" if mismatches else ("dirty" if source_dirty else "clean")
    result.update(
        {
            "state": state,
            "remote": remote,
            "branch": branch,
            "commit": commit,
            "dirty_paths": source_dirty,
            "checkout_dirty_paths": checkout_dirty,
            "reproducible": state == "clean",
        }
    )
    if mismatches:
        result["error"] = "; ".join(mismatches)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--lock", type=Path, default=LOCK)
    parser.add_argument(
        "--fork-root",
        type=Path,
        default=Path(os.environ["LINEAGE_POC_FORK_ROOT"])
        if "LINEAGE_POC_FORK_ROOT" in os.environ
        else None,
    )
    parser.add_argument("--component", action="append", help="check only this component; repeatable")
    parser.add_argument(
        "--checkout",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="override one component checkout path",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="report dirty checkouts without failing the command",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        fork_root, components = parse_manifest(args.manifest.resolve(), args.fork_root)
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
        if lock.get("schema_version") != 1 or not isinstance(lock.get("components"), dict):
            raise ManifestError("unsupported or malformed component lock")
        names = {component["name"] for component in components}
        selected = set(args.component or names)
        if unknown := selected - names:
            raise ManifestError("unknown component(s): " + ", ".join(sorted(unknown)))
        overrides: dict[str, Path] = {}
        for assignment in args.checkout:
            name, separator, value = assignment.partition("=")
            if not separator or name not in names or not value:
                raise ManifestError(f"invalid --checkout value: {assignment}")
            overrides[name] = Path(value)
        inspected = []
        for component in components:
            name = component["name"]
            if name not in selected:
                continue
            pin = lock["components"].get(name)
            if not isinstance(pin, dict):
                raise ManifestError(f"component {name} has no lock entry")
            inspected.append(inspect_component(fork_root, component, pin, overrides.get(name)))
    except (OSError, ManifestError, RuntimeError, ValueError) as error:
        print(f"source preflight: ERROR: {error}", file=sys.stderr)
        return 2

    payload = {
        "manifest": str(args.manifest.resolve()),
        "lock": str(args.lock.resolve()),
        "components": inspected,
    }
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Source preflight: {args.manifest.resolve()}")
        for component in inspected:
            state = str(component["state"]).upper()
            suffix = ""
            if component.get("dirty_paths"):
                suffix = f" ({len(component['dirty_paths'])} dirty path(s))"
            if component.get("error"):
                suffix = f" ({component['error']})"
            print(f"  {state:7} {component['name']}: {component['path']}{suffix}")

    failures = [
        component
        for component in inspected
        if component["state"] != "clean"
        and (not args.allow_dirty or component["state"] != "dirty")
    ]
    if failures:
        print(
            "source preflight: FAIL: selected source scopes must match the lock "
            "and be clean; use --allow-dirty only for inventory/reporting",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
