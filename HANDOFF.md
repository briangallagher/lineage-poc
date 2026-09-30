# Handoff — 2026-09-30, 07:27 UTC

Slice 1 is complete for the inherited fixture. Read this file and
`architecture/implementation-slices.md` before starting Slice 2. This is not a
production-readiness claim; the production-gap register remains authoritative.
No credentials, tokens, kubeconfig data, or sensitive payloads are recorded
here.

## User intent and scope

Build an API/backend-first, production-shaped lineage and governance POC for
RHOAI. Keep product planning, ADRs, production gaps, deployment/reproduction
instructions, and evidence in this `lineage-poc` repository. Component changes
belong in local forks, must be published and pinned here, and must be built,
deployed, and verified on the user's current OpenShift cluster. Discuss any
production concern before intentionally deferring it. The initial slice uses
the inherited `dr-lineage/sample-app-best-practices` fixture; later slices add
Data Registry, KFP, SDG, AutoML, AutoRAG/OGX, EvalHub, and MLflow as their real
contracts are established. The user's `AGENTS.md` also requires reading
`/Users/briangallagher/dev/workspaces/data-registry/PROJECT_CONTEXT.md` for
Data Registry context.

## Published revisions and local state

- Integration repository: `/Users/briangallagher/dev/git-repos/lineage-poc`,
  branch `codex/lineage-poc-bootstrap`, published commit
  `375e283cd809645b2491a21b4c0e4066ed2c0e86` before the final evidence and
  handoff update. The source lock pins the fork commit below.
- Fixture fork: `/Users/briangallagher/dev/workspaces/dr-lineage`, remote
  `https://github.com/briangallagher/dr-lineage.git`, branch
  `codex/lineage-poc-fixture-credentials`, published commit
  `bfd8f9de9417c921c2db6617ce227178741fd5a7`.
- Fixture source scope `sample-app-best-practices` is clean and pinned. An
  unrelated untracked `competitor-analysis.md` at the fork root is user-owned
  and has been preserved.
- The fixture has 40 passing local tests, changed-file Ruff check and format
  check pass, and `git diff --check` passes.

## Cluster verification and current execution

- `oc` context on 2026-09-29: `htpasswd-cluster-admin-user` at
  `https://api.bgal-pool-ljt7l.aws.rh-ods.com:6443`.
- RHOAI operator CSV `rhods-operator.3.6.0-ea.1` is Succeeded;
  `default-dsc` is Ready with 12 managed components. All seven nodes are
  Ready; desired RHOAI deployments are available. The NFD CRD uses
  `nodefeaturegroups.nfd.k8s-sigs.io`, not the suffix expected by the
  cluster-health helper; NFD pods and one L40S GPU were healthy. See
  `evidence/2026-09-29-cluster-preflight.json` for the precise checks.
- Dedicated namespace `ol-best-practices` has the fixture's MinIO, Marquez,
  registry, Spark Operator integration, and KFP/DSPA. No public Routes were
  created for the fixture.
- Fresh images built from fork commit `bfd8f9d...` and deployed:
  `lineage-demo-app:bfd8f9de9417` digest
  `sha256:55fcabe57deb2328e9e846dad36dfeb3e79da41c8f972b0c4f210e441b5bfaaa`;
  `lineage-demo-spark:bfd8f9de9417` digest
  `sha256:b0090d8297154ab779702d63f849810d364519d862573ea2b40a287fde8b5b48`.
  Seed Job completed and registry rollout succeeded.
- Compiled package `sample-app-best-practices/build/pipeline.yaml` SHA-256
  `510c1999857d31702277525f5810151e79bb0739a89139ba2b7ed308a3c96fa3`.
  KFP pipeline ID `76c7563e-7fcb-4fde-bbf4-61dac8a80a69`; version ID
  `5a83ee36-34f2-4764-b168-3cc7ef175ed1`.
- The accepted six-scenario suite produced run IDs
  `aee6700b-6e48-49ed-9e59-a89b764e838d`,
  `92d11481-92d1-44d7-aec4-966babb06e6c`,
  `e1c733f2-4ed6-4631-9beb-6942893423b7`,
  `e19e1def-0388-4d1d-bbfa-2978a3eb3f36`,
  `48453eb3-f355-4aea-8086-519047eea58d`, and
  `ed500ef8-12cf-4eb2-ae08-ad7923792458`. All six runs were re-read from KFP
  and carried the exact pipeline/version reference above. The scenario report
  and 18-check verifier passed.
- Sanitized evidence is recorded in
  `evidence/2026-09-30-slice-1-cluster.json`.

## Findings and decisions

1. The first fresh six-scenario suite reached the expected three successful
   and three failed KFP terminal states, but the 18-check lineage contract
   failed: `failure-spark expected two distinct task attempts; observed 1`.
   KFP had retried; the second SparkApplication create returned 409
   `AlreadyExists` because the original name used only the time-derived first
   eight UUIDv7 characters. The diagnostic is in
   `evidence/2026-09-29-slice-1-retry-collision.json`; the fix and rationale
   are in `architecture/decisions/ADR-0002-per-attempt-spark-application-identity.md`.
   The corrected name uses the full 32 UUID hex characters. Cluster contract
   reverification passed in the accepted cluster evidence.
2. A separate pipeline-version provenance gap was found in the initial suite.
   The fixture now submits with `kfp.Client.run_pipeline(..., pipeline_id=...,
   version_id=...)`, asserts each run reference through KFP's read API, and
   records the IDs in the report. The version-linked cluster rerun passed;
   GAP-011 remains Partial because the product workflow is not yet qualified.
3. External seed-image pull and S3 lifecycle `Content-MD5` issues were fixed
   in earlier fork commits; production gaps 009 and 010 remain partial because
   external base-image accessibility and storage upgrades need qualification.

## Resume safely

1. Confirm `git status --short` and `git rev-parse HEAD` in both repositories;
   keep the unrelated `competitor-analysis.md` untouched. Confirm `oc whoami`
   and `oc whoami --show-server` before any cluster write.
2. No acceptance suite is currently running. The next work is Slice 2:
   establish the Data Registry and DCH contracts, pin their source revisions,
   and agree the governed asset-to-model acceptance question before changing
   component forks.
3. Preserve the evidence boundary: Slice 1 proves the inherited fixture's
   linked operational lineage and version-linked KFP execution. It does not
   close the open production gaps or prove immutable source bytes.

All cluster changes so far were confined to the existing
`ol-best-practices` namespace and its fixture resources. No secrets should be
copied from OpenShift output into the repository.
