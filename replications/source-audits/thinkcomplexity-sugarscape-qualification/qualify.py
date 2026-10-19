"""Bounded modern-runtime qualification, not reconstruction of chapter experiments."""
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root/'Sugarscape'))
from Sugarscape import Sugarscape

pins = json.loads((root/'members.json').read_text())
for name, expected in pins.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected
started = time.monotonic()
counts = []
with (root/'qualification.csv').open('x') as stream:
    writer = csv.writer(stream)
    writer.writerow(['tax_rate','seed','step','population','total_wealth','mean_wealth'])
    for tax in [0,0.04,0.2]:
        random.seed(0)
        model = Sugarscape(tax_rate=tax)
        for step in range(101):
            assert time.monotonic()-started < 120
            wealths = [a.sugar_reserve for a in model.agents]
            assert wealths and all(math.isfinite(v) for v in wealths)
            assert model.timestamp == step
            writer.writerow([tax,0,step,len(wealths),sum(wealths),sum(wealths)/len(wealths)])
            if step<100:model.nextstep()
        counts.append(len(model.agents))
(root/'qualification.json').write_text(json.dumps({'python':platform.python_version(),'conditions':3,'steps_per_run':100,'observations':303,'final_populations':counts,'source_files_unchanged':True,'scope':'Unmodified core simulation through public constructor/nextstep on modern Python. Seed0 and100 steps chosen for bounded qualification, not historical figure settings. Does not exercise Python2 DataCollect division or graphical interface; no chapter reproduction verdict.'},indent=2)+'\n')
print((root/'qualification.json').read_text())
