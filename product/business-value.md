# Business value and success measures

## Value hypotheses

### Faster investigation

Reduce the time needed to answer where a model, index, or application answer
came from and which downstream assets are affected.

### Safer promotion

Make evaluation evidence and release thresholds visible and repeatable before a
model or application is promoted.

### Lower integration cost

Give RHOAI components a shared identity and lineage contract so customers do
not build one-off provenance integrations for every workflow.

### Stronger governance

Make authorization, source evidence, evaluation history, and limitations
visible rather than implying that every lineage edge is audit-grade provenance.

## Measures for the POC

- A complete asset-to-answer and asset-to-model journey can be demonstrated.
- Every deployed component is traceable to a fork commit and image digest.
- Required lineage conformance tests pass on the target cluster.
- Cross-project negative authorization tests pass.
- A changed source revision identifies affected work and triggers a new
  evaluation path.
- A failure scenario identifies the authoritative workload status and the
  lineage delivery status separately.
- A new operator or engineer can reproduce the run from this repository and
  the pinned fork sources.
