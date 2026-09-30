# Implementation slices

The POC is intentionally staged so each slice proves a customer-facing
lineage question before more RHOAI components are added.

## Slice 0 — repository and source control baseline

Status: in progress.

Deliverables already started:

- product charter, personas, use cases, value measures, and success gate;
- inherited `dr-lineage` findings and evidence links;
- lineage identity and assurance profile;
- fork manifest, commit snapshot, production-gap register, and source
  preflight.

Exit criteria: the repository can identify every source checkout and refuses a
reproducibility claim when a configured checkout is dirty.

## Slice 1 — inherited golden fixture and contract harness

Use the existing `dr-lineage` application as the first backend workload. Run
its local checks and the cluster scenarios, then adapt the assertions into
machine-readable evidence consumed by this repository.

Current status: local checks complete, RHOAI and application preflight pass,
and the retry-collision fix has completed a fresh six-workflow cluster rerun.
The fixture submits by an uploaded KFP pipeline-version reference and
re-reads every run to verify that KFP retained that reference. The fresh
version-linked rerun passed all 18 Marquez contract checks and its source,
image, package, and run evidence is captured under `evidence/`.

The local fixture credential runner was hardened in the `dr-lineage` fork and
its published commit is pinned in the source lock.

The initial inline-spec cluster suite was intentionally not accepted as final
provenance evidence: KFP run metadata did not contain a pipeline version
reference. That gap is tracked in `production/production-gaps.md`; the
version-linked submission path is now the accepted Slice 1 path.

Prove:

- Registry asset to physical dataset identity and observed-content evidence;
- KFP root, child, retry, and failure relationships;
- native Spark OpenLineage behavior without duplicate events;
- workload state versus contradictory event-terminal state;
- namespace and authorization boundaries.

Exit criteria: the existing behavior is reproduced from a recorded source
commit and the conformance result is attached to a `lineage-poc` commit.

## Slice 2 — governed asset-to-model path

Add the Data Registry API and DCH references to the fixture, then run a KFP
pipeline that consumes a registered structured asset, records the registry
revision and source evidence, trains a baseline model, and writes MLflow
artifacts.

Candidate producers: Data Registry, DCH, KFP, Spark, and AutoML. AutoML is an
adapter target until its deployed API and pipeline contract are pinned.

Exit criteria: an authorised API query can answer which asset evidence, run,
artifact, and evaluation candidate produced a model.

## Slice 3 — governed RAG and evaluation path

Register an unstructured document asset, build a vector index through the
selected AutoRAG/OGX path, expose an application endpoint, and evaluate the
retrieval and answer behavior through EvalHub using an explicit test-data
adapter.

MLflow traces capture request-time retrieval, model, and tool spans. The
lineage graph links the trace to the application release, index, source
asset, and EvalHub job; it does not duplicate MLflow's trace ownership.

Exit criteria: an authorised user can start from an answer or evaluation and
walk back to the index, source asset, source evidence, and producing run.

## Slice 4 — change impact and operational qualification

Change a source asset or revision and demonstrate that the API identifies the
affected index, model, evaluation, and application release. Then test retry,
replay, retention, backup/restore, cross-project authorization, and failure
recovery according to the production-gap register.

Exit criteria: the POC reports both the lineage result and its assurance level
(`LINKED`, `OBSERVED`, or `REPRODUCIBLE`) and does not hide unresolved gaps.

## Immediate next action

Run Slice 1 as a read-only and reproducibility check: cleanly identify the
source commit to use, execute the inherited local conformance checks, confirm
the active OpenShift identity/context, and write the first evidence record.
Do not modify a component fork until a missing contract is demonstrated and a
decision is recorded in an ADR or production-gap entry.
