# Sugarscape replication program

Owner: [Metta-AI/sugarscape](https://github.com/Metta-AI/sugarscape).
Engine upstream: [nkremerh/sugarscape](https://github.com/nkremerh/sugarscape), initially pinned to
`e6559bed1a6bda71bb07a3498dae862ea899b10f`.
The [Coworld wrapper](https://github.com/Metta-AI/coworld-sugarscape) consumes that engine separately.

Goal: reproduce the Sugarscape results of at least ten distinct papers.
Book chapters, multiple figures from one paper, and repeated versions of a paper do not count as separate papers.
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

Status vocabulary: candidate → specified → running → discrepancy / partial / replicated.
Use `replicated` only after all declared Sugarscape targets pass their predeclared criteria.
Explicitly exclude unrelated case studies from papers containing several models.

## Candidate papers

| ID | Paper | Initial Sugarscape target | Status |
| --- | --- | --- | --- |
| mcculloch-2022 | McCulloch et al., [Calibrating Agent-Based Models Using Uncertainty Quantification Methods](https://www.jasss.org/25/2/1.html) (2022) | Figures 3–6: stabilization, ensemble variance, history matching, posterior | specified; source audit underway |
| kremer-herman-2024 | Kremer-Herman, Gupta, Severson, [Blueprints for Machine Ethics: A Digital Terrarium for Socio-Ethical Artificial Agent Decisionmaking](https://doi.org/10.1109/ACCESS.2024.3519139) (2024) | Table 3 and homogeneous-society population/resource outcomes; 500 seeds, 5,000 steps | candidate |
| kremer-herman-2023 | Kremer-Herman and Gupta, Replacing Sugarscape: A Comprehensive, Expansive, and Transparent Reimplementation (SimuTools 2023; proceedings 2024); [conference slides](https://simutools.eai-conferences.org/2023/static/uploads/sites/782/2024/01/Replacing-Sugarscape-EAI-SimuTools-2023.pdf) | Acquire full chapter and map its original replication claims to engine examples | candidate; full chapter needed |
| bigbee-2007 | Bigbee, Cioffi-Revilla, Luke, [Replication of Sugarscape Using MASON](https://citeseerx.ist.psu.edu/document?doi=0e41ff02af3ab5578a925a3cf7c81f4262bbf0c0&repid=rep1&type=pdf) (2007) | Rule-set outcomes and documented replication failures | candidate |
| kiran-2014 | Kiran, [Using FLAME Toolkit for Agent-Based Simulation: Case Study Sugarscape Model](https://arxiv.org/abs/1408.3441) (2014) | Three spatial initialization scenarios; separate behavioral results from hardware timings | candidate |
| oremland-2014 | Oremland and Laubenbacher, [Optimization of Agent-Based Models](https://www.jasss.org/17/2/6.html) (2014) | Sugarscape taxation schedule, revenue, population, and reduced-model comparison | candidate |
| raimbault-2019 | Raimbault et al., [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html) (2019) | Sugarscape spatial sensitivity and Gini outcomes | candidate |
| carrella-2021 | Carrella, [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html) (2021) | Sugarscape parameter recovery comparison and error tables | candidate |
| stevenson-2021 | Stevenson, [Dynamics of Wealth Inequality in Simple Artificial Societies](https://arxiv.org/abs/2108.11892) (2021) | Equilibrium/non-equilibrium inequality and reproduction-cost experiments | candidate |
| buzing-2005 | Buzing, Eiben, Schut, [Emerging Communication and Cooperation in Evolving Agent Societies](https://www.jasss.org/8/1/2.html) (2005) | Cooperation pressure versus communication and survival | candidate |
| flentge-2001 | Flentge, Polani, Uthmann, [Modelling the Emergence of Possession Norms using Memes](https://www.jasss.org/4/4/3.html) (2001) | Possession norms, aggression, and population outcomes | candidate |
| pan-2019 | Pan, [Rebellion on Sugarscape: Case Studies for Greed and Grievance Theory of Civil Conflicts using Agent-Based Models](https://arxiv.org/abs/1908.06883) (2019) | Published policy case studies and rebellion outcomes | candidate |

The 1996 Epstein–Axtell book and Kehoe's [formal specification](https://arxiv.org/abs/1505.06012)
are baseline references, outside the ten-paper count.
Paper-specific variants must remain explicit: superficially similar Sugarscape implementations can implement different models.

## Current state

2026-10-15: created the organization-owned engine fork and candidate inventory.
No paper is yet replicated. The first study audits McCulloch et al.'s released Mesa implementation against the DTL engine.
Nexus 0.15.1 GitHub-backed login failed twice during setup; its activity-note write also failed while signed out.
Repository creation and public-source access succeeded independently.
