# Initial-landscape interpretation audit

The [paper, Section 4.3](https://onlinelibrary.wiley.com/doi/10.1002/spe.3207), specifies a torus and gives contradictory capacity values of four and seven.
Its Equation 10 sums radius-five bands from all peaks. It claims minimum peak separation of 20 prevents exceeding the maximum of four.
The released source uses wrapped peak-separation distances, direct cell-to-peak distances, and a final capacity clamp of four.

This posthoc diagnostic reuses two retained seed-zero macOS host initializations, each with 54 peaks and 65,536 cells.
They differ by compiler/library and are not independent experimental seeds. Neither is the Linux GPU world.
Both complete released landscapes are reproduced exactly before changing geometry or capacity interpretation.
The toolchain mismatch and failed historical-image comparisons remain preserved in the earlier evidence.

| Quantity | macOS GCC world | macOS Clang world |
| --- | ---: | ---: |
| Released total initial sugar | 115,845 | 117,705 |
| Direct-distance cells exceeding four before clipping | 1,638 | 1,128 |
| Maximum direct-distance summed sugar | 6 | 5 |
| Cells changed by wrapped distances, retaining cap four | 4,500 | 3,913 |
| Added sugar from wrapped distances, retaining cap four | 7,382 | 5,923 |
| Cells changed by direct-distance cap seven | 1,638 | 1,128 |
| Added sugar from direct-distance cap seven | 1,678 | 1,128 |
| Wrapped summed sugar before clipping | 125,064 | 125,064 |

Both peak sets satisfy minimum wrapped separation of 20. Their overlapping bands nevertheless exceed four.
Thus the spacing condition alone does not imply the claimed bound; explicit clipping has an observable effect.
Equal wrapped totals arise from translating the same peak kernel on a torus before clipping, not from equal landscapes.

## Verification and limits

Python verifies retained input hashes and reconstructs all cell capacities using the released float-distance band arithmetic.
Independent R uses integer squared-distance thresholds of 25, 100, 225 and 400, checks peak spacing, and reproduces all 786,432 surface values exactly.
It also checks all aggregate values against the original complete host worlds.
Each world retains six surfaces: direct and wrapped sums, each unclipped, capped at four, and capped at seven.

Run `python analyze.py`, then `Rscript verify.R <this-directory>`.
The scripts consume adjacent retained initialization evidence; use NumPy 1.26.4 and R 4.6.1 with jsonlite.

No source model was changed and no GPU simulation was run. No behavioral or performance effect is inferred from initialization alone.
The paper does not select a unique capacity interpretation. Neither alternative is labelled the recovered historical method.
Future native controls must retain an unchanged baseline and separately label geometry and capacity changes.
They must also address metabolism maximum and update order rather than treating landscape changes as full method fidelity.
No completed-study credit follows from this diagnostic.
