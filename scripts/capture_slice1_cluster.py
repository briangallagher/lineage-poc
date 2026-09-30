#!/usr/bin/env python3
"""Capture source, image, pipeline, and run IDs for a completed Slice 1 suite."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from source_preflight import LOCK, MANIFEST, ROOT, inspect_component, parse_manifest


def command(*args: str) -> str:
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def oc_json(*args: str) -> dict:
    return json.loads(command("oc", *args, "-o", "json"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="ol-best-practices")
    parser.add_argument("--pipeline-id", required=True)
    parser.add_argument("--pipeline-version-id", required=True)
    parser.add_argument("--checkout", type=Path)
    args = parser.parse_args()

    fork_root, components = parse_manifest(MANIFEST, None)
    component = next(item for item in components if item["name"] == "dr-lineage")
    pin = json.loads(LOCK.read_text(encoding="utf-8"))["components"]["dr-lineage"]
    source = inspect_component(fork_root, component, pin, args.checkout)
    if source["state"] != "clean":
        raise RuntimeError(f"Pinned fixture source is not clean: {source['state']}")

    app = Path(str(source["path"])) / str(source["source_scope"])
    package = app / "build" / "pipeline.yaml"
    report = json.loads((app / "build" / "scenario-results.json").read_text(encoding="utf-8"))
    runs = report["runs"]
    expected = {
        "success-1": "SUCCEEDED",
        "success-2": "SUCCEEDED",
        "success-after-bypass": "SUCCEEDED",
        "failure-ingest": "FAILED",
        "failure-spark": "FAILED",
        "failure-embed": "FAILED",
    }
    observed = {run["scenario"]: run["actual_state"] for run in runs}
    if observed != expected or len(runs) != len(expected):
        raise RuntimeError(f"Scenario results do not match the expected suite: {observed}")
    unlinked = [
        run["scenario"]
        for run in runs
        if run.get("pipeline_id") != args.pipeline_id
        or run.get("pipeline_version_id") != args.pipeline_version_id
    ]
    if unlinked:
        raise RuntimeError(
            "Scenario runs are not linked to the executed pipeline version: "
            f"{unlinked}"
        )
    bypass = report["bypass"]
    if bypass["eventCountBefore"] != bypass["eventCountAfter"]:
        raise RuntimeError("Direct source overwrite unexpectedly changed event count")

    image_tag = pin["commit"][:12]
    images = {}
    for name in ("lineage-demo-app", "lineage-demo-spark"):
        data = oc_json("get", "istag", f"{name}:{image_tag}", "-n", args.namespace)
        images[name] = {
            "tag": image_tag,
            "digest": data["image"]["metadata"]["name"],
            "reference": data["image"]["dockerImageReference"],
        }

    registry = oc_json("get", "deployment", "registry", "-n", args.namespace)
    seed = oc_json("get", "job", "object-store-seed", "-n", args.namespace)
    expected_app = (
        f"image-registry.openshift-image-registry.svc:5000/{args.namespace}/"
        f"lineage-demo-app:{image_tag}"
    )
    registry_image = registry["spec"]["template"]["spec"]["containers"][0]["image"]
    seed_image = seed["spec"]["template"]["spec"]["containers"][0]["image"]
    if registry_image != expected_app or seed_image != expected_app:
        raise RuntimeError("Registry or seed Job image differs from the pinned source tag")
    if seed["status"].get("succeeded") != 1:
        raise RuntimeError("Seed Job did not complete")

    output = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scope": "slice-1-fresh-cluster-suite",
        "lineage_poc_base_commit": command("git", "-C", str(ROOT), "rev-parse", "HEAD"),
        "source": {
            "repository_url": pin["repository_url"],
            "branch": pin["branch"],
            "commit": pin["commit"],
            "source_scope": source["source_scope"],
            "working_tree": source["state"],
        },
        "cluster": {
            "api": command("oc", "whoami", "--show-server"),
            "identity": command("oc", "whoami"),
            "namespace": args.namespace,
        },
        "images": images,
        "deployment": {
            "registry_image": registry_image,
            "registry_ready_replicas": registry["status"].get("readyReplicas", 0),
            "seed_image": seed_image,
            "seed_succeeded": seed["status"]["succeeded"],
        },
        "pipeline": {
            "id": args.pipeline_id,
            "version_id": args.pipeline_version_id,
            "run_submission": "pipeline_version_reference",
            "package_sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
        },
        "asset_id": report["asset"]["assetId"],
        "bypass_event_count": bypass,
        "runs": runs,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
