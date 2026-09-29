# Use cases and user stories

## UC-001: Trace a model or index to its data

As a data scientist, I want to start from a Data Registry asset and see the
authorised runs, transformations, model versions, or vector indexes that used
it, so that I can understand downstream impact.

Acceptance evidence:

- The API returns logical asset, physical dataset, revision, and observed
  content evidence separately.
- Parent and child runs are visible with retries preserved as separate attempts.
- Cross-project access is denied and tested.

## UC-002: Explain an application answer

As an AI engineer, I want to connect an application trace to the model,
retrieval operation, vector index, and source asset used for a request, so that
I can investigate an incorrect or unsafe answer.

Acceptance evidence:

- The trace has a stable application release and correlation identifier.
- The retrieval path links to the index and source revision.
- Physical locations and prompt content are redacted according to policy.

## UC-003: Evaluate and promote a release

As a governance owner, I want an EvalHub result and evaluation card linked to
the exact model, application, and evaluation dataset, so that promotion is
based on retained evidence.

Acceptance evidence:

- Thresholds and pass/fail outcomes are recorded.
- The evaluation dataset is a governed asset reference.
- MLflow and EvalHub identifiers can be followed from the lineage API.

## UC-004: Assess the impact of a data change

As a platform user, I want to change a Registry asset revision and see which
indexes, models, evaluations, and application releases are stale, so that I
can rerun only the affected work.

Acceptance evidence:

- Old and new revisions remain distinguishable.
- The impact response identifies required reruns.
- A new evaluation can be compared with the previous evaluation.

## UC-005: Diagnose an operational failure

As a platform administrator, I want to see processing failures, lineage delivery
failures, retries, and authoritative status sources separately, so that I can
repair the right system.

Acceptance evidence:

- Workload and lineage-delivery status can differ without being conflated.
- Duplicate, late, replayed, and contradictory events are tested.
- The evidence includes a useful correlation ID and failure reason.
