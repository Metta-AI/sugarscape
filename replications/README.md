# Sugarscape replication program

Owner: [Metta-AI/sugarscape](https://github.com/Metta-AI/sugarscape).
Engine upstream: [nkremerh/sugarscape](https://github.com/nkremerh/sugarscape), initially pinned to
`e6559bed1a6bda71bb07a3498dae862ea899b10f`.
The [Coworld wrapper](https://github.com/Metta-AI/coworld-sugarscape) consumes that engine separately.

Goal: faithfully reproduce and exercise the Sugarscape methods of at least ten distinct papers.
Exact numerical agreement is reported separately and is not a completion requirement (user clarification, October 19, 2026).
Foundational book chapters, multiple figures from one paper, and repeated versions do not count as separate papers.
Distinct research papers published in conference proceedings do count.
The table distinguishes candidates, unfinished studies, and completed replications.

Current completion count: **six studies**, including Carrella’s and Thaler’s qualified method reproductions.
The dated progress entries below retain earlier criteria and counts; `study-evidence.json` is the current evidence ledger.

The [new $100 continuation budget](budgets/continuation-2026-10-19/README.md) reserves $20 across three bounded tasks. Need for Greed now has 757 audited original inputs; Richmond’s five declared method controls passed 3,964,000 post-step state checks; its GPU node is stopped. Neither adds a completed study.

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
| oremland-2014 | Oremland and Laubenbacher, [Optimization of Agent-Based Models](https://www.jasss.org/17/2/6.html) (2014) | Sugarscape taxation schedule, revenue, population, and reduced-model comparison | [Study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/21): 2,000 diagnostic runs audit 51,000 paired states and 500,936 tax events; another 20,000 convergence runs cover 100 reconstructed policies and both clocks. Mean deaths change by at most 0.91 agents from 50 to 100 seeds, but SD changes reach 24%; 2,538,400 reduced-model and 10,000 independent full-size ranking runs audited; concordance differs from Figure 10. The GUI extinction crash is repaired with 400 exact reference comparisons and a complete extinction workflow. Four small-grid ensembles completed with 405,245 exact retained-prefix matches. A source conflict on zero-sugar death now has a native 408-state probe and a completed paired 37,600-request sensitivity: mortality changes in 37,223 pairs and algorithm-rule 40x40 mortality concordance is .5854/.5511; the 37,600-run seed-design diagnostic is fully audited against its own reference, with 40x40 pooled mortality linear concordance .8686/.8695; no validated negative replication or completion credit |
| christley-2017 | Christley et al., [Optimal control of sugarscape agent-based model via a PDE approximation model](https://doi.org/10.1002/oca.2265) (2017; online 2016) | Tax revenue, survival, and PDE-derived controls | [source audit](source-audits/christley-2017.json): coauthor slides recovered; distinct nondepleting strip model; journal text, original implementation, and control solver unresolved; no runs |
| lima-2024 | Lima and Aguiar, [Towards a Docker-based architecture for open multi-agent systems](https://doi.org/10.11591/ijai.v13.i1.pp45-56) (2024) | Two NetLogo Sugarscape models exchanging agents with JaCaMo; both container-only and host-GUI scenarios | completed qualified author-code feasibility reproduction; both full scenarios, saved state, native GUI and conservation verified; historical binary equivalence unproven; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/19) |
| raimbault-2019 | Raimbault et al., [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html) (2019) | Sugarscape spatial sensitivity and Gini outcomes | 6/6 archived Table 2 and 24/24 Table 4 statistics reproduced; 55,000/55,000 reference simulations audited with 110,000 exact Gini matches; 8,000 generated inputs also audited with 16,000 exact Gini matches; full generated landscapes and spatial sensitivity remain incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/5) |
| carrella-2021 | Carrella, [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html) (2021) | Sugarscape parameter recovery comparison and error tables | completed qualified method reproduction: 5,000 author and 5,000 independent simulations; all 75 finite Table 8 workflows; 38 printed matches and 37 discrepancies retained. Historical randomness/runtime and stochastic equivalence remain qualified; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/4) |
| brearcliffe-2020 | Brearcliffe and Crooks, [Creating Intelligent Agents: Combining Agent-Based Modeling with Machine Learning](https://doi.org/10.1007/978-3-030-83418-0_3) (2021; CSS 2020) | Figures 3–9; sixteen ordered method pairings, fifty repeats each | Fifteen released-code cohorts and six paper-table cohorts complete; 1,077 audited inputs and 21,541,077 observations. Final released successes audited; disjoint25-input recovery runs under$2cap; paper-table execution continues; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/23) |
| stevenson-2021 | Stevenson, [Dynamics of Wealth Inequality in Simple Artificial Societies](https://arxiv.org/abs/2108.11892) (2021) | Equilibrium/non-equilibrium inequality and reproduction-cost experiments | [Study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/8): both fixed and both conditional evolutionary cases complete 100 seeds at 100,000 cycles. All twenty Table 1 means have source-extracted comparisons. Evolutionary native/trait audits and 96 independent statistical checks pass; fixed-society ages, growth fits, author conventions and remaining figure/Appendix B requirements remain unresolved. No completion credit |
| buzing-2005 | Buzing, Eiben, Schut, [Emerging Communication and Cooperation in Evolving Agent Societies](https://www.jasss.org/8/1/2.html) (2005) | Cooperation pressure versus communication and survival | three 150-run reconstruction/correction grids fully audited; historical fidelity unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/9) |
| buzing-2003 | Buzing, Eiben, Schut, [Evolving Agent Societies with VUScape](https://www.cs.vu.nl/~gusz/papers/ECAL2003-Buzing-Eiben-Schut.pdf) (2003) | Fixed-listening communication, population variation, and cooperation | 200-run grid and actual initialization audited; all populations extinct; historical fidelity unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/12) |
| pike-2019 | Pike, [Multi-Level Mesa](https://arxiv.org/abs/1904.08315) (2019) | Three experimental phases: grouping, movement policies, and shared resources | All 2,100 Phase I–III runs audited and analyzed; 400 threshold-five/ten common-resource runs and 900 timing runs audited; all 400 native common-resource runs contain nonfinite health; 400 archived runs additionally audited; older-runtime controls still produce nonfinite holdings; numerical validity, interpretation and source fidelity remain unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/13) |
| need-for-greed-2024 | Kremer-Herman and Gupta, [The Need for Greed in Artificial Decisionmakers](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:need-for-greed.pdf) (2024) | Full selfishness sweep, outcome proportions and five agent/society measurements | [source audit](source-audits/need-for-greed-2024.json): explicit v2024.1 code pin; 10,100 sweep and 400 baseline configs verified as exact Blueprints archive subsets; 164 shared inputs audited; full experiment and measurements incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/24) |
| serrano-2020 | Serrano and Satoh, [An Agent-Based Model for Exploring Pension Law and Social Security Policies](https://doi.org/10.1007/978-3-030-58790-1_4) (2020 proceedings) | Pension sustainability, inequality and social exclusion | [source audit](source-audits/pensions-2020.json): author code and 1,280 archived runs recovered; 2,304 workbook values reconstructed; full text and paper-specific protocol pending |
| quera-bofarull-2025 | Quera-Bofarull et al., [Automatic Differentiation of Agent-Based Models](https://arxiv.org/html/2509.03303v2) (2025) | Sugarscape gradient validation, sensitivity, and variational calibration | [source audit](source-audits/quera-bofarull-2025.json): three calibration pilots and all 256 gradient-baseline seeds independently replayed; 34,560,000 ordinary/differentiated state values match exactly; flow dependency runs; initialization-law discrepancy quantified; full gradient/calibration comparisons remain incomplete; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/15) |
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

## Current state

The [evidence index](study-evidence.json) records 22 studies with pinned commits and README hashes.
Four studies are complete: two mixed studies, one positive structural replication, and one qualified author-code feasibility reproduction.
The remaining eighteen are incomplete; audited cohorts and operational launches do not add paper credit.
Active-study refreshes cover Carrella, Blueprints, and Brearcliffe; their checked commits and evidence counts appear in the index.
Earlier checked entries retain their recorded dates; other entries remain dated snapshots of their pinned commits.
Evidence-file counts are inventory checks, not scientific acceptance criteria.

- Carrella: both complete 5,000-input simulation ensembles and all required estimator sizes are audited. All 75 finite Table 8 entries are evaluated: 38 printed-precision matches and 37 unresolved discrepancies. The full five-fold GAM interval replay passes exact output, random-state, and aggregate checks. The complete historical-runtime control also passes audit: none of its five scores matches the paper, while final random states match the modern replay. Runtime sensitivity is confirmed; discrepancies remain unresolved.
- Raimbault: All 55,000 reference inputs audited, with 110,000 exactly reproduced Gini measurements. The repaired 8,000-input generated run is complete: 16,000 exact Gini comparisons and 31 morphology differences within the predeclared tolerance. This ordered prefix covers population 10 only. Full generated-grid production remains incomplete. Archived morphology reanalysis identifies inconsistent reference-marker scaling, separately from simulation outcomes.
- Blueprints: all 2,000 homogeneous inputs and four Table 3 rows are complete. Published homogeneous curves have been compared; all 19,970 Figure 6 vertices match the later all-cause plotter. Deposited runtime coverage is 935/1,200; its bounded continuation is terminal. Supplementary coverage is 1,006/100,000, with two complete 500-seed conditions. Heterogeneous-50 population, wealth, and several agent metrics have qualified graphical agreement, but Figure 20 death-rate interpretation remains unresolved. The deposited runtime groups do not establish the paper’s separate 500-seed timing claim.
- Brearcliffe: nine of sixteen released-code pairings have complete 50-seed cohorts, independently checked in R. Coverage is 450 released-code plus three paper-table inputs. All 453 audited inputs have verified storage backups. The bounded ensemble continues; discrepancies, parameter interpretations, and implementation fidelity remain under investigation.
- Pike: complete 900-run controlled timing audit. Native timing excludes operations counted by the full-step timer. All 400 threshold-five/ten common-resource runs contain nonfinite health values.
- Thaler lock-free: all 25 native Table 6 conditions audited; 26/27 pairwise rankings match. Hardware differs, so this is not historical timing equivalence. All twenty Table 8 conditions are audited. The original TVar executable segfaulted; the preserved failure receives no scientific verdict. The full population ensemble and its four-condition timing continuation are complete; all 51 Table 6/8/9 timing cells are audited. All 225 population processes across 45 conditions pass independent trajectory audits. All 90 retry processes across eighteen conditions are audited. The matching-instance Table 9 experiment completes all six timings and thirty retry processes. Timing slowdown matches the published direction. The normal32 retry mean is 0.086126 versus published 0.29; counter-source inspection does not explain this discrepancy. Two identical native graphical-source replays match all 201 Figure 5a occupied positions uniquely at step 83, despite its step-50 caption. The completed six-process control audits 51 simulations: Criterion defaults give mean ratio 0.0871433, versus fresh single 0.0894201. Repetition does not explain the published 0.29 in this control; historical execution differences remain unresolved.
- Quera: all 256 gradient-baseline seeds pass independent replay of 614,400 agent updates and 15,360,000 cell updates. All 34,560,000 ordinary/differentiated state values match exactly. The 38,400 derivatives match their 115,200 archived records. Aggregate differences are exactly explained by reduction order. Outside-vision moves occur in every seed at zero-score ties; exact published experiment and calibration settings remain unresolved.
- Thaler properties: complete culture, corrected trade, corrected disease, and combat cohorts extend earlier ensembles. Regional culture diagnostics are exploratory. The original test framework records coverage warnings without enforcing their predicates; native confirmation remains running. All 100 inheritance/control pairs are now audited. Combat-region evidence distinguishes rebirth and culture conversion from invasion. Full-resolution migration controls reproduce 2,002 summary rows and validate 294,792 agent observations. Appendix claims and source/configuration discrepancies still prevent completion.

- Richmond: all 84 native conditions audited; 6,600 population records and 162 resolution rows match the author archive exactly. The state audit reconciles 893,017 observations and 615,829 movements given observed destinations. Figures 11A–C are replotted; native illustrations differ from the released historical images. Original compiler provenance and source-rule fidelity remain unresolved. H100 performance does not establish V100 timing equivalence.

The [Need for Greed study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/24) now tracks 164 audited shared inputs and 815,329 observations. These comprise 64 Bentham baselines and all 100 original seeds at selfishness 0.37. Two sweep readbacks match byte-for-byte; independent NumPy confirms four population medians and endpoint counts. Another 336 baseline raw checks, 10,000 sweep inputs, and paper table/figure comparisons remain. No completed-paper credit is assigned.
Run overlap never adds independent seeds. Corrected-source sensitivities remain separate from historical reproduction.



2026-10-15: created the organization-owned engine fork and candidate inventory.
Completed studies: **4 / at least 10**: three published papers and one unpublished working paper.
Positive structural replication: Izquierdo’s full Sugarscape appendix; mixed outcomes: McCulloch and Dogan. Lima completes a qualified author-code architecture-feasibility reproduction, with explicit historical-runtime limits.
McCulloch et al.: validated negative finding under the declared exact-stability criterion, with conditional posterior agreement.
The independent model matches 660 author-code trajectories and passes 80 complete-world checks across all calibration parameters.
All 51 variance ensembles and both 10,000-particle posterior experiments completed; raw evidence and limitations are in the study PR.
The historical seeds remain unavailable, so this does not disprove the authors' particular original runs.

Carrella: two complete historical NetLogo replays each match all 150 archived statistics.
An initial 24-statistic mismatch was resolved as connector observation timing; it is not negative paper evidence.
Ten linear-regression, ten rejection-estimation, and five full-size local-linear Table 8 values now match published precision.
The complete 5,000-input replay now matches all 750,000 archived statistics; every trajectory is retained and hash-verified.
Its first ten complete trajectories match the separate-call reference path in all 35,070 numeric values.
Both quantile-forest sizes and one-dimensional semiautomatic estimators completed; stochastic comparison remains unresolved.
The small-data generalized additive model differs from the paper. One observation dominates its second-fold error.
Replaying that observation reproduces all 150 archived simulation statistics. Both current and historical fitting runtimes retain the extreme prediction.
No observation was removed, and no negative paper verdict follows from this diagnostic.
The clean semi-automatic 4D run also matches all five printed Table 8 values and independently validates 25,000 predictions.
Both generalized additive model sizes have complete evidence; discrepancies remain unresolved.
The independent simulation and estimator ensembles are now complete; stochastic fidelity and published-score discrepancies remain unresolved.

Raimbault: independent archived-data analysis reproduces all 24 Table 4 statistics.
The initial fresh-simulation mismatch was resolved by restoring the historical 10,000-step horizon.
Both recorded Gini values now match exactly for three archived inputs; complete ensembles remain unfinished.
This was a configuration mismatch, not a negative replication. Neither ongoing study counts toward completion.

Blueprints: the separate author datasets repository supplies all 2,000 homogeneous-society configurations and 500 shared original seeds.
These identify HalfLookaheadBinary models, unlike our provisional plain-model runs. All four provisional batches were stopped and preserved.
Every archived configuration key and nonoperational default matches the May 2024 release; the exact author code revision remains unverified.
Corrected pilots match byte-for-byte across 5,001 observations. Four original 500-seed ensembles are running; none is complete.
No provisional output is counted toward paper replication.
The official lab site supplies the full Blueprints and Replacing Sugarscape PDFs.
Published numeric targets and the remaining selfishness, mixed-society, and runtime archives are now available.

Stevenson: both 100-seed fixed-society ensembles completed 100,000 cycles per seed, with 200,200 validated observations and no extinctions.
Twenty additional predeclared sensitivity runs show that the birth-threshold comparison substantially changes mean age.
A later author algorithm supports the baseline inequality; the 2021 historical rule and age discrepancy remain unresolved.
Both 100-seed growth diagnostics now complete, with 600,000 validated observations and 6,200 exact shared samples against the earlier ensembles.
Fitted growth rates differ from the paper; the author fitting protocol remains unknown. Evolutionary scenarios and distributional targets remain outstanding.

Buzing: recovered and compiled 78 unchanged Java source files from the archived JAWAS release.
The original nominal seed does not control agent-level random generators. A declared variant controls all seven unseeded constructors.
Two independent seed-zero runs match all ten output files; seed one differs, across 2,100 validated scalar observations.
The recovered v2.2b also differs from the paper's v1.2.3 and published experiment defaults. These pilots are not completed replications.

The [engine prerequisite PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/2) fixes resource imports and initial logging.
Study-specific variants remain explicit rather than claiming that DTL matches every source model.
Nexus 0.15.1 GitHub-backed login failed twice during setup; its activity-note write also failed while signed out.
Repository creation and public-source access succeeded independently.


## Cross-study completion gaps

The following requirements remain separate from successful execution or source-output matching:

| Study | Required next evidence |
| --- | --- |
| Carrella | 37 published-score discrepancies, parser-sensitive extreme predictions, independent-model stochastic fidelity, and full historical estimator sensitivity |
| Raimbault | The full 55,000-row reference replay is complete; generated-grid comparison and full spatial-sensitivity results remain outstanding |
| Blueprints | Full selfishness/mixed-society sweeps, remaining 265 deposited runtime inputs, heterogeneous death-rate interpretation, longer horizons, and deposited 100-seed versus reported 500-seed runtime schedule |
| Replacing | Table3 qualitative classification, trade/lending comparisons, disease discrepancy, and historical control/configuration alignment |
| Bigbee | Published 2007 protocol and implementation alignment; corrected 2011 draft showcases alone are insufficient |
| Stevenson | Evolutionary scenarios, distributions, and unresolved fixed-society growth-rate/mean-age discrepancies; author fitting protocol unknown |
| Buzing | Version 1.2.3 harvesting, scheduling, landscape, communication semantics, and full ten-run condition ensembles |
| Dogan | Completed mixed study; original-source fork integration and claim-level verdict verified, with explicit limits on causal interpretation |
| Pike | Numerical validity of all common-resource runs, timing interpretation, platform sensitivity, and historical source fidelity |
| Quera | Exact gradient-figure protocol, source-law discrepancy, prior/loss/validation configuration and full 5,000-epoch calibration |
| Thaler lock-free | Table 9 retry discrepancy, historical performance interpretation, and remaining image resource/label limitations |
| Thaler properties | Original model-suite outcome, faithful Weaver migration/pollution comparison, qualitative appendix outcomes, and remaining source/configuration discrepancies |
| Richmond | Historical illustration/source fidelity, hardware-qualified timing comparisons, resolution histogram interpretation, and source/prose discrepancies |
| Lima | Completed qualified author-code feasibility reproduction; all six original protocol requirements pass. Exact historical binaries and independent-engine replication are not claimed. |
| Kiran, Oremland, Pan, Flentge | Resolve original-model specification gaps and implement their full declared experiments |

Replacing's twenty seasonal seeds now have 10,020 native-parity observations and individual death-cause audits.
Across 180 windows, 21,883 cohort memberships end through aging and 8,140 through starvation; 3,589 survive.
Those dependent memberships distinguish proximate causes but do not establish seasonal causation or paper-level replication.
Both twenty-seed disease revisions complete without the reported extinctions; historical equivalence remains unresolved.

Bigbee's original release contains missing newborn registration and inconsistent empty-cell selection.
The corrected variant passes all population checks in seventeen scenarios and preserves original failing evidence.
These implementation corrections do not establish a negative result for the historical paper.

[Evidence snapshot](study-evidence.json) records checked study commits and unresolved scope.
It is an index into evidence, not an automated scientific completion certificate.

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

## Latest verified components

Replacing completes all twenty reproduction seeds at 2,500 steps and all seventeen released examples.
The baseline matches all 2,452 recoverable Figure 2 vector vertices; its prose timing discrepancy is not a failure to reproduce the plotted curve.
Table 3 classifications and historical control conditions remain unresolved.

Dogan completes all 205 canonical runs, the 45-run longer horizon, 210-run composition sweep, and 60-run multiplier sweep with byte-identical deposited outputs.
Independent fresh-data audits reconstruct main Tables 1–6 and appendix Tables B.1, C.1, and D.1.
The welfare-ranking qualification and composition-ranking exceptions persist in fresh execution.
A native levy observer confirms 762.5 units deducted but only 180.0583 credited across 60 events; its full trajectory matches an uninstrumented run.
Both 75-run levy sweeps and the per-seed calibration study now complete; the paired correction exposes changes in the reported sensitivity bounds.
The full fork canonical run matches the separate original replay byte-for-byte across all 206,010 cells.
All 570 available individual-seed mortality comparisons favor pure means-tested policies; horizon comparisons lack universal-policy arms.
Four of six within-type contribution comparisons contradict the manuscript's equalization claim.
A full native tax observer confirms recurring autonomous wealth taxation, contradicting the claimed absence of that instrument.
Both observed tax trajectories match unobserved runs byte-for-byte and reproduce canonical Gini, mortality, and revenue.
The final claim inventory validates a mixed verdict: numerical replication succeeds, while several mechanism claims contradict native source and outcomes.
This counts as one completed study, not a wholly positive paper replication.

Blueprints independently audits all retained completed prefixes and recovers each of four disk-interrupted seeds without substitution.
All four original schedules have resumed in fresh output directories. No full model ensemble is yet complete.
No partial run, table match, or reporting discrepancy increases the completed-paper count.

Replacing also completes the declared 60-run paired trade/lending diagnostic.
Mean relative increases are 2.421% and 3.359%; maxima are 6.182% and 7.610%.
Unknown historical seeds and measurement windows prevent treating these as confirmation or refutation of the reported 3%/5% claims.
Carrella's full 5,000-input regression-forest workflow has launched with the native settings; no result is claimed before all five folds validate.

Raimbault's retained audit covers 5,966 unique reference inputs and 11,932 exact Gini matches.
Five continuations cover the remaining declared input ranges; the 55,000-run reference and generated-landscape experiment remain incomplete.
Boundary replay overlap is excluded from coverage counts.

The completed Dogan verdict also verifies mortality invariance across all four UHI multipliers in every speed/seed condition.
It distinguishes author-source fork integration from independent engine replication, and preserves the unpublished working-paper status.
No unfinished historical study is removed from the program.

## Additional historical source lead

[Kehoe source audit](source-audits/kehoe-2017-2019.json) pins the author’s Sugarscape repository and recovered 379-page 2017 thesis.
The thesis contains quantified comparisons of synchronous and asynchronous updating.
The current source forces seed zero and doubles landscape sugar for evolution; it is not yet a matched carrying-capacity experiment.
The full related 2017/2019 conference papers and historical configuration still require verification.
This lead adds no completed study and replaces no unfinished candidate.

The historical audit isolates landscape scaling to August 2016 and Qt introduction to 2020.
An unchanged June 2016 core build fails on an inheritance-constructor mismatch; the compiler logs and source hashes are retained.
This is a build failure, not evidence against a scientific result.

The September 2017 native core builds and links without modifications.
A headless initialization returns 400 agents, and two 1,000-cycle synchronous movement pilots exit successfully.
Despite fixed seed zero, 84 population observations differ, first at cycle 2 (392 versus 391).
Both native outputs and the harness are retained; reference repeatability must be resolved before paper comparisons.

A controlled Kehoe thread diagnostic repeats the same native binary with one, two, and four OpenMP threads.
One-thread outputs match exactly; two-thread and four-thread pairs differ in 95 and 86 population observations.
The parallel movement loop calls a shared unsynchronized random generator.
Address/undefined-behavior sanitizers report no violation, but their single-thread trajectory differs from the ordinary build in 97 observations.
Source inspection also finds uninitialized world spice-metabolism bounds read during agent construction.
[Runtime evidence](source-audits/kehoe-runtime-diagnostics/diagnosis.json) preserves both issues; neither successful execution nor a quiet sanitizer establishes fidelity.

A controlled storage-pattern experiment confirms the Kehoe constructor leaves both spice-metabolism bounds uninitialized.
Zero-filled storage yields bounds 0/0; one-filled bytes yield 16,843,009/16,843,009.
Four complete single-thread 1,000-cycle runs repeat within each pattern, and population trajectories match across these two equal-bound patterns.
Thus missing initialization is confirmed, but this diagnostic does not establish it as the cause of the earlier population divergence.
All diagnostic outputs are retained without modifying the author source or treating these artificial patterns as paper settings.

The author-hosted2003VUScape paper has been recovered and its Table2 and Figure2 visually checked.
[Its separate specification](source-audits/buzing-2003.json) uses400agents, richness0.5, growth3, fixed listening, and a500-cycle displayed horizon.
These differ materially from the2005communication experiments; existing2005runs cannot count as a second completed paper.
The earlier text does not resolve fertility-end inheritance, historical source, or message-removal settings.

Seventeen distinct paper studies now have separate PRs; three meet their declared completion criteria.
The remaining fourteen are unfinished. The 2003 VUScape study uses its own published parameters and trajectories.
The 2005 fertility correction passes all 150 paired runs and 11,494,812 births, but changes survival in several paired seeds.
Its COM1 threshold-one survival rises from one to three of ten; implementation sensitivity still prevents a paper-level verdict.

The [author-hosted formal-analysis paper](https://www.cs.vu.nl/~schut/pubs/Eiben/2007a.pdf) provides another distinct Sugarscape-derived candidate.
[Its source audit](source-audits/eiben-formal-2007.json) records 50 traces across five population levels and communication on/off.
The recovered JAWAS archive has no identified generator matching its formal predicates; literal-byte searches alone cannot prove absence.
Visual inspection also finds temporal inequalities that differ from the prose, requiring explicit interpretation before reproducing the property results.
Exact settings, trace boundaries, and original property files remain unresolved. No simulation or completed-study credit is claimed.

The archived newscast cache defect now has [native execution evidence](source-audits/jawas-newscast-native-2026/validation.json).
In a 100-cycle, seed-zero run using archived defaults, the selector returned the wrong message in 803,270 of 811,582 unique-oldest cases.
Passive instrumentation preserves all ten recorded data files byte-for-byte, and the configuration is unchanged.
Changing only the single-candidate return expression changes the final population from 90 to 148.
This is an implementation sensitivity diagnostic, not a paper replication: the archive version, default population, horizon, and parameter grid differ from the Eiben/Schut/Vink experiment.
The paper-level conclusion remains unresolved; these runs establish a concrete defect that must be investigated before interpreting protocol comparisons.

The [original bundled bytecode](source-audits/jawas-newscast-native-2026/bytecode-audit.json) independently confirms both cache-selection expressions.
Its unique-candidate branch returns the last enumerated key, and its tie branch passes `size - 1` to `Random.nextInt`.
The class and source bytes were verified against the original archive members; neither expression originated in our recompilation or instrumentation.
ZIP timestamps record June 2004 for the class and March 2004 for the source.
These unauthenticated timestamps predate the 2005 paper but do not establish the authors’ experimental revision.

Lima now has complete original container and host-native trajectories, plus a controlled native AgentSpeak reload.
All three account for every registered identity. The reload preserves beliefs and plans but fails its score-increment criterion.
A separate packaged GUI attempt lost unarchived trajectories through a collection error; its retained database and logs receive no trajectory credit.
The corrected collector preserves native files in a verified end-to-end collection. Native GUI observation is now documented with screenshots and process provenance.

Portable Lima container, host-native and saved-agent workflows now also complete with independently audited trajectories and conservation.
The portable saved-agent control preserves 39 plans and the retained belief, but again departs with score 1 rather than the declared target 2.
All 953 router deliveries reconcile and all 799 identities are conserved. Two screenshots now show the native Mining World agent moving. The full visual scenario now completes 1,000 steps, 934 transfers and conservation of all 799 identities. Its claim-level audit completes the protocol; exact historical-runtime equivalence remains unproven.

## Additional candidate qualification

[SocioVerse2 (2026)](source-audits/socioverse-2026-qualification/README.md) supplies a runnable Sugarscape benchmark. Ten reconstructed-seed rule controls execute, but the released evaluator and LLM settings need reconciliation with the paper before inference. This source qualification does not change the 18 study PRs or four completed studies.

[The candidate's legacy comparison](source-audits/socioverse-legacy-comparison-2026-10-18/README.md) executes ten original Mesa controls and independently checks their metrics and movement/resource bounds. It identifies 134 changed capacity cells and different initialization/scheduling, so the rewrite is not treated as a historical model substitute.

The latest Blueprints and Richmond refresh pins their pushed heads and parses every tracked JSON result. Blueprints adds two complete original inputs before the local disk guard stops its retry batch. Richmond’s paired GNU input reproduces prior native states exactly; Clang initialization matches the initial illustration but leaves later frames unresolved. Neither study receives completion credit.

Pensions candidate: the complete native deposited grid now passes its audit (1,280 runs, 128 conditions, ten repetitions, 1,000 steps). All 768 condition/metric pairs are compared descriptively with archived outputs in [the evidence report](source-audits/pensions-native-complete-2026-10-18/README.md). Full-paper targets and independent fork behavior remain unvalidated; no completion credit.

The latest verified snapshot includes Blueprints’ 871 audited runtime inputs (2,700,518 observations) and Richmond’s completed XORWOW/all-frame diagnostics. The latter rules out RNG-family replacement alone and a simple frame-index mismatch within the two captured trajectories. Both studies remain incomplete. The seven-input Bentham recovery and independent estimators remain live; no active or queued input is counted as completed.

The latest Blueprints update publishes eight sequential runtime controls with 40,008 byte-identical observations and a frozen 499-input selfishness-0.37 cohort. Its two full parity gates precede bulk execution on eight CPUs, bounded to roughly $8. These controls add no unique supplementary inputs or completed studies.

Stevenson Figure 4 now supplies an initial-population constraint: both ten-trait marginal count sets imply 830 agents. The original vector extraction retains 22 curves and 4,015 vertices, with independent arithmetic and byte-identical fresh replay. This constrains the unimplemented evolutionary experiment but does not establish its missing rules or complete the study.

Stevenson now includes a conditional inherited-trait stable evolutionary ensemble: 100 complete seeds, 50,000 cycles, and 3,194,850 audited inheritance events. All runs reach infertility10/birthcost0 fixation by cycle499. Two homogeneous controls preserve original observations byte-for-byte. Original evolutionary rules, chaotic case, growth-rate and steady-state replication remain outstanding; no completion credit.

Stevenson’s chaotic-parameter extension now completes 100 seeds and 50,000 cycles, with 20,018,826 audited inheritance events. Both evolutionary cases are conditionally implemented, but original settings, steady-state sampling, growth rates and whole-paper agreement remain unresolved. The new analysis preserves stable comparisons and summaries; no completed-study count changes.

Carrella’s fourth independent neural-network fold is audited; four folds cover 20,000 predictions and 3,020,000 input-cell checks. Stevenson’s selected-trait growth adds 200 runs and 600,000 observations, with all 600 optimizer residual sums independently verified. The fitted rates differ under the declared convention, without a validated negative-replication verdict. Completed studies remain four.

Blueprints supplementary checkpoint: 25 additional original selfishness-0.37 inputs pass independent audit for 125,025 full-horizon observations. Coverage reaches 35/100,000 supplementary inputs, including 28/500 at selfishness 0.37. Export and member hashes verify. This completion-order prefix adds no paper completion credit. Study evidence is committed in PR6; the attempted PR-description update was denied by GitHub permissions.

[Masumori and Ikegami (2025)](source-audits/masumori-survival-2025.json) is an additional Sugarscape-style preprint candidate. Two public implementations were inspected at pinned commits. One hard-codes personality probabilities; the other explicitly changes model rules and disclaims strict reproduction. Neither supplies author-code provenance. Original mechanics, seeds, model versions and complete experiment settings remain unresolved; no inference run or completion credit is added.

Brearcliffe and Crooks’ [Creating Intelligent Agents](https://doi.org/10.1007/978-3-030-83418-0_3) is an ongoing native reproduction study. The [source audit](source-audits/brearcliffe-2020.json) retains the original NetLogo model, map, ODD, and author manuscript. The paper requests 50 runs per pairing; the released sweep specifies five and generates unrecorded seeds. The current audited coverage appears above; historical settings remain unresolved.

The Brearcliffe study’s [PR #23](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/23) retains recorder qualifications, full-cohort comparisons, failed checks, and durable evidence receipts. It receives no completed-study credit.

The [market algorithm candidate audit](source-audits/market-genetic-qualification-2026-10-19/README.md) pins the paper-linked author implementation and eleven historical drivers. Released repetitions and horizons differ from the paper; license text and the experimental snapshot remain unresolved. No runs or completion credit are added.

Need for Greed now has six complete endpoint controls: all three baseline/sweep pairs are byte-identical at the preselected seed, preserving both timeout prefixes. The frozen-input reconciliation raises coverage to 170 inputs and 835,607 observations, without double counting. Full ensembles and measurement discrepancies remain unresolved; four completed studies remain.

Carrella historical fitting seeds three and four now pass complete five-fold audits. Their point predictions equal historical seed zero, while all interval bounds differ. Five prospective seeds remain; no printed-score discrepancy is resolved by these seeds. The market-algorithm candidate notebook also references an absent alternate model directory and two absent dataset groups, so current released defaults remain unqualified as the paper experiment.

Need for Greed has a bounded recovery command queued for all 333 baseline inputs whose retained manifests lack raw trajectories. It uses original configurations, compares full outputs with retained hashes, and stops new admissions on mismatch. The six-hour command has a $5.40 conservative ceiling and adds no completion or coverage credit.

Need for Greed population quartiles at selfishness 0.37 now distinguish aggregation order: all tested per-run quantiles fit the nominal curve envelope, while all tested pooled-temporal quantiles fall outside. Independent R arithmetic validates the result after preserving and correcting a type-3 convention mismatch. No new simulations or completed-paper credit are added.

Need for Greed’s two Table IV pilot pairs now pass independent local artifact audits. Each original input produces 5,001 byte-identical CPython/PyPy observations, and all 49 checkpoint members verify after publication. The larger sweep continues; the two pilots remain part of that assignment. Baseline recovery is also running. No completed-study or shared-coverage credit is added.

Need for Greed’s death-rate quartiles now show why median agreement is insufficient. All tested aging-inclusive medians fit the nominal envelope, but neither quartile does; the later author pooled calculation behaves similarly. Fresh raw aggregation and 486 independent R checks pass. Historical measurement fidelity remains unresolved, with no negative-paper or completion credit.

Brearcliffe Q/Q now completes all 50 seeds, bringing coverage to 553 inputs and 11,060,553 observations. Eleven released-code cohorts are complete. Independent R arithmetic and durable archive readback pass. Eight readable endpoint ranges overlap the paper, while six remain unresolved; no equivalence or whole-paper completion is claimed.

The [related reinforcement-learning repository audit](source-audits/market-genetic-rlearners-2026-10-19/README.md) verifies 13 source files, four driver revisions, and eight population traces. Its 200-agent, 10,000-period protocol differs from the Market Algorithm paper; it adds no replication credit.

[Hawick’s 2014 geometry study](source-audits/hawick-2014/audit.json) is an additional candidate. Public author text was located, but original Java code and complete execution settings remain unverified. The author host no longer resolves; publisher/PDF retrieval failed. Targeted GitHub repository search found no match, while code search was unavailable. No simulation or completion credit is added.
