# Published figure title and placement audit

All 112 panels across Figures 3–9 were screened against their outer row and column labels using Tesseract on the original extracted images.
After normalizing case and whitespace, 102 titles match the expected labels.
Direct enlarged-image review of the remaining ten resolves eight OCR errors and confirms the two already excluded Figure 6 conflicts.
Four SARSA/SARSA titles were also inspected directly after ambiguity in page-sized renderings; all four read S v S.
No further target exclusion is justified by this check.

The 112 inventory image rectangles match their actual PDF placements.
Each row and column follows the documented method order geometrically, including the previously corrected Figure 3 final row.
The two conflicting image hashes match `paper-target-exclusions.json` exactly.

`review.json` separates automated matches from manual transcriptions. Original images for all 14 manual reviews are retained here.
`read_titles.py` records the original OCR workflow and pinned paper/inventory checks. Its paths identify the retained source evidence.
All source PDF pages and extracted images remain in `/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-figure-title-audit-001`.

OCR and visual reading can have errors. This checks titles and placement, not historical curve data or a replication outcome.
No simulation coverage, primary score, or study completion credit changes.
