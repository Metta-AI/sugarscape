# Legacy/refactored Sugarscape comparison

The unchanged legacy Mesa script at author revision `b3b93e474cd20271bbc3ecbb908d587801e3311f`
ran all ten declared seeds 0–9, with 200 initial agents and 100 steps.
An isolated Python 3.11.14 / Mesa 2.4.0 environment is pinned in `environment.json`.
The historical package versions and seeds are not established.
Both Python's global random generator and the Mesa model generator receive each declared seed.

All 1,010 snapshots retain 2,525,000 cell observations and 129,306 live-agent observations.
Independent pairwise Gini calculations agree with the legacy metric within 2.78e-16.
All 127,306 survivor transitions satisfy toroidal movement and harvest/metabolism bounds.
Occupancy uniqueness, capacity bounds, trait constancy, population monotonicity,
and necessary death conditions also pass. This is not a full transition replay.

The default legacy and refactored environments differ at 134 of 2,500 capacity cells.
Total capacities are 3,638 and 3,772, respectively.
Legacy patches initialize uniformly from zero to capacity; the rewrite initializes every patch at capacity.
The legacy model observes and acts sequentially after regrowth;
the rewrite observes agents as a batch before applying actions and then regrows resources.
Agent initialization and random-number consumption also differ.

Mean final populations are 118.1 for legacy and 91.1 for the prior refactored controls.
These runs share seed labels, not realized initial conditions or scheduling.
The outcome difference cannot be attributed to a single change, and is not a negative paper verdict.
This demonstrates that the rewritten defaults cannot simply stand in for the legacy model in a fidelity claim.

The complete compressed native states, original runner, independent audit, logs,
and package inventory are retained in `native-evidence.tar.gz`.
Every member was compared byte-for-byte with retained evidence.
Legacy LLM prompts, paper settings, Figure 10 targets and historical provenance still require investigation.
No paid inference or completed-paper credit is claimed.
