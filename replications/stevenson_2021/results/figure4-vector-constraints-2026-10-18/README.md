# Original evolutionary-figure constraints

The source figure from arXiv:2108.11892v2 contains 22 curves and 4,015 exported vertices.
The extractor calibrates the original population, Gini, wealth, and time axes; it does not fit our simulations.
All vertices and omitted-collinear-point limitations are retained.

The initial ten infertility counts round to 81, 79, 70, 96, 87, 67, 97, 88, 90, 75: total 830.
The initial ten birth-cost counts round to 91, 82, 79, 102, 83, 88, 84, 80, 70, 71: total 830.
Each approximate count is within 0.05 agents of its nearest integer. Independent Decimal arithmetic reproduces both lists and totals.
The first curve in each family is explicitly labelled infertility 10 or birth cost 0.
The remaining gray curves are individually unlabelled; their list order is not asserted to map to specific alternative trait values.

The plotted observations start at zero and end approximately at generation 499.
Every exported time ordinate is within 0.05 of an integer under the labelled tick calibration.
This is vector digitization, not recovered simulation data. The axis says generations; a mapping to action cycles is not established.
Initial Gini and wealth are plotted at zero, but these aggregates cannot identify agents' ages or joint trait assignments.

These observations constrain the Figure 4 reconstruction: its initial population differs from the fixed-society one-agent growth experiment.
They do not specify inheritance, mutation, trait reassignment, initial placement, or the original random seed.
No simulator behavior or acceptance criterion is changed, and no replication completion is claimed.

An initial extraction attempt used a 0.02-generation coordinate gate and stopped because the terminal tick calibration differs by approximately 0.022 generations.
The retained implementation checks every exported time against the stated 0.05-generation rounding tolerance and preserves the original coordinates.
The failed extraction remains in the local evidence directory; no scientific output was altered.
