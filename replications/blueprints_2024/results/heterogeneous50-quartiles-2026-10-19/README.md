# Heterogeneous50 population quartiles

Figure 16 describes quartiles of the per-run mean populations across 500 seeds.
The pinned PDF page 17 has upper and lower dotted black paths, visually checked against the median curve and axes.
At exactly 50% utilitarian agents, the lower-quartile path has no visible ink: the coordinate falls inside a dash gap.
That target remains unresolved. No interpolation through the gap is used.

The upper-quartile path has four outline intersections at this coordinate.
Their envelope spans population 1142.645459–1147.207888. This is graphical precision, not a confidence interval.
All nine standard quantile definitions fall inside that envelope under all four previously declared averaging conventions.
For linear interpolation (type 7), the upper quartile is 1144.922915 including the initial state and 1145.1019 excluding it.
Zero extension after extinction does not change these upper quartiles.

Lower quartiles are sensitive to extinction treatment: type 7 gives 47.422898/46.225708 for observed rows and 1.863227/1.8136 with zero extension.
The first value includes the initial state; the second excludes it. These values receive no paper-agreement score because the target is missing at this coordinate.

Independent R computes all 72 quantiles (nine definitions, four averaging conventions, two quartiles), agreeing within 2.28e-13 absolute error.
Repeating PDF extraction and calculation produces byte-identical JSON. The exact rational type-7 values and every alternative are retained.
These sensitivity checks are not independent experiments. Historical conventions and additional frame calibration uncertainty remain unresolved.
This adds upper-quartile graphical agreement for one complete condition, not whole-paper replication or new simulation coverage.
