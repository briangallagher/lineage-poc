# Reproducibility scripts

## Source preflight

Run this before building a component image or applying a deployment:

```bash
python3 scripts/source_preflight.py --component dr-lineage
```

The command reads [`sources/forks.yaml`](../sources/forks.yaml) and the
[commit lock](../sources/component-commits.lock.json), then checks the selected
checkout's origin, commit, and source scope. It fails when the source is
missing, mismatched, or dirty. Run without `--component` to inventory every
configured checkout.

Use `--allow-dirty` only for inventory. A dirty source scope is not a
reproducible build input until its changes are committed to the source
repository or captured as a reviewed patch under `sources/patches/`. Dirty
paths outside a component's declared source scope are reported separately.

Use `--json` when a later build/evidence tool needs machine-readable output.

## Slice 1 local validation

```bash
python3 scripts/verify_slice1_local.py
```

This validates the locked `dr-lineage` fixture, runs pytest, Ruff, shell
syntax checks, and renders the OpenShift manifests. It emits JSON evidence on
stdout without copying test logs or credentials into the record. Use
`--setup` on a fresh checkout to install the locked Python dependencies first.
Set `UV_CACHE_DIR` if your default cache is not writable.

## Slice 1 cluster evidence

After `run-scenarios.sh` succeeds, capture the source commit, image digests,
pipeline package hash, and six KFP run IDs with:

```bash
python3 scripts/capture_slice1_cluster.py \
  --pipeline-id PIPELINE_ID --pipeline-version-id VERSION_ID
```

The command validates the scenario states, the direct-write blindness check,
the pipeline-version reference recorded on every run, the seed Job, and the
images used by the deployment. It prints a sanitized JSON record to stdout for
review and inclusion under `evidence/`.
