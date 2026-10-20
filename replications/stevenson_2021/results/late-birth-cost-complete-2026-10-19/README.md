# Complete later-window birth-cost ensemble

All 100 original seeds complete 150,000 cycles with unchanged model rules.
All 100,100 shared-prefix observations match the original 100,000-cycle trajectories byte-for-byte.
The complete audit validates 150,100 retained observations, timestamps, finite metrics, population bounds, native conservation checks, source hashes and successful exits.
No seed becomes extinct or is excluded.

| Metric | Original (75,000,100,000] mean | Later (130,000,150,000] mean |
| --- | ---: | ---: |
| Population | 821.45668 | 821.51270 |
| Total wealth | 15902.67000 | 15899.17345 |
| Mean age | 1418.79840 | 1420.66626 |
| Gini | 0.33671435 | 0.33686113 |

The mean-age change is +1.86787 cycles, with paired 95% interval −3.12201 to +6.85774 across the same 100 seeds.
The later-window mean-age interval is 1416.88488–1424.44764, still far below the published Table 1 value 2264.
This particular later-window choice does not explain the age discrepancy.
The four paired-change intervals include zero; this does not prove stationarity or author-model fidelity.
The target paper's exact averaging convention and implementation remain unidentified, so this is not a negative paper replication.

An independent standard-library calculation checks all 48 reported statistical quantities within 1e-9.
All 413 archive members match their retained source bytes.
Extracting the archive and rerunning its complete analyzer produces byte-identical seed means and summary JSON.
The archive retains the exact C++ source, compiled binary, compiler details, launch protocol, all trajectories and observer files, every exit receipt, and analysis scripts.

```sh
python /extracted/analyze.py /extracted /new/output
```

The audit also requires the pinned original ensemble at the recorded repository path for full-prefix comparison.
No primary results are replaced and no whole-paper completion credit is assigned.
