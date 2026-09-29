# POC charter

## Objective

Demonstrate that RHOAI can connect governed data assets to processing,
training, retrieval, evaluation, deployment, and request-time evidence through
stable APIs and production-shaped operational controls.

The first reference scenario is a P&C underwriting assistant. It combines
registered underwriting documents, structured submission data, a referral
model, a RAG index, an application, and evaluation evidence.

## Customer problem

AI teams can build models and applications, but it is difficult to answer:

- Which data and version produced this model or index?
- Which source did this answer use?
- Which evaluation approved this release?
- What must be rerun when a source changes?
- Can another project see restricted data or lineage?

## POC hypothesis

Data Registry provides the durable data-asset anchor. OpenLineage captures
reported execution relationships. KFP provides orchestration context. MLflow
stores experiments, evaluations, artifacts, and traces. EvalHub provides
repeatable evaluation evidence. A RHOAI API can join these records into an
authorised, asset-centred answer for users.

## Scope

Initial scope includes Data Registry, KFP, Spark, Data Connect Hub where
available, SDG Hub, AutoRAG/OGX, AutoML, Training Hub or Kubeflow Trainer,
EvalHub, MLflow, and a small application workload.

The first implementation is API and backend focused. UI work follows after the
API, identity, authorization, event, and evidence contracts are proven.

## Non-goals

- Replacing MLflow, EvalHub, KFP, or the Data Registry with one service.
- Claiming that a lineage edge proves the exact source bytes.
- Treating a mutable location or Registry revision as immutable content.
- Modifying every upstream component before an adapter can test the contract.

## Initial decision gate

The POC is successful when an authorised user can start from a Data Registry
asset and retrieve the relevant source evidence, execution runs, derived model
or vector index, evaluation result, and application trace, including an
explanation of what must be rerun after an asset change.
