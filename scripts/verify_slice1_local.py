#!/usr/bin/env python3
"""Run the inherited lineage fixture's local checks and emit JSON evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from source_preflight import LOCK, MANIFEST, ROOT, inspect_component, parse_manifest


def run(command: list[str], cwd: Path, *, include_output: bool = True) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except OSError as error:
        return {"command": command, "result": "failed", "error": str(error)}
    record: dict[str, object] = {
        "command": command,
        "result": "passed" if completed.returncode == 0 else "failed",
        "exit_code": completed.returncode,
    }
    if include_output:
        output = "\n".join(
            part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
        )
        record["output"] = output[-4000:]
    return record


def emit(record: dict[str, object]) -> None:
    """Discard command output so evidence cannot accidentally include secrets."""

    for check in record.get("checks", []):
        check.pop("output", None)
    print(json.dumps(record, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--setup",
        action="store_true",
        help="run uv sync --frozen --extra dev before validation",
    )
    parser.add_argument(
        "--checkout",
        type=Path,
        help="override the local dr-lineage checkout path",
    )
    args = parser.parse_args()

    fork_root, components = parse_manifest(MANIFEST, None)
    component = next(item for item in components if item["name"] == "dr-lineage")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    pin = lock["components"]["dr-lineage"]
    source = inspect_component(fork_root, component, pin, args.checkout)
    app = Path(str(source["path"])) / str(source["source_scope"])
    checks: list[dict[str, object]] = []
    record: dict[str, object] = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "slice": "slice-1-inherited-golden-fixture",
        "scope": "local-validation",
        "lineage_poc_base_commit": run(
            ["git", "rev-parse", "HEAD"], ROOT
        ).get("output", "").strip(),
        "source": source,
        "checks": checks,
    }

    if source["state"] != "clean":
        record["result"] = "blocked"
        record["reason"] = "dr-lineage source does not match the pinned clean scope"
        emit(record)
        return 1

    if args.setup:
        checks.append(run(["uv", "sync", "--frozen", "--extra", "dev"], app))
        if checks[-1]["result"] != "passed":
            record["result"] = "failed"
            emit(record)
            return 1

    venv_python = app / ".venv" / "bin" / "python"
    venv_ruff = app / ".venv" / "bin" / "ruff"
    if not venv_python.is_file() or not venv_ruff.is_file():
        record["result"] = "blocked"
        record["reason"] = "pinned .venv is absent; rerun with --setup"
        emit(record)
        return 1

    checks.append(run([str(venv_python), "-m", "pytest"], app))
    pytest_output = str(checks[-1].get("output", ""))
    if match := re.search(r"\b(\d+) passed\b", pytest_output):
        checks[-1]["passed_tests"] = int(match.group(1))
    checks.append(run([str(venv_ruff), "check", "src", "tests", "pipeline"], app))

    scripts = sorted((app / "scripts").glob("*.sh"))
    shell_checks = [run(["bash", "-n", str(script)], app, include_output=False) for script in scripts]
    checks.append(
        {
            "command": "bash -n scripts/*.sh",
            "result": "passed"
            if all(item["result"] == "passed" for item in shell_checks)
            else "failed",
            "scripts_checked": len(scripts),
            "failed_scripts": [
                script.name
                for script, result in zip(scripts, shell_checks)
                if result["result"] != "passed"
            ],
        }
    )
    checks.append(run(["oc", "kustomize", "openshift"], app, include_output=False))
    record["result"] = (
        "passed" if all(check["result"] == "passed" for check in checks) else "failed"
    )
    emit(record)
    return 0 if record["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
