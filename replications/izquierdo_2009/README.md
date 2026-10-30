# Izquierdo et al. (2009): Sugarscape as a Markov chain

Study source: [Techniques to Understand Computer Simulations: Markov Chain Analysis](https://www.jasss.org/12/1/6.html),
specifically its [Sugarscape appendix](https://www.jasss.org/12/1/6/appendixB/EpsteinAxtell1996.html).
The other nine model case studies are outside this Sugarscape replication.

**Status: structural result reproduced.** The [constructive proof](PROOF.md) establishes finiteness, irreducibility, and aperiodicity for the appendix’s formal model.
Together these imply its unique, initial-state-independent limiting and occupation distributions.
This conclusion concerns the full Sugarscape appendix, not the paper’s other nine models or a practical mixing-time claim.

## Model and evidence

`model.py`, shared by the return and regeneration runners, implements the appendix's 50×50 torus with 250 agents and separate growback, movement, and replacement phases.
Agents see cardinal cells, choose maximum sugar and then minimum distance, harvest, metabolize, and lose one unit of remaining life.
Starvation or exhausted life removes an agent; replacements occur after the movement phase at age zero.
Replacement attributes retain the published ranges: vision 1–6, metabolism 1–4, wealth 5–25, and maximum age 60–100.
The state contains landscape sugar and agent position, vision, metabolism, wealth, and remaining life, excluding identifiers and elapsed time.

The paths deliberately select permissible random choices with positive probability.
They are not unbiased simulation samples and do not estimate stationary probabilities or convergence times.
Regeneration paths record every activation permutation, movement destination, replacement order, and newborn.
Return paths retain their seed and full states; movement ties choose an eligible minimum-index cell.
Every replacement is checked against the vacant cells and published attribute ranges.

The paper's Figure 2 has 305 interior desert sites whose cardinal neighbors also have zero capacity.
The witnesses use 250 of those sites, so all agents remain stationary and harvest nothing.
One positive-capacity marker has four extra edge pixels; its radius-three shape is interpreted as capacity three.
This explicit raster interpretation cannot affect the zero-harvest paths.
Figure 1 differs at one cell and yields 306 qualifying sites; the common NetLogo map yields 322.
Both paper figures provide enough sites for this construction, so that difference alone does not refute the paper.

## Return construction

Let the common state have pristine landscape sugar and 250 desert agents with vision one, metabolism one, wealth one, and remaining life 95.
This state is reachable after four steps from an allowed initial population with wealth five and maximum age 99.

All agents starve on the common state's next step. Replace each at its vacated location:

| Return length | Newborn wealth | Newborn maximum age | Subsequent steps | Final wealth | Final remaining life |
| --- | --- | --- | --- | --- | --- |
| 5 | 5 | 99 | 4 | 1 | 95 |
| 6 | 6 | 100 | 5 | 1 | 95 |

Both paths return to the identical full state, with 250 births and zero harvest.
Their lengths have greatest common divisor one, establishing aperiodicity for the class containing that state.
The reported log probabilities are finite conditional probabilities of selected event sequences, not estimates of the state's stationary mass.

## Validation

```bash
python replications/izquierdo_2009/witness.py /downloaded/figure2.png /new/run
python replications/izquierdo_2009/verify_witness.py /new/run /new/verification
```

The input is pinned by SHA-256 and available at
[the journal's Figure 2](https://www.jasss.org/12/1/6/appendixB/EpsteinAxtell1996-2.png).
The runner needs NumPy and Pillow; the independent verifier uses only Python's standard library.

[Retained evidence](https://github.com/Metta-AI/sugarscape/blob/a18abe32088f518ba30e5120ff473f7bbd4eefb3/replications/izquierdo_2009/results/full-model-return-2026-10-17/report.json) contains all 18 full states across the two return paths and initial reachability path.
Independent arithmetic and topology checks cover 4,500 agent observations and 45,000 cell observations.
The checker recomputes full-state hashes and verifies every wealth, lifetime, birth count, position, and landscape value.
A complete workflow with newborn wealth increased by one fails its return assertion and creates no completion report.
Ruff formatting and lint checks pass.

## General regeneration and proof

The proof bounds every reachable agent by `wealth + 3 × remaining_life ≤ 325`, making the full state space finite.
From any reachable state, controlled desert replacements eliminate the original population within 100 steps.
Four further growbacks restore the landscape; permitted five- and six-step lifespans synchronize mortality in another 30 steps.
One final replacement can create any prescribed legal initial state, completing a 135-step positive-probability path.
The five- and six-step returns then establish aperiodicity throughout the communicating state space.

```bash
python replications/izquierdo_2009/regenerate.py /new/run/capacity.csv /new/regeneration
python replications/izquierdo_2009/verify_regeneration.py /new/regeneration /new/regeneration-verification
```

[Regeneration evidence](https://github.com/Metta-AI/sugarscape/blob/a18abe32088f518ba30e5120ff473f7bbd4eefb3/replications/izquierdo_2009/results/regeneration-2026-10-17/report.json) starts from three reachable states, after zero, 37, and 100 warmup steps.
An independent geometric replay checks 545 full states, 135,500 movement decisions, and 13,910 replacements.
All three paths reach the same prescribed legal initial state after 135 controlled steps.
These examples validate the implementation; the general proof establishes reachability for every state.

The evidence includes executed source snapshots and complete compressed choice tapes.
A copied tape with an occupied destination and a recomputed checksum is rejected by the semantic movement check.
Original evidence remains untouched.
The age convention is explicit: newborn age zero, one lifetime unit consumed per movement, death at exhausted life.
The paper does not supply age-update pseudocode; this realizes its stated maximum lifetime and remaining-life state variable.
No empirical stationary distribution, convergence rate, or pseudorandom-generator ergodicity is claimed.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/91441ad4115b0c351a654127acc29cc16ab3ea0c/replications/izquierdo_2009/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show 91441ad4115b0c351a654127acc29cc16ab3ea0c:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/e0e3613f4712e14b0804d75fd2c345c4ab7dab9e/replications/izquierdo_2009).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=e0e3613f4712e14b0804d75fd2c345c4ab7dab9e --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/a18abe32088f518ba30e5120ff473f7bbd4eefb3/replications/izquierdo_2009) retains raw outputs removed in previous cleanups.
