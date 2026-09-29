# Production gap register

This register contains explicit decisions about production concerns that the
POC does not fully implement yet. A gap is not considered closed because a
demo succeeds.

| ID | Area | Current decision | Risk | Revisit trigger | Status |
|---|---|---|---|---|---|
| GAP-001 | Durable delivery and replay | Must be tested before a production-readiness claim | Events may be lost or duplicated | First backend slice is deployed | Open |
| GAP-002 | Cross-project authorization and redaction | Required acceptance gate | Lineage or physical locations may leak | First authenticated API exists | Open |
| GAP-003 | Retention and archive semantics | Must be qualified separately for events, graph, evaluations, and traces | Retained edges may outlive evidence | Backend persistence is selected | Open |
| GAP-004 | Migration and backup/restore | Required for production-shaped qualification | Upgrades may lose relationships or evidence | First persistent cluster deployment | Open |
| GAP-005 | Immutable source evidence | Capture where the source supports it; label weaker evidence honestly | A mutable URI may be mistaken for reproducibility | Registry and DCH contracts are wired | Open |
| GAP-006 | Upstream component changes | Use adapters first; upstream only when required context is unavailable | Fork divergence may become unmaintainable | A missing producer contract is demonstrated | Open |
| GAP-007 | Credential handling | The fixture now passes credentials through stdin; product workflows still require managed workload identities and secret references | Test credentials remain in local process memory during a run | First product component integration | Partial |
| GAP-008 | Image provenance | Record source commit, image digest, deployment image, pipeline package, and run IDs together | A mutable or development tag cannot prove which code ran | First fresh Slice 1 build | Open |
| GAP-009 | External image availability | Pin all fixture and product images by digest and verify access from target cluster registries | A formerly public tag can become unavailable and block redeploy | First fresh Slice 1 build | Open |
| GAP-010 | S3 checksum compatibility | The fixture adds `Content-MD5` for MinIO lifecycle updates; rerun the wire-level and cluster test when Botocore or object storage changes | A client checksum default can make lifecycle setup fail after an otherwise successful seed | Dependency or storage upgrade | Partial |
