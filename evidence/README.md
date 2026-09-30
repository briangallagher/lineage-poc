# Evidence

Evidence records connect a verification result to the exact `lineage-poc`
working tree, component source commits, commands, and observed result. They
must not contain credentials, kubeconfig contents, tokens, or sensitive data.

The first record is the local Slice 1 validation of the inherited
`dr-lineage` fixture. Cluster evidence is accepted only when the scenario
report contains the six expected terminal states, the retry contract passes,
and every run carries the pipeline/version reference used for submission.
