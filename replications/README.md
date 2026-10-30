# Sugarscape replication program

[The subsequent ten-study recheck](reviews/2026-10-20/README.md) passes selected native workflows and evidence audits, restores Dogan’s directly runnable figure bundle, and maps the studies into Coworld variants.

**The ten-study method-replication target is met.** [The completion review](completion-2026-10-20.md) links all ten study PRs and their qualifications.
Brearcliffe adds the tenth: 1,600 audited native runs, both parameter interpretations, independent checks and a mixed verdict.

Quera’s complete method review adds the ninth study. Both calibration estimators and all predictive outputs are audited. VarGrad mismatch, partial parameter recovery, and reconstruction choices remain explicit; no validated negative or wholly positive verdict is assigned.

Richmond’s final requirement audit completes its qualified author-code replication. All 84 original conditions and figure analyses are verified. Numerical results reproduce; source defects, ambiguous specifications, historical images, and hardware limitations remain explicit. Corrective controls do not replace the full-grid replay.

Owner: [Metta-AI/sugarscape](https://github.com/Metta-AI/sugarscape).
Engine upstream: [nkremerh/sugarscape](https://github.com/nkremerh/sugarscape), initially pinned to
`e6559bed1a6bda71bb07a3498dae862ea899b10f`.
The [Coworld wrapper](https://github.com/Metta-AI/coworld-sugarscape) consumes that engine separately.

Goal: faithfully reproduce and exercise the Sugarscape methods of at least ten distinct papers.
Exact numerical agreement is reported separately and is not a completion requirement (user clarification, October 19, 2026).
Foundational book chapters, multiple figures from one paper, and repeated versions do not count as separate papers.
Distinct research papers published in conference proceedings do count.
The table distinguishes candidates, unfinished studies, and completed replications.

Current completion count: **ten studies**, including one unpublished working paper. Only one has a wholly positive verdict under its declared scope; numerical agreement is assessed separately.
`study-evidence.json` is the current evidence ledger; dated checkpoint updates remain in the experiment archive.

## Evidence required

Each study gets its own directory and pull request, with follow-up commits for discrepancies.
Before running its confirmatory experiments, record:

1. The paper version, source URL, exact figure/table/claim, and reference-code revision and license.
2. Landscape, scheduling, movement, initialization, death, reproduction, and measurement semantics.
3. Complete configurations, seed schedule, sample sizes, numerical targets, and justified comparison criteria.
4. Commands, dependency versions, engine revision, raw outputs, hashes, plots, and uncertainty across independent runs.
5. A claim-by-claim comparison, including failed results, specification ambiguities, and omitted experiments.

Distinguish **author-code reproduction**, **independent engine replication**, and **qualitative agreement**.
Running the original code alone does not validate the fork's implementation.
A smoke test, matching direction of effect, or hand-picked seed never counts as quantitative replication.
Do not tune parameters, discard seeds, or widen acceptance criteria after inspecting results to manufacture agreement.
If a source claim fails, preserve the failure and investigate the mechanism.
Treat disagreements as possible implementation or configuration errors first. Search for author and third-party implementations.
Validate scheduling, initialization, measurement definitions, dependencies, and statistical uncertainty before assigning a negative verdict.
A validated negative replication counts as a completed study, as explicitly authorized by the user.
An unexplained numerical discrepancy alone does not prevent method completion once implementation fidelity is supported.
Unresolved method choices, incomplete core workflows, and failed required runs still prevent completion.
A numerical mismatch is not automatically a validated negative paper result.

Status vocabulary: candidate → specified → running → partial / completed-method-qualified / replicated / validated-negative.
Use `completed-method-qualified` for executed, evidence-supported methods with explicit assumptions and numerical discrepancies.
Reserve `replicated` for targets passing their declared numerical criteria; do not silently change those criteria.
For each PR, separate the stated method, author-code behavior, our implementation choices, and result-matching diagnostics.
If agreement requires a departure from the stated method, document the departure and report both outcomes.
Do not require recovery of an undocumented historical seed merely to complete a faithful method reproduction.
Explicitly exclude unrelated case studies from papers containing several models.

## Candidate papers

| ID | Paper | Initial Sugarscape target | Status |
| --- | --- | --- | --- |
| mcculloch-2022 | McCulloch et al., [Calibrating Agent-Based Models Using Uncertainty Quantification Methods](https://www.jasss.org/25/2/1.html) (2022) | Figures 3–6: stabilization, ensemble variance, history matching, posterior | completed mixed study; validated-negative exact stabilization, conditional posterior agreement; [PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/3) |
| kremer-herman-2024 | Kremer-Herman, Gupta, Severson, [Blueprints for Machine Ethics: A Digital Terrarium for Socio-Ethical Artificial Agent Decisionmaking](https://doi.org/10.1109/ACCESS.2024.3519139) (2024) | Table 3 and homogeneous-society population/resource outcomes; 500 seeds, 5,000 steps | All 2,000 homogeneous inputs audited; all four Table 3 rows match released plotting semantics. Deposited runtime coverage is 935/1,200. Supplementary coverage is 1,006/100,000, including complete 500-seed selfishness-0.37 and heterogeneous-50 cohorts. Death-rate definition, full sweeps, and historical runtime protocol remain unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/6) |
| kremer-herman-2023 | Kremer-Herman and Gupta, Replacing Sugarscape: A Comprehensive, Expansive, and Transparent Reimplementation (SimuTools 2023; proceedings 2024); [full paper](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2023:replacing-sugarscape.pdf) | Three baseline scenarios, twenty additional seeds, seventeen examples, and trade/lending comparisons | twenty original disease seeds complete (10,020 observations); reported extinction seeds eradicate disease in verified observer replays; historical alignment unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/10) |
| bigbee-2007 | Bigbee, Cioffi-Revilla, Luke, [Replication of Sugarscape Using MASON](https://citeseerx.ist.psu.edu/document?doi=0e41ff02af3ab5578a925a3cf7c81f4262bbf0c0&repid=rep1&type=pdf) (2007) | Rule-set outcomes and documented replication failures | all seventeen draft scenarios run twice; corrected reproduction invariants pass 17,034 observations; historical alignment outstanding; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/7) |
| kiran-2014 | Kiran, [Using FLAME Toolkit for Agent-Based Simulation: Case Study Sugarscape Model](https://arxiv.org/abs/1408.3441) (2014) | Three spatial initialization scenarios; separate behavioral results from hardware timings | [source audit](source-audits/kiran-2014.json): six Table 5 targets extracted; original C/XML and initialization details unresolved |
| oremland-2014 | Oremland and Laubenbacher, [Optimization of Agent-Based Models](https://www.jasss.org/17/2/6.html) (2014) | Complete Sugarscape method: convergence, reduction, rankings, optimization, held-out transfer and timing | **Completed qualified method reconstruction**; historical settings and numerical agreement remain qualified; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/21) |
| christley-2017 | Christley et al., [Optimal control of sugarscape agent-based model via a PDE approximation model](https://doi.org/10.1002/oca.2265) (2017; online 2016) | Tax revenue, survival, and PDE-derived controls | [source audit](source-audits/christley-2017.json): coauthor slides recovered; distinct nondepleting strip model; journal text, original implementation, and control solver unresolved; no runs |
| lima-2024 | Lima and Aguiar, [Towards a Docker-based architecture for open multi-agent systems](https://doi.org/10.11591/ijai.v13.i1.pp45-56) (2024) | Two NetLogo Sugarscape models exchanging agents with JaCaMo; both container-only and host-GUI scenarios | completed qualified author-code feasibility reproduction; both full scenarios, saved state, native GUI and conservation verified; historical binary equivalence unproven; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/19) |
| raimbault-2019 | Raimbault et al., [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html) (2019) | Sugarscape spatial sensitivity and Gini outcomes | 6/6 archived Table 2 and 24/24 Table 4 statistics reproduced; 55,000/55,000 reference simulations audited with 110,000 exact Gini matches; 8,000 generated inputs also audited with 16,000 exact Gini matches; full generated landscapes and spatial sensitivity remain incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/5) |
| carrella-2021 | Carrella, [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html) (2021) | Sugarscape parameter recovery comparison and error tables | completed qualified method reproduction: 5,000 author and 5,000 independent simulations; all 75 finite Table 8 workflows; 38 printed matches and 37 discrepancies retained. Historical randomness/runtime and stochastic equivalence remain qualified; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/4) |
| brearcliffe-2020 | Brearcliffe and Crooks, [Creating Intelligent Agents: Combining Agent-Based Modeling with Machine Learning](https://doi.org/10.1007/978-3-030-83418-0_3) (2021; CSS 2020) | Figures 3–9; sixteen ordered method pairings, fifty repeats each | **Completed qualified author-code method**; all thirty-two cohorts, 1,600 runs and 32,001,600 observations audited. Mixed outcomes and both parameter interpretations retained; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/23) |
| stevenson-2021 | Stevenson, [Dynamics of Wealth Inequality in Simple Artificial Societies](https://arxiv.org/abs/2108.11892) (2021) | Equilibrium/non-equilibrium inequality and reproduction-cost experiments | [Study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/8): both fixed and both conditional evolutionary cases complete 100 seeds at 100,000 cycles. All twenty Table 1 means have source-extracted comparisons. Evolutionary native/trait audits and 96 independent statistical checks pass; fixed-society ages, growth fits, author conventions and remaining figure/Appendix B requirements remain unresolved. No completion credit |
| buzing-2005 | Buzing, Eiben, Schut, [Emerging Communication and Cooperation in Evolving Agent Societies](https://www.jasss.org/8/1/2.html) (2005) | Cooperation pressure versus communication and survival | three 150-run reconstruction/correction grids fully audited; historical fidelity unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/9) |
| buzing-2003 | Buzing, Eiben, Schut, [Evolving Agent Societies with VUScape](https://www.cs.vu.nl/~gusz/papers/ECAL2003-Buzing-Eiben-Schut.pdf) (2003) | Fixed-listening communication, population variation, and cooperation | 200-run grid and actual initialization audited; all populations extinct; historical fidelity unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/12) |
| pike-2019 | Pike, [Multi-Level Mesa](https://arxiv.org/abs/1904.08315) (2019) | Three experimental phases: grouping, movement policies, and shared resources | All 2,100 Phase I–III runs audited and analyzed; 400 threshold-five/ten common-resource runs and 900 timing runs audited; all 400 native common-resource runs contain nonfinite health; 400 archived runs additionally audited; older-runtime controls still produce nonfinite holdings; numerical validity, interpretation and source fidelity remain unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/13) |
| need-for-greed-2024 | Kremer-Herman and Gupta, [The Need for Greed in Artificial Decisionmakers](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:need-for-greed.pdf) (2024) | Full selfishness sweep, outcome proportions and five agent/society measurements | [source audit](source-audits/need-for-greed-2024.json): explicit v2024.1 code pin; 10,100 sweep and 400 baseline configs verified as exact Blueprints archive subsets; 164 shared inputs audited; full experiment and measurements incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/24) |
| serrano-2020 | Serrano and Satoh, [An Agent-Based Model for Exploring Pension Law and Social Security Policies](https://doi.org/10.1007/978-3-030-58790-1_4) (2020 proceedings) | Pension sustainability, inequality and social exclusion | [source audit](source-audits/pensions-2020.json): author code and 1,280 archived runs recovered; 2,304 workbook values reconstructed; full text and paper-specific protocol pending |
| quera-bofarull-2025 | Quera-Bofarull et al., [Automatic Differentiation of Agent-Based Models](https://arxiv.org/html/2509.03303v2) (2025) | Sugarscape gradient validation, sensitivity, and variational calibration | **Completed qualified method reconstruction, mixed outcomes:** 256 gradient baselines, 9,216 perturbations, both 5,000-epoch arms, 4,000 predictive trajectories, independent audits and archive readback. Historical settings and numerical identity unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/15) |
| izquierdo-2009 | Izquierdo et al., [Techniques to Understand Computer Simulations: Markov Chain Analysis](https://www.jasss.org/12/1/6.html) (2009) | Sugarscape appendix: regeneration, irreducibility and aperiodicity | Replicated structural result: finite-state bound, general 135-step regeneration proof, and five/six-step returns; 545 full states independently replayed; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/14) |
| flentge-2001 | Flentge, Polani, Uthmann, [Modelling the Emergence of Possession Norms using Memes](https://www.jasss.org/4/4/3.html) (2001) | Possession norms, aggression, and population outcomes | [source audit](source-audits/flentge-2001.json): 161-page thesis and experiment appendix recovered; source ZIP, executable, landscape and seeds unresolved; no runs |
| pan-2011 | Pan, [Rebellion on Sugarscape: Case Studies for Greed and Grievance Theory of Civil Conflicts using Agent-Based Models](https://arxiv.org/abs/1908.06883) (2011 proceedings; 2019 arXiv upload) | Published policy case studies and rebellion outcomes | [source audit](source-audits/pan-2011.json): twelve scenario targets and explicit rules extracted; hardship mapping, scheduling, map, and original implementation unresolved |
| thaler-2019 | Thaler and Siebers, [A tale of lock-free agents](https://doi.org/10.1186/s40294-019-0067-9) (2019) | Sugarscape population dynamics, timing, scaling and retry ratios; Figures 5–7 and Tables 6–9 | Original code recovered; 53 archived regression estimates and 51 printed timing cells independently reconstructed; Figure 5b reproduced across 50 frozen targets; Figure 5a occupancy matches all 201 positions at step 83 despite its step-50 caption; 45/45 native Table 6/8 timing conditions audited; all six Table 9 timings and thirty retry processes audited; graphical-source control matches benchmark states; full 225-process population and 90-process retry ensembles audited; qualified method reproduction complete; historical hardware/scheduling and time-83 image alignment remain explicit; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/16) |
| thaler-properties-2019 | Thaler and Siebers, [Show me your properties: the potential of property-based testing in agent-based simulation](https://www.researchgate.net/publication/333198243_SHOW_ME_YOUR_PROPERTIES_THE_POTENTIAL_OF_PROPERTY-BASED_TESTING_IN_AGENT-BASED_SIMULATION) (2019) | Sugarscape property demonstrations and full validation appendix | Historical 60-file source unchanged; 35 original tests passed; historical and corrected cohorts audited, including 100 inheritance/control pairs; regional analysis covers 400 combat trajectories; full-resolution migration controls reproduce 2,002 summary rows; recovered NetLogo migration preset exposes four configuration differences; pollution diagnostic validates 262,701 cell records and identifies different diffusion neighborhoods; original model suite and whole-paper verdict pending; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/17) |
| richmond-2023 | Richmond et al., [FLAME GPU 2: A framework for flexible and performant agent based simulation on GPUs](https://doi.org/10.1002/spe.3207) (2023) | Sugarscape Section 4.3, Figures 6 and 11 | All 84 native conditions audited, with 6,600 exact population records and 162 exact resolution rows; state-transition audit complete for observed destinations; historical illustration provenance unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/18) |
| springer-2019 | Springer and Masuhara, [DynaSOAr](https://doi.org/10.4230/LIPIcs.ECOOP.2019.17) (2019) | Sugarscape Figures 10–11: allocator performance and capacity | Original CUDA9.1/GCC5.4 build preserves all511 artifact files. A32x32 control completes10,000 steps;128x128 times out. Timeout phase is unresolved in this uninstrumented run. Full-size benchmarks, equal-heap capacity and independent state validation remain incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/22) |
| openabl-2021 | Cosenza et al., [Easy and efficient agent-based simulations with the OpenABL language and compiler](https://doi.org/10.1016/j.future.2020.10.014) (2021) | Sugarscape code size, cross-backend performance, and distributed scaling | C, MASON and FLAME grids audited; all 13 GPU sizes executed with structural and initialization audits; message-order sensitivity retained; historical timings and distributed scaling incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/20) |

Dogan (2026), [Policy Robustness Under Accelerating Automation](https://github.com/dgnerg867-ux/sugarscape), is an additional unpublished working-paper study.
Completed mixed replication in [PR 11](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/11): all 700 original primary runs and 205 bundled canonical runs complete.
All 653 printed cells and 42 plotted ordinates reproduce; native execution contradicts several mechanism claims.
It supplements the existing candidates rather than replacing them.

A separate [2024 pension-model thesis, deposited in 2025](https://arxiv.org/abs/2504.01242), now has a [source audit](source-audits/firouzian-pensions-2025.json). Its recovered model predates the thesis and disagrees on sampling and experiment settings. It remains a candidate outside the nineteen study PRs.

The 1996 Epstein–Axtell book and Kehoe's [formal specification](https://arxiv.org/abs/1505.06012)
are baseline references, outside the ten-paper count.
Paper-specific variants must remain explicit: superficially similar Sugarscape implementations can implement different models.

## Implementation discovery

- Blueprints: paper-linked [digital-terraria-lab/sugarscape](https://github.com/digital-terraria-lab/sugarscape),
  distinct from the development repository. Original [configuration archives](https://github.com/digital-terraria-lab/datasets) were introduced June 12, 2024.
  Their complete schema matches release `b9ca671ab7591c7b3606f2d76c33eda344d626d1`, May 28, 2024.
  Configuration has 250 agents, 50 diseases, and three tribes; the study runner sets the paper’s 5,000-step horizon.

- McCulloch: [Urban-Analytics/uncertainty](https://github.com/Urban-Analytics/uncertainty), pinned in the study.
- Raimbault: author-linked [JusteRaimbault/SpaceMatters](https://github.com/JusteRaimbault/SpaceMatters),
  revision `270cc7f112b3a999b10e02b0f9525038d6d4754d`. Includes NetLogo source, OpenMOLE workflows, grids, and analysis.
  The paper describes 2,500,000 generated-grid simulations; actual archived parameter counts differ and are documented in the study.
  A small pilot cannot substantiate the full spatial-sensitivity result.
- Carrella: [CarrKnight/nofreelunch](https://github.com/CarrKnight/nofreelunch),
  revision `0400f750063215d06659a203f777b21da2e99231`. Includes the Sugarscape trade model, parameters,
  simulation data, and R calibration notebooks. The companion [freelunch](https://github.com/CarrKnight/freelunch)
  package provides estimators; it is not the simulation model itself.
- Stevenson, Kiran, and Pan: initial GitHub/web searches have not established a paper-specific code repository.
  This is a search status, not evidence that no implementation exists.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/d0128ac66d9a84616cb2a28817383db5e1b8a4c4/replications).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=d0128ac66d9a84616cb2a28817383db5e1b8a4c4 --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/b267f319275dbab9246ecdf1da221c2d170c1a9e/replications) retains raw outputs removed in previous cleanups.
