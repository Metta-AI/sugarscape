# First accepted Table 9 condition

The 32-capability, 2,500-agent rebirth condition passes the predeclared fit rule on its first attempt.
Independent ordinary least-squares reconstruction from four native Criterion measurements gives
89.962304 seconds per simulation and R-squared 0.999874136128.
Slope reconstruction differs from Criterion by less than 1e-13 seconds.
The paper reports 76.4 seconds; this is a descriptive comparison, not a negative replication verdict.

The instance is m5ad.16xlarge with AMD EPYC 7571, 64 logical CPUs and two threads per core.
Source archive contents and the retained timing binary pass their hashes.
Instance class alone does not establish historical clock state, placement or isolation.

The producer sealed this checkpoint before starting its next condition.
Its 3,669,782-byte archive passes the recorded SHA-256; fresh extraction reproduces both audit files byte-for-byte.
The complete-audit path rejects this incomplete checkpoint.
Five timing conditions and all thirty retry processes remain required; the original producer continues.
The earlier 1,200-second timeout remains preserved separately.

```sh
python replications/thaler_2019/timing/audit_table9.py EXTRACTED CHECKPOINT_AUDIT --timing-prefix
```

Place the pinned source-f5851488.tar.gz alongside EXTRACTED/results before auditing.
Omit --timing-prefix only for the complete terminal archive; the default requires six timings and thirty retry processes.
