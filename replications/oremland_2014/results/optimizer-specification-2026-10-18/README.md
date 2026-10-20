# Optimizer specification concordance

The journal's [Algorithm 1](https://www.jasss.org/17/2/6/algorithm1.png) and the dissertation's Algorithm 1 (PDF page 23, printed page 9) describe the same procedure.
The retrieved journal image was visually inspected, and the dissertation algorithm was read in the retained PDF.

The stated procedure initializes random policies, evaluates each generation, and carries the current nondominated frontier into the next generation.
Parent tournaments use two candidates and a random comparison subset of five policies.
Dominance decides the winner when only one candidate meets that criterion; otherwise a neighborhood criterion and then random choice break ties.
Uniform crossover produces two complementary children, choosing the source parent independently for each policy component.
Per-component mutation probability is `0.20 * (max_gens - generation) / max_gens`.

These rules support an implementation, but do not uniquely identify the authors' optimizer.
The following choices remain unstated in the inspected journal text/image and corresponding dissertation chapter:

- Numeric generation size and generation limit.
- Initial-policy distribution and optimizer random streams.
- Whether a candidate must dominate the comparison set or merely be nondominated by it.
- Neighborhood distance, radius, normalization, and which policies are counted.
- Sampling replacement and whether comparison sets include the tournament candidates.
- Whether mutation selects from all four rates or requires a different rate.
- Generation numbering and the resulting first/last mutation probabilities.
- Reevaluation versus reuse of noisy objective estimates for retained policies.
- Handling an odd number of remaining population slots when crossover produces two children.

The figure does not state a numeric neighborhood rule or numeric optimization budget.
We have not filled these gaps by fitting settings to the published frontier.
The cited Horn et al. method is a source lead, but a related algorithm's defaults do not establish the authors' modified implementation.

## Dissertation attachments

The public Virginia Tech DSpace item is `c80dbbb9-5931-4aaf-8a10-7099ca356591`.
All returned bundle and bitstream pages were inspected; each collection has one page.
Its current public bundles contain:

| Bundle | File | Bytes |
| --- | --- | ---: |
| ORIGINAL | Oremland_MS_D_2014.pdf | 5,094,083 |
| TEXT | Oremland_MS_D_2014.pdf.txt | 299,140 |
| THUMBNAIL | Oremland_MS_D_2014.pdf.jpg | 3,700 |

No source archive is attached in this public inventory.
This does not establish absence from other repositories, historical versions, or private deposits.
Raw API responses, the inventory, and hashes are retained here.

The new batch evaluator supplies complete native outcomes for future optimizer experiments.
A reconstruction must declare the missing choices and evaluate sensitivity before interpreting a difference as a negative replication.
The original full-paper optimization and reduced-model transfer results remain incomplete.

Algorithm attribution: Matthew Oremland and Reinhard Laubenbacher, *Optimization of Agent-Based Models: Scaling Methods and Heuristic Algorithms*, JASSS 17(2), 6 (2014), Algorithm 1, DOI 10.18564/jasss.2472.
