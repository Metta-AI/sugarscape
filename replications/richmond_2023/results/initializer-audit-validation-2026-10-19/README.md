# Initializer audit validation

`audit_initializer.py` checks every observed initial cell, agent attributes, peak coordinates, and the declared landscape geometry/capacity.
Integer squared-distance bands independently reconstruct all capacities. Peak separation violations are reported, preserving the source's bounded placement fallback.
The auditor checks two complete retained host worlds: 131,072 cells. Both capacities and previously recorded aggregate values agree exactly.
An intentionally incorrect wrapped-geometry label for the unchanged GCC world fails; no successful report is written.
The initial CSV parser failed because integer Literal fields received strings. Explicit integer parsing fixes the cause; the failure record remains retained.

`audit_state_transitions.py --initial-audit REPORT` checks the complete initial-state SHA-256 against the typed initializer report.
The default historical path retains its original pinned hash; released-state replay retains its full trajectory pin.
Reauditing the original native release preserves every report field across all 881,753 post-step observations.
The new initializer-audit path has not yet audited a new GPU control; those native controls remain unexecuted.

The initializer report validates state structure and arithmetic, not random-draw fidelity or model-source provenance.
The native collector/launcher must verify source hashes and actual parameters separately before accepting a new initial world.
Peak and full-cell capture are now included in prepared controls; two preparations and all nine patch round trips pass again.
Prior preparations without peak capture remain in retained evidence as `richmond-initializer-controls-prepared-001/002`.
Current preparations are `richmond-initializer-controls-prepared-003/004`.

No new simulations, allocation, or completed-study credit follow from these validations.
