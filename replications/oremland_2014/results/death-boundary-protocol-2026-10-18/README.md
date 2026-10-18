# Paired death-boundary diagnostic

The [article](https://www.jasss.org/17/2/6.html) contains conflicting instructions: Appendix B prose specifies death at zero sugar; Algorithm 3, line 19 specifies death below zero.
Earlier ensembles follow the prose. Neither convention is established author-code behavior.

The retained native probe runs both rules, both clocks, and both payment treatments for 50 steps with zero tax rates.
All 408 states pass audit. The prose rule leaves no zero-sugar survivors; the algorithm rule leaves as many as 11.
The first probe failed when reopening a model on one NetLogo workspace. Its failure log is retained; the successful probe uses one workspace per model.

The new 37,600-request protocol changes only the death comparison in the independent-stream experiment.
Policies, requests, seeds, maps, tax clocks, and horizons are unchanged. Four workers have a one-hour global execution bound.
Execution is pending audit; this directory supplies the frozen protocol and preparation command, not completed ensemble results.

With negative-only death, literal negative tax payments can restore a dying agent to zero and preserve its life.
Adding refunds therefore measures positive payments along the literal trajectory; it does not reproduce a clipped-payment counterfactual.
The auditor labels that objective accordingly and bounds refunds by 40 times initial population (ten tax steps, metabolism at most four).

The updated auditor rechecks 17,600 retained prose-rule runs. Both resulting analysis CSVs are byte-identical to the previous analysis.
No paper completion or validated negative result is claimed.

```sh
python prepare_death_boundary.py /path/to/completed-independent-streams /path/to/new-death-diagnostic
# Use the unchanged run_rankings.py launcher, then:
python audit_ranking_model.py /path/to/new-death-diagnostic MODEL /path/to/new-audit --seed-design independent --death-boundary negative
```
