# Complete modern-runtime qualification

All five saved folds complete under the original 1,800-second bound: exit zero in 1,598.612 seconds. The full replay retains 10,000 normal/residual draws per test observation, all five parameters, and every training/test row.

All 6,250 predictions, 6,250 lower bounds, and 6,250 upper bounds match the original workflow exactly. Every fold-ending random state also matches. A fresh R process reopens all ten original/replay fold files and confirms dimensions, ordered parameter names, all 18,750 numeric values, and all five random states. The known rowname metadata difference does not change observation order or numeric values.

All 25 aggregate metrics—RMSE, training-mean baseline RMSE, normalized performance, coverage, and interval width for five parameters—also match the original CSV values exactly. The original Table 8 comparison remains unchanged. This qualifies the portable full-workflow orchestration in the modern runtime; it does not resolve the paper discrepancies or establish historical-runtime equivalence.

The frozen script, complete outputs, input hashes, process receipt, fresh-readback script/receipt, and aggregate verifier are retained. The subsequent pinned historical-runtime control is recorded separately.
