# GPU timing comparison across different systems

The complete native size grid is compared with all 13 published Figure 4 GPU points.
Native timings are one observation per condition on an H100 system.
Published timings came from the paper's Titan Xp and i5-4690K system.
CPU, storage, GPU, toolchain, and potentially historical dependency revision differ.
The ratios below are descriptive and do not establish a historical speed reproduction.

| Requested cells | Published seconds | Native whole-runner seconds | Native engine span seconds | Native / published |
| ---: | ---: | ---: | ---: | ---: |
| 250 | 1.402959 | 0.58 | 0.095981 | 0.4134 |
| 500 | 1.196057 | 0.60 | 0.152232 | 0.5016 |
| 1,000 | 1.310000 | 0.69 | 0.246879 | 0.5267 |
| 2,000 | 1.565774 | 0.90 | 0.447645 | 0.5748 |
| 4,000 | 2.096863 | 1.31 | 0.835338 | 0.6247 |
| 8,000 | 2.923950 | 2.15 | 1.635927 | 0.7353 |
| 16,000 | 4.820908 | 3.86 | 3.254298 | 0.8007 |
| 32,000 | 8.991795 | 7.22 | 6.459839 | 0.8030 |
| 64,000 | 17.029216 | 13.87 | 12.789343 | 0.8145 |
| 128,000 | 32.624156 | 27.81 | 26.086670 | 0.8524 |
| 256,000 | 64.727384 | 58.45 | 55.444559 | 0.9030 |
| 512,000 | 128.874583 | 114.75 | 108.986984 | 0.8904 |
| 1,024,000 | 256.003856 | 230.14 | 218.786531 | 0.8990 |

The largest condition takes 230.14 seconds, versus the digitized 256.003856 seconds.
No uncertainty estimate is inferred from one observation.
Paper-coordinate sensitivity retained in `../paper-targets/figure4.json` is digitization sensitivity, not a timing confidence interval.

![Different-system GPU timing comparison](https://github.com/Metta-AI/sugarscape/blob/acf37262740cf14092345caac51d5a004d6f40a3/replications/openabl_2021/gpu-timing-comparison/comparison.png)

The plot was visually inspected. Both whole-process timing series and their ratios are shown.
The third curve preserves the engine-reported span, which is not isolated kernel time.
The pinned FLAME GPU template starts CUDA-event timing before the iteration loop
and records the stop event afterward; that loop includes XML writes when output is enabled.
Our unchanged generated runner retains the default write on every step.
The historical source/configuration used by the authors is not independently identified.

The released OpenABL benchmark times the whole `run.sh` subprocess after building.
Its GPU `run.sh` invokes `./runner`, which creates the initial XML and executes the engine.
Our GNU time measurement encloses the same runner plus its timeout wrapper;
the two measurements are comparable in scope but do not have identical measurement overhead.
No XML-off control or kernel-only benchmark was substituted for the native workload.

All 13 log exit codes are zero. `comparison.json` pins input log hashes and the digitized targets.
`engine-template-source-audit.json` pins the timer/XML template and relevant line ranges.
The public entry point reproduces the CSV and JSON from retained evidence:

```sh
python replications/openabl_2021/compare_gpu_timings.py NEW_OUTPUT
```

Run the retained `plot.py` beside `timings.csv` with Matplotlib installed to reproduce the plot.
Timing fidelity and distributed scaling remain open; this comparison adds no completed-paper credit.
