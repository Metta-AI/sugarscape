# Sugarscape replication program

Owner: [Metta-AI/sugarscape](https://github.com/Metta-AI/sugarscape).
Engine upstream: [nkremerh/sugarscape](https://github.com/nkremerh/sugarscape), initially pinned to
`e6559bed1a6bda71bb07a3498dae862ea899b10f`.
The [Coworld wrapper](https://github.com/Metta-AI/coworld-sugarscape) consumes that engine separately.

Goal: reproduce the Sugarscape results of at least ten distinct papers.
Foundational book chapters, multiple figures from one paper, and repeated versions do not count as separate papers.
Distinct research papers published in conference proceedings do count.
The papers below are candidates, not completed replications.

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
An unexplained discrepancy or failed run does not count.

Status vocabulary: candidate → specified → running → discrepancy / partial / replicated / validated-negative.
Use `replicated` only after all declared Sugarscape targets pass their predeclared criteria.
Explicitly exclude unrelated case studies from papers containing several models.

## Candidate papers

| ID | Paper | Initial Sugarscape target | Status |
| --- | --- | --- | --- |
| mcculloch-2022 | McCulloch et al., [Calibrating Agent-Based Models Using Uncertainty Quantification Methods](https://www.jasss.org/25/2/1.html) (2022) | Figures 3–6: stabilization, ensemble variance, history matching, posterior | completed mixed study; validated-negative exact stabilization, conditional posterior agreement; [PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/3) |
| kremer-herman-2024 | Kremer-Herman, Gupta, Severson, [Blueprints for Machine Ethics: A Digital Terrarium for Socio-Ethical Artificial Agent Decisionmaking](https://doi.org/10.1109/ACCESS.2024.3519139) (2024) | Table 3 and homogeneous-society population/resource outcomes; 500 seeds, 5,000 steps | original 2,000 configurations recovered; corrected pilots match all 5,001 observations byte for byte; all four original 500-seed ensembles running; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/6) |
| kremer-herman-2023 | Kremer-Herman and Gupta, Replacing Sugarscape: A Comprehensive, Expansive, and Transparent Reimplementation (SimuTools 2023; proceedings 2024); [full paper](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2023:replacing-sugarscape.pdf) | Three baseline scenarios, twenty additional seeds, seventeen examples, and trade/lending comparisons | twenty original disease seeds complete (10,020 observations); reported extinction seeds eradicate disease in verified observer replays; historical alignment unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/10) |
| bigbee-2007 | Bigbee, Cioffi-Revilla, Luke, [Replication of Sugarscape Using MASON](https://citeseerx.ist.psu.edu/document?doi=0e41ff02af3ab5578a925a3cf7c81f4262bbf0c0&repid=rep1&type=pdf) (2007) | Rule-set outcomes and documented replication failures | all seventeen draft scenarios run twice; corrected reproduction invariants pass 17,034 observations; historical alignment outstanding; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/7) |
| kiran-2014 | Kiran, [Using FLAME Toolkit for Agent-Based Simulation: Case Study Sugarscape Model](https://arxiv.org/abs/1408.3441) (2014) | Three spatial initialization scenarios; separate behavioral results from hardware timings | [source audit](source-audits/kiran-2014.json): six Table 5 targets extracted; original C/XML and initialization details unresolved |
| oremland-2014 | Oremland and Laubenbacher, [Optimization of Agent-Based Models](https://www.jasss.org/17/2/6.html) (2014) | Sugarscape taxation schedule, revenue, population, and reduced-model comparison | [source audit](source-audits/oremland-2014.json): 2014 dissertation Appendix B recovered; landscape, tax timing, and negative-wealth handling unresolved |
| raimbault-2019 | Raimbault et al., [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html) (2019) | Sugarscape spatial sensitivity and Gini outcomes | 24/24 archived Table 4 statistics reproduced; three simulations exactly replayed at historical horizon; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/5) |
| carrella-2021 | Carrella, [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html) (2021) | Sugarscape parameter recovery comparison and error tables | complete author replay: 750,000/750,000 statistics across 5,000 inputs; 30 estimator table entries matched in successful runs; remaining forest/neural runs and runtime discrepancies unresolved; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/4) |
| stevenson-2021 | Stevenson, [Dynamics of Wealth Inequality in Simple Artificial Societies](https://arxiv.org/abs/2108.11892) (2021) | Equilibrium/non-equilibrium inequality and reproduction-cost experiments | two complete 100-seed, 100,000-cycle ensembles; discrepancies and twenty-run birth-threshold sensitivity audited; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/8) |
| buzing-2005 | Buzing, Eiben, Schut, [Emerging Communication and Cooperation in Evolving Agent Societies](https://www.jasss.org/8/1/2.html) (2005) | Cooperation pressure versus communication and survival | controlled seed variant repeats all ten output files; harvest and landscape differences remain; [study PR](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/9) |
| flentge-2001 | Flentge, Polani, Uthmann, [Modelling the Emergence of Possession Norms using Memes](https://www.jasss.org/4/4/3.html) (2001) | Possession norms, aggression, and population outcomes | candidate |
| pan-2011 | Pan, [Rebellion on Sugarscape: Case Studies for Greed and Grievance Theory of Civil Conflicts using Agent-Based Models](https://arxiv.org/abs/1908.06883) (2011 proceedings; 2019 arXiv upload) | Published policy case studies and rebellion outcomes | [source audit](source-audits/pan-2011.json): twelve scenario targets and explicit rules extracted; hardship mapping, scheduling, map, and original implementation unresolved |

Dogan (2026), [Policy Robustness Under Accelerating Automation](https://github.com/dgnerg867-ux/sugarscape), is an additional unpublished working-paper study.
All 205 canonical runs and horizon, composition, and multiplier experiments match deposited outputs; original/corrected levy and remaining fork/robustness experiments remain active in [PR 11](https://app.graphite.dev/github/pr/Metta-AI/sugarscape/11).
It supplements the existing candidates rather than replacing them.

The 1996 Epstein–Axtell book and Kehoe's [formal specification](https://arxiv.org/abs/1505.06012)
are baseline references, outside the ten-paper count.
Paper-specific variants must remain explicit: superficially similar Sugarscape implementations can implement different models.

## Current state

2026-10-15: created the organization-owned engine fork and candidate inventory.
Completed studies: **1 / at least 10**. Wholly positive paper replications: **0**.
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
Independent fork behavior and remaining estimators remain unfinished.

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
| Carrella | Remaining estimator ensembles, historical stochastic/runtime explanation, and independent fork behavior |
| Raimbault | Full55,000-row reference replay is running; generated-grid comparison and full spatial-sensitivity results remain outstanding |
| Blueprints | All original homogeneous seeds, selfishness and mixed-society experiments, runtime targets, and source-version alignment |
| Replacing | Table3 qualitative classification, trade/lending comparisons, disease discrepancy, and historical control/configuration alignment |
| Bigbee | Published 2007 protocol and implementation alignment; corrected 2011 draft showcases alone are insufficient |
| Stevenson | Evolutionary scenarios, distributions, and unresolved fixed-society growth-rate/mean-age discrepancies; author fitting protocol unknown |
| Buzing | Version 1.2.3 harvesting, scheduling, landscape, communication semantics, and full ten-run condition ensembles |
| Dogan | Remaining levy/per-seed robustness runs, full fork verification, and corrected-levy comparison; native tables pass but accounting and prose discrepancies require interpretation |
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
A separate accounting correction passes all 60 event checks and is undergoing the declared paired 75-run comparison.
Original and forked model sources remain unchanged for faithful reproduction; full fork canonical verification is still pending.

Blueprints independently audits all retained completed prefixes and recovers each of four disk-interrupted seeds without substitution.
All four original schedules have resumed in fresh output directories. No full model ensemble is yet complete.
No partial run, table match, or reporting discrepancy increases the completed-paper count.

Replacing also completes the declared 60-run paired trade/lending diagnostic.
Mean relative increases are 2.421% and 3.359%; maxima are 6.182% and 7.610%.
Unknown historical seeds and measurement windows prevent treating these as confirmation or refutation of the reported 3%/5% claims.
Carrella's full 5,000-input regression-forest workflow has launched with the native settings; no result is claimed before all five folds validate.
