# RHOAI lineage profile for the POC

The POC uses OpenLineage for operational relationships and adds RHOAI context
through validated facets and correlation metadata.

## Identity layers

```text
Data Registry asset       stable business identity
Registry revision         declared metadata revision
Observed content          object version, hash, manifest, or snapshot
OpenLineage dataset       exact (namespace, name) runtime identity
```

These identities must not be silently collapsed.

## Run layers

```text
KFP pipeline run          orchestration root
Component run             work observed by a component
Attempt                   one execution including a retry
MLflow run                experiment, metric, artifact, or evaluation record
MLflow trace              request-time execution tree
EvalHub job               evaluation orchestration record
```

ParentRunFacet expresses execution hierarchy. Dataset inputs and outputs
express data dependency. They are complementary relationships.

## Assurance

- `LINKED`: a logical asset is connected to a reported runtime path.
- `OBSERVED`: the producer recorded source evidence.
- `REPRODUCIBLE`: immutable or retained inputs and required execution
  artifacts are available for reconstruction.

An OpenLineage edge alone is `LINKED` unless additional evidence supports a
higher assurance level.

## Initial producers

Data Registry, DCH, KFP, Spark, SDG, AutoML, AutoRAG, Training Hub or Trainer,
and EvalHub are candidate producers. The POC will use adapters first and make
upstream fork changes where the component boundary cannot provide the required
context.

MLflow remains the owner of experiment, evaluation, artifact, and trace
records. The POC links those records to OpenLineage and Registry identifiers.
