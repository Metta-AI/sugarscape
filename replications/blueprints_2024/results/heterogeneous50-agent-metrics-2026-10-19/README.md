# Heterogeneous50 agent outcomes

All 500 original trajectories and 1,781,148 observations are checked against the complete population audit before aggregating agent metrics.
Each archive and trajectory hash, observation count, contiguous tick sequence, and population sum is revalidated.
The pinned PDF page 18 was visually inspected: Figure 18 spans 0–350 wealth, Figure 19 spans 10–20 timesteps, and Figure 21 spans 0–70 age.

| Recorded metric | Observed rows, including / excluding initial | Zero-extended, including / excluding initial | Published median ink |
| --- | --- | --- | --- |
| Mean wealth | 159.844852 / 159.866867 | 131.590893 / 131.607257 | 158.694794–161.101199 |
| Mean time to live | 17.854092 / 17.869964 | 17.096746 / 17.098715 | 17.811924–17.887188 |
| Mean age at death | 60.654839 / 60.666970 | 60.654839 / 60.666970 | 60.416107–60.887001 |

Observed-duration averages match the plotted median in all three figures. Zero extension fails the graphical comparison for wealth and time to live.
This supports observed-duration averaging for these metrics in this condition, but does not prove the historical plotting implementation.
All four conventions were retained; none was discarded after comparison.
Zero-padding an extinct society's per-agent metric is an explicit sensitivity convention, not a claim that nonexistent agents have a measured value.

The author code's `meanAgeAtDeath` is a per-update mean over deaths, with zero on updates without deaths.
This analysis weights recorded timesteps equally; it does not pool individual deaths across time.
The time-to-live metric uses `findTimeToLive(True)`, the age-limited form. Source definitions and revision hashes are retained.

Exact rational calculations preserve the recorded decimal values. Independent R checks all 12 medians within 2.85e-14 absolute error.
Repeating archive traversal, aggregation, and PDF extraction yields byte-identical output.
The medians are of per-run temporal means, following the surrounding heterogeneous analysis; exact historical choices remain unverified.
Ink bounds are not confidence intervals. One complete condition does not establish the full sweep or paper, and no new study-completion credit is added.
