from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root = Path(__file__).resolve().parent
with (root / 'timings.csv').open() as stream:
    rows = list(csv.DictReader(stream))
x = [int(r['requested_cells']) for r in rows]
fig, (top, bottom) = plt.subplots(2, 1, figsize=(8, 7), sharex=True, layout='constrained')
for key, label, marker in [('published_seconds', 'Published figure: Titan Xp system', 'o'), ('native_wall_seconds', 'Native H100 system: whole runner', 's'), ('engine_reported_seconds', 'Native engine span (also includes XML)', '^')]:
    top.loglog(x, [float(r[key]) for r in rows], marker=marker, label=label)
top.set(ylabel='Seconds', title='Native OpenABL run: 100 steps with per-step XML output')
top.legend(fontsize=9)
top.grid(alpha=.25)
bottom.semilogx(x, [float(r['native_over_published']) for r in rows], marker='s', color='#d2691e')
bottom.axhline(1, color='black', linewidth=.7, linestyle='--')
bottom.set(xlabel='Requested cells (rounded down to a square grid)', ylabel='Native wall / published', ylim=(0, 1.15))
bottom.grid(alpha=.25)
fig.suptitle('Different hardware; one native observation per size; descriptive comparison', fontsize=11)
fig.savefig(root / 'comparison.png', dpi=150)
fig.savefig(root / 'comparison.pdf')
