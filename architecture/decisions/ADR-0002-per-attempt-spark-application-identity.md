# ADR-0002: Unique SparkApplication identity per KFP attempt

## Status

Accepted and implemented in the `dr-lineage` fixture fork

## Context

The fresh Slice 1 failure suite showed that a failed Spark task was retried by
KFP, but its second attempt never started a SparkApplication. Both attempts
used a resource name based on the first eight characters of a UUIDv7. Those
characters encode time and were identical for the two nearby attempts. The
second create returned Kubernetes 409 `AlreadyExists`, leaving only one native
Spark lineage run and failing the two-attempt contract check.

## Decision

Use the full 32 hexadecimal characters of the per-attempt UUIDv7 in the
SparkApplication name (`transform-<uuid-hex>`). This is a valid Kubernetes DNS
label below the 63-character limit. Keep the native Spark OpenLineage
application run ID equal to that same UUID, and retain KFP's root run ID as
the parent. A regression test supplies two UUIDv7 values with the same first
eight characters and requires different application names.

## Consequences

- A KFP retry gets a distinct Kubernetes resource and native Spark lineage
  identity, even when attempts occur within the same short time window.
- Failed SparkApplications remain inspectable without blocking subsequent
  attempts. Their retention and cleanup policy is still a production concern.
- The fix belongs in the source fork and is pinned by the integration lock;
  a fresh cluster build and six-scenario contract run must validate it.
