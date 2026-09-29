# ADR-0001: Repository and source traceability

## Status

Accepted for the POC baseline

## Decision

`lineage-poc` is the integration, deployment, verification, and evidence
repository. Component forks remain independently source controlled. Every POC
run records the exact fork commit or captured patch, image digest, deployment
revision, run identifiers, and verification result.

## Rationale

Component repositories have their own ownership, build systems, and upstream
lifecycles. Keeping their code in separate forks preserves a path to upstream
contribution while the integration repository remains reproducible.

## Consequences

- The POC needs a source manifest and snapshot command.
- Builds must reject unrecorded dirty working trees.
- A component change and its integration evidence are separate commits that
  must be linked in the evidence bundle.
- The repository can reproduce the integration even when the UI is not yet
  implemented.
