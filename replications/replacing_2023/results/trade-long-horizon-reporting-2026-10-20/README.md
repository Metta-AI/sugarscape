# Horizon-dependent reporting prevents raw-prefix equality

The unchanged baseline completes 10,000 steps and exits zero, retaining 10,001 observations.
The declared exact raw-prefix gate then fails. Trade and lending do not start.
The original failed runner, protocol, raw trajectory, and all mismatch records remain retained.

Only four prefix records differ, at steps 125, 250, 375, and 500.
The author collects three per-agent arrays at quarters of the configured horizon.
Their sampling steps therefore change from 125/250/375/500 to 2500/5000/7500/10000.
The original final record also includes `endLog`'s extra metabolism accumulation.
Its 1,620-unit difference equals the final agents' recorded total metabolism exactly.
Every other field in all 501 prefix records matches.

This identifies a reporting dependency; it does not validate full-state equivalence or justify silently dropping fields.
The next qualification will reconstruct the original array samples from passive observations and account explicitly for closing-log arithmetic.
It must preserve the native extended trajectory and original records.
No extended-horizon effect estimate or whole-study completion credit is assigned here.
