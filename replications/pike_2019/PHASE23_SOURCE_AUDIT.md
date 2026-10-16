# Remaining experiment source map

At Sugarscape revision `585e53398f4f58e89ec184c83bb20819f0e4c96a`:

| Directory | Released behavior | Required paper variations |
| --- | --- | --- |
| Policy-Network | Trade threshold 10; movement policy argument commented out | Phase II thresholds 1/5/10; Phase III movement policy |
| Policy-Explicit | Trade threshold 10; movement policy enabled | Phase II without policy; Phase III with policy; thresholds 1/5/10 |
| Common Resource- one level | Threshold 10; shared-resource policy | Shared-resource threshold comparisons |
| Common Resource- multi-level | Threshold 10; shared-resource policy; group_to_net=True | Nested shared-resource threshold comparisons |

Movement policy selection uses Python's module-level `random.randint`, independently of Mesa's model generator and NumPy.
New diagnostic pilots record all three seeds: Mesa 42, NumPy 0, and module-level random 0.
Original module-level and NumPy states remain unavailable.
No threshold or policy switch has yet been silently applied to these released configurations.

## Nested-resource type mismatch

The selected library revision `99d2091721076df9fff32e8b49a0e33e98c34a6f` assigns `GroupAgent.type = 'group'`.
The multi-level `organization.rules.calc_accumulations` adds nested resources only when `agent.type == 'meta'`.
Thus that branch does not recognize the selected library's group objects.
Its effect on complete trajectories must be measured; source inspection alone does not quantify lost resources or explain paper results.

The example's first commit is `0b43878119421944649e9b77c591da223250d18e`, January 31, 2019 at 14:27:33 -0400.
The library's group refactor, `9c0cf5f`, followed at 14:36:00 that day.
Its preceding revision `9457d475c5cde09500278b86e7e50d404d8425ac` labels objects `meta`.
The shared-resource organization file is unchanged between the initial and selected example revisions.

An unchanged-code pairing of the first examples with that preceding library fails at the first step: the examples already call `net_group`, while the library exposes the older API.
Therefore chronology alone does not provide a clean historical source pair.
The failed runs and tracebacks are preserved externally; no aliases or source patches were inserted to conceal the failure.
Current-revision and explicitly documented corrective experiments must remain separate from paper-fidelity claims.
