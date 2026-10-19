# Matching-instance Table 9 timeout

The original GHC 8.4.3 build completed on m5ad.16xlarge, matching the paper's instance type.
The first condition, 2,500 rebirthing agents at 32 capabilities, exceeded the frozen 1,200-second attempt limit.
The enclosing workflow exited 1. No Criterion timing sample was accepted:
`report.json` is empty and no HTML report was produced.
All six timing conditions and thirty retry processes therefore remain required.

The archive retains the source archive, compiler/build log, timing executable,
frozen protocol, hardware manifest, command and complete timeout traceback.
Its 6,893,506 bytes match SHA-256 `189724f6964c9f6b5f0076ad87ecb1794745b33da8a00264cce5d04c12c3b69e`.
The independent full-result auditor cannot pass this incomplete run.
No timed-out process is converted into a measured runtime or a negative replication.

The instance is confirmed stopped after verified collection; its disk remains retained.
The initial inspection mistakenly used the launch-only role, which disallows DescribeInstances.
The repository's normal sandbox client performed the intended instance inspection and stop.
The recorded state is an observation, not a promise of the final transition time.

The next investigation must determine whether a complete model iteration progresses
and whether the original Criterion sampling overhead exceeds the attempt budget.
A larger budget alone would not establish model fidelity or scientific disagreement.
