# Izquierdo et al. (2009): Sugarscape as a Markov chain

Study source: [Techniques to Understand Computer Simulations: Markov Chain Analysis](https://www.jasss.org/12/1/6.html),
specifically its [Sugarscape appendix](https://www.jasss.org/12/1/6/appendixB/EpsteinAxtell1996.html).
The other nine model case studies are outside this Sugarscape replication.

**Status: partial.** Executable return paths establish aperiodicity of one reachable communicating class.
They do not establish global irreducibility or complete this study.
The outstanding target is the appendix's full argument for a unique, initial-state-independent limiting distribution.
Finite simulation agreement cannot substitute for that argument.

## Model and evidence

`witness.py` implements the appendix's 50×50 torus with 250 agents and separate growback, movement, and replacement phases.
Agents see cardinal cells, choose maximum sugar and then minimum distance, harvest, metabolize, and lose one unit of remaining life.
Starvation or exhausted life removes an agent; replacements occur after the movement phase at age zero.
Replacement attributes retain the published ranges: vision 1–6, metabolism 1–4, wealth 5–25, and maximum age 60–100.
The state contains landscape sugar and agent position, vision, metabolism, wealth, and remaining life, excluding identifiers and elapsed time.

The paths deliberately select permissible random choices with positive probability.
They are not unbiased simulation samples and do not estimate stationary probabilities or convergence times.
Activation permutations are recorded through the seed and probability calculation; movement ties choose an eligible minimum-index cell.
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

[Retained evidence](results/return-witness-2026-10-17/report.json) contains all 18 full states across the two return paths and initial reachability path.
Independent arithmetic and topology checks cover 4,500 agent observations and 45,000 cell observations.
The checker recomputes full-state hashes and verifies every wealth, lifetime, birth count, position, and landscape value.
A complete workflow with newborn wealth increased by one fails its return assertion and creates no completion report.
Ruff formatting and lint checks pass.

## Remaining work

- Establish a finite state-space bound under the exact scheduling convention.
- Construct and independently verify regeneration paths from general states, including legal replacement choices and synchronized mortality.
- Supply the general reachability proof; selected executable paths alone do not prove irreducibility.
- Check the resulting limiting-distribution claim without asserting a practical mixing-time bound.
