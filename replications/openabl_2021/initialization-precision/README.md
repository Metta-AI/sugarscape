# Generated constant precision

The128,000-cell initialization audit found22 differences in environmental sugar and capacity. The model formula gives variance3186.2250000000004, but the released C++ printer emits six significant digits:3186.23. The independent initializer previously used the unformatted expression.

`initialize.py` now reproduces that compiler formatting before evaluating the Gaussian resource map. All1,019,592 fields match at this size. Rechecking all ten retained sizes,250 through128,000 requested cells, also passes. The original discrepancy and failed assertion remain preserved. This is a validator correction, not evidence against the paper.

The native compiler, model, and RNG are unchanged. Source reference: `Printer.hpp` double insertion uses the default string stream, and `examples/sugarscape.abl` line50 defines the folded variance. The two largest MASON paired conditions resume in a new directory; the first nine remain valid.
