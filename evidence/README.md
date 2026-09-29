# Evidence

Evidence records connect a verification result to the exact `lineage-poc`
working tree, component source commits, commands, and observed result. They
must not contain credentials, kubeconfig contents, tokens, or sensitive data.

The first record is the local Slice 1 validation of the inherited
`dr-lineage` fixture. Cluster evidence will be added only after the active
OpenShift API is reachable and the run identifiers are captured from that
execution.
