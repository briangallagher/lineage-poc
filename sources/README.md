# Source and fork traceability

Component source remains in the local checkouts. This repository records how
each checkout is used and provides scripts to verify, build, deploy, and
capture evidence from those exact revisions. Several current `origin` URLs are
upstream repositories, not personal forks. Record a real fork URL before
making component code changes that must be published.

## Required source record

The lock file records the source repository URL and exact commit. Each build
or deployment evidence record must also identify:

- fork repository when code changes are made;
- source scope and working-tree state;
- captured patch, if any;
- build context and image reference;
- deployed image digest.

## Reproducibility rule

Normal builds must use committed revisions. A dirty source scope must be
committed before the build or have its complete diff captured under
`sources/patches/`. The build must fail when the source state cannot be
reconstructed. Changes outside the declared source scope are reported but do
not contaminate that build. The initial `dr-lineage` fixture has a clean
`sample-app-best-practices` source scope despite an unrelated untracked note
at the repository root.

Paths in [`forks.yaml`](forks.yaml) are relative to the repository root's
parent. Set `LINEAGE_POC_FORK_ROOT` or use `--checkout NAME=PATH` to adapt a
different local layout. [`component-commits.lock.json`](component-commits.lock.json)
contains portable source pins, without local filesystem paths or a circular
reference to the commit containing the lock itself.
