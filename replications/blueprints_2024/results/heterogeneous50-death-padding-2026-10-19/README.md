# Extinction handling does not resolve the death-rate discrepancy

This post-discrepancy diagnostic retains all 500 heterogeneous-50 seeds and the previously audited 1,781,148 observations. It compares positive-population rows, observed rows with a zero rate assigned at population zero, and zero extension through the full 5,000-step horizon. Each convention is evaluated with and without initial state, using both reported-all-cause and starvation-plus-combat numerators.

All twelve medians remain outside Figure 20's 1.204152–1.399848% ink interval. For all reported causes, observed-duration medians are 1.648438–1.648768%; fixed-horizon medians fall to 1.496749–1.497048%. Starvation-plus-combat fixed-horizon medians are 0.151678–0.151708%. Assigning zero at the terminal zero-population row alone does not change these medians.

The calculation accounts for 719,352 unobserved future rows and 150 terminal zero-population observations. The original accumulators retain 152 all-cause deaths at zero population; those counts are not silently deleted. Assigning their percentage to zero is an explicit plotting convention, not a claim that no death occurred.

The historical author helper zero-fills arrays and assigns zero at a zero denominator. However, it aggregates across runs before dividing; this per-run diagnostic is not asserted to be the historical Figure 20 procedure. It rules out the tested zero-padding convention as a sufficient explanation, without establishing a negative paper result.

Independent R verifies all twelve medians and row/death counts with zero numerical difference, using the same previously native-audited accumulators. Fresh repeated analysis is byte-identical. These checks do not repeat the native trajectory audit. An initial exact-baseline assertion exposed changed floating-point operation order; the corrected calculation restores the original order and retains exact baseline identity. The failed script and numerical deltas remain preserved.

No simulations, exclusions, parameter changes, or completed-paper credit are added.
