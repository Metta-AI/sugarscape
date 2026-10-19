# Death plotting history and executed author helper

The pinned v2024.1 plotting helper uses starvation plus combat deaths divided by population.
The author's v2024.3 release, commit `cc0408afbb09d8d124ce6f7e6b1844d202d0f8b6` dated August 23, 2024, adds aging deaths.
It sets the plotted value to zero when population is zero and divides summed deaths across runs by summed population at each timestep.
This release predates the December 2024 paper but differs from the v2024.1 simulation release explicitly named by the paper.
Neither helper establishes the supplementary Figure 20 plotting implementation.

We executed v2024.3's unmodified `findMeans` function on all 500 audited v2024.1 heterogeneous50 trajectories.
The function was extracted with Python's AST to avoid running unrelated CLI and plotting setup.
Its input arrays use the author's zero-initialized 5,001-step layout and sum each observed trajectory into its timestep positions.
Every source archive and trajectory hash was checked. The execution retains all 500 runs.

The resulting death-rate series has temporal mean 1.558741% including the initial row, or 1.559052% excluding it.
Its temporal median is 1.540366% or 1.540369%, respectively.
These diagnostic summaries remain above Figure 20's previously extracted 1.204152–1.399848% ink interval.
They are not substituted for the paper's stated median-across-seeds statistic.
All recorded disease deaths sum to zero, so adding or removing that cause cannot explain the earlier difference.

Independent R recomputes all 5,001 per-timestep rates from the retained death-count and population sums, agreeing within 1.78e-15 percentage points.
It also reproduces the four temporal summaries. This checks the executed helper's arithmetic, not historical Figure 20 provenance.

A current author-organization repository listing and datasets tree show no identified supplementary analysis script.
Two targeted GitHub code searches returned no hits; this is not proof that the script does not exist.
Queries and raw receipts are retained. The archived author scripts retain their MIT license.
The discrepancy remains unresolved, with no negative-replication or whole-paper completion credit.
