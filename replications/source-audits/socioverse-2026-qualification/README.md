# SocioVerse2 Sugarscape source qualification

Candidate: [SocioVerse2, September 2026 preprint](https://arxiv.org/abs/2609.24911v1), Case Study 1 and Appendix A.2.
The author-linked [benchmark repository](https://github.com/Lishi905/SocioVerse-ABM) is pinned at `b3b93e474cd20271bbc3ecbb908d587801e3311f`.
Its complete Sugarscape scope includes the rule control and all three LLM conditions in Figure 10.
No separate credit would be assigned to the cited companion benchmark's same experiment.

Ten unchanged native rule controls ran 200 agents for 100 steps, retaining 1,010 snapshots.
Seeds 0–9 are an explicitly reconstructed schedule; historical seeds were not recovered.
Source/configuration hashes, complete timestep sequences, final-metric consistency, finite means,
Gini bounds, and nonincreasing population were checked.
This is execution qualification, not an independent model-transition audit.

Using the paper's outcome-vector formula against these ten runs' own mean yields
mean consistency 0.9510747196 and sample standard deviation 0.0337109064.
No comparison with the published Sugarscape point is claimed yet.
These numbers are not the repository's separate action-agreement score.

Two fidelity issues must be resolved before paid inference:

- The refactored Sugarscape LLM call sets temperature 0.2 and an 8-token cap; the paper gives 0.7 and a 256-token maximum.
  Eight tokens is within the stated upper bound; its numerical effect is untested.
- The shared evaluator computes action agreement, whereas the paper describes relative deviation of mean wealth, survivors, and Gini.

The repository also retains legacy Mesa scripts. Their model dynamics, prompts, and runtime need comparison with the refactored path.
The exact seeds, model snapshots, Figure 10 values and uncertainty, and all nine LLM runs remain unresolved.
No paid inference was launched. This candidate adds neither a study PR nor completed-paper credit.

The archive retains the exact external runner, configurations, native outputs, logs, hashes, and qualification audits.
Every member was compared byte-for-byte with its retained source.
