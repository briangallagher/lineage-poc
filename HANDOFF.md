# Handoff — 2026-09-29, 17:39 UTC

This is a pause point, not a Slice 1 completion claim. Read this file and
`architecture/implementation-slices.md` before resuming cluster work. No
credentials, tokens, kubeconfig data, or sensitive payloads are recorded here.

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
  `7063144a5d36597a4755a91768b47fec6b1c5e13` before this handoff. The
  source lock pins the fork commit below. The retry-collision diagnostic
  evidence and this handoff must be committed/pushed at the pause.
- Fixture fork: `/Users/briangallagher/dev/workspaces/dr-lineage`, remote
  `https://github.com/briangallagher/dr-lineage.git`, branch
  `codex/lineage-poc-fixture-credentials`, published commit
  `b4c418c9f4b53ada66fca71e74bd5c434a90d62c`.
- Fixture source scope `sample-app-best-practices` is clean and pinned. An
  unrelated untracked `competitor-analysis.md` at the fork root is user-owned
  and has been preserved.
- The fixture has 39 passing local tests, changed-file Ruff check and format
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
- Fresh corrected images built from fork commit `b4c418c...` and deployed:
  `lineage-demo-app:b4c418c9f4b5` digest
  `sha256:9f4aa93137d80a9b5e094a154b73c426703a50d34dfc39cf471e4157508e1618`;
  `lineage-demo-spark:b4c418c9f4b5` digest
  `sha256:fef8aac202b3f40cdc9b4ba8de93989b17915eab13add29f2bd7fc4d6e0338aa`.
  Seed Job completed and registry rollout succeeded.
- Compiled package `sample-app-best-practices/build/pipeline.yaml` SHA-256
  `00fe8f691521a915032be59cd6ff3a2269fee104971ad9470e390541441404f0`.
  KFP pipeline ID `76c7563e-7fcb-4fde-bbf4-61dac8a80a69`; uploaded
  version ID `f9051a7c-59a0-4974-8169-15bf462981dd`. KFP API confirmed that
  uploaded version's pipeline and platform specs exactly match both YAML
  documents of the compiled package.
- A six-scenario rerun was started via
  `sample-app-best-practices/scripts/run-scenarios.sh` in tool session `3977`.
  At 17:39 UTC, the first two success workflows (`...-b6dlw`, `...-2l2fr`)
  had Succeeded; the next scenario had not yet appeared. The first run ID is
  `bf697cb7-1a10-4453-a6e7-85b11c89aa8a`. The suite submits scenarios
  sequentially and writes `build/scenario-results.json` only at the end, then
  calls `scripts/verify.sh`. Do not mistake the older report for this rerun.
  The process may continue while this chat is paused; verify its state rather
  than assuming it completed or stopped.

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
   reverification remains pending until the current suite finishes.
2. A separate pipeline-version provenance gap was found. The fixture's
   `create_run_from_pipeline_package` API submits an inline spec. KFP's run
   metadata has no `pipeline_version_id`, even though the uploaded version
   matches the same compiled package. Do **not** describe the current suite as
   version-linked. Before claiming Slice 1 fully qualified, change the
   fixture runner to submit with `kfp.Client.run_pipeline(..., pipeline_id=...,
   version_id=...)`, assert each run references that version through KFP's
   read API, test it, publish a new fork commit, update the source lock,
   rebuild, and rerun. Record this as an explicit provenance decision/gap.
3. External seed-image pull and S3 lifecycle `Content-MD5` issues were fixed
   in earlier fork commits; production gaps 009 and 010 remain partial because
   external base-image accessibility and storage upgrades need qualification.

## Resume safely

1. Confirm `git status --short` and `git rev-parse HEAD` in both repositories;
   keep the unrelated `competitor-analysis.md` untouched. Confirm `oc whoami`
   and `oc whoami --show-server` before any cluster write.
2. In the fixture directory, check whether the current suite's process is
   still running (tool session `3977` may or may not survive the pause).
   Inspect `oc get workflows.argoproj.io -n ol-best-practices` for the new
   workflows and inspect `build/scenario-results.json`. A completed new report
   must contain first run ID `bf697cb7-1a10-4453-a6e7-85b11c89aa8a`.
   If the process ended early or the report is absent/old, diagnose before
   rerunning. Avoid overlapping suites because they share a mutable S3 source
   and Marquez event-count bypass check.
3. Once the new report exists, run `./scripts/verify.sh` from the fixture if
   its automatic result is unknown. This is the regression gate for distinct
   Spark retries. Capture the exact pass/fail result; do not mark it passed
   from KFP states alone.
4. Update the diagnostic evidence's `cluster_reverification` and create a
   fresh cluster evidence record. The existing
   `scripts/capture_slice1_cluster.py` records source, images, package hash,
   and runs, but its `pipeline.version_id` currently denotes an *uploaded*
   version, not the version executed by these inline-spec runs. Correct that
   field/semantics before publishing evidence.
5. Implement and verify the version-linked run path described above. Update
   `architecture/implementation-slices.md`, `production/production-gaps.md`,
   `evidence/README.md`, and the root README with accurate status and links.
   Commit and push both repositories as required; do not claim production
   readiness while open gaps remain.

All cluster changes so far were confined to the existing
`ol-best-practices` namespace and its fixture resources. No secrets should be
copied from OpenShift output into the repository.
