# RHOAI Lineage and Governance POC

This repository is the reproducible integration laboratory for exploring
lineage, provenance, evaluation, and governance across RHOAI.

The POC is built around a customer journey rather than a component demo:

```text
Data Registry asset
  -> governed source and evidence
  -> KFP execution
  -> processing, training, or RAG index
  -> model or application
  -> EvalHub evaluation
  -> MLflow experiment or request trace
  -> authorised lineage and impact view
```

## Repository rules

- Every component build records the source fork, branch, commit, patch state,
  image reference, and deployed image digest.
- Every cluster result records the `lineage-poc` commit, component commits,
  deployment revision, run IDs, and verification result.
- Uncommitted fork changes must be captured as patches or the build must stop.
- Secrets, tokens, kubeconfig contents, and sensitive data never enter this
  repository or its evidence bundles.
- Deferred production concerns are recorded and decided in
  [`production/production-gaps.md`](production/production-gaps.md).

## Start here

- [POC charter](product/charter.md)
- [Personas](product/personas.md)
- [Use cases and user stories](product/use-cases.md)
- [Business value and success measures](product/business-value.md)
- [Previous best-practices findings](prior-art/dr-lineage-best-practices.md)
- [Source and fork traceability](sources/README.md)
- [Architecture and lineage profile](architecture/lineage-profile.md)
- [Implementation slices](architecture/implementation-slices.md)
- [Production gap register](production/production-gaps.md)
- [Evidence records](evidence/README.md)

## Current status

This repository contains the planning and traceability baseline. Slice 1 reuses
the existing `dr-lineage` best-practices application as the initial workload
and conformance fixture before adding new component-fork changes.

The immediate next action is [Slice 1](architecture/implementation-slices.md):
reproduce the inherited fixture, verify the active cluster context, and record
the first machine-readable evidence bundle.

The first local validation result is recorded in
[`evidence/2026-09-29-slice-1-local.json`](evidence/2026-09-29-slice-1-local.json).
The RHOAI health check and retained lineage verification are recorded in
[`evidence/2026-09-29-cluster-preflight.json`](evidence/2026-09-29-cluster-preflight.json).
