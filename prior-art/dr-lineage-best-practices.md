# Prior art: dr-lineage best-practices application

Source repository: [briangallagher/dr-lineage at the pinned commit](https://github.com/briangallagher/dr-lineage/tree/75b37c7ed9d548fa922bca256e8a7616e734db88/sample-app-best-practices).
The local checkout is `/Users/briangallagher/dev/workspaces/dr-lineage`.

The application was previously validated as a deployable learning application
using KFP, Spark Operator, native Spark OpenLineage, MinIO, Marquez, PostgreSQL,
and namespace-scoped OpenShift manifests. It provides the initial workload,
fixtures, scenarios, and conformance ideas for this POC.

## Findings inherited by this POC

- A Registry logical asset and a physical S3 dataset are separate identities;
  the relationship needs an explicit symlink or alias facet.
- A mutable source URI does not prove immutable content or reproducibility.
- KFP owns the root run; ingestion, Spark, and embedding work are child runs.
- Retries receive distinct run IDs.
- Spark uses native instrumentation and must not receive duplicate manual events.
- The actual KFP root ID must be obtained from runtime metadata because the
  literal pipeline placeholder was unresolved on the validation cluster.
- Spark failure events can expose contradictory native terminal events; the
  KFP and Spark workload states remain authoritative for final status.
- Feast matched Marquez for the tested operational fixture, but the test-only
  Feast service exposed an authorization gap and did not prove the full RHOAI
  business or revision contract.
- Retention, replay, outage recovery, migrations, backup/restore, capacity,
  cross-project authorization, and revision evidence require separate tests.
- The useful initial assurance model is `Linked`, `Observed`, and
  `Reproducible`.

## Source evidence

- [Application README](https://github.com/briangallagher/dr-lineage/blob/75b37c7ed9d548fa922bca256e8a7616e734db88/sample-app-best-practices/README.md)
- [Session handoff](https://github.com/briangallagher/dr-lineage/blob/75b37c7ed9d548fa922bca256e8a7616e734db88/dr-lineage-handoff.md)
- [Lineage contract](https://github.com/briangallagher/dr-lineage/blob/75b37c7ed9d548fa922bca256e8a7616e734db88/rhoai-lineage-contract-and-integration.md)
- [Feast versus Marquez conformance](https://github.com/briangallagher/dr-lineage/blob/75b37c7ed9d548fa922bca256e8a7616e734db88/sample-app-best-practices/docs/feast-vs-marquez-conformance.md)
- [Live cluster validation](https://github.com/briangallagher/dr-lineage/blob/75b37c7ed9d548fa922bca256e8a7616e734db88/sample-app-best-practices/docs/cluster-validation.md)
