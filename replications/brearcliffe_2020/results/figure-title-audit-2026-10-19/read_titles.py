from pathlib import Path
import hashlib
import json
import subprocess
import fitz

root = Path(__file__).resolve().parent
inventory_path = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020/figure-panel-inventory.json')
inventory = json.loads(inventory_path.read_text())
paper = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-source-001/paper.pdf')
assert hashlib.sha256(paper.read_bytes()).hexdigest() == inventory['paper_sha256']
images = root / 'panels'; images.mkdir()
labels = {'Rule M': 'M', 'EC': 'EC', 'Q-Learning': 'Q', 'SARSA': 'S'}
metrics = {3: 'Mean Wealth', 4: 'Mean Vision', 5: 'Mean Metabolism', 6: 'Mean Combat Death', 7: 'Mean Starvation Death', 8: 'Mean Age', 9: 'Mean Max Age'}
rows = []
with fitz.open(paper) as pdf:
    for figure in inventory['figures']:
        for index, panel in enumerate(figure['panels']):
            raw = pdf.extract_image(panel['xref'])['image']
            assert hashlib.sha256(raw).hexdigest() == panel['sha256']
            path = images / f"figure-{figure['figure']}-panel-{index:02d}.png"
            path.write_bytes(raw)
            result = subprocess.run(['/opt/homebrew/bin/tesseract', str(path), 'stdout', '--psm', '11'], capture_output=True, text=True, timeout=15, check=True)
            path.with_suffix('.txt').write_text(result.stdout)
            lines = [s.strip() for s in result.stdout.splitlines() if s.strip()]
            expected = f"{labels[panel['group_A']]} v {labels[panel['group_B']]}: {metrics[figure['figure']]}"
            row = {'figure': figure['figure'], 'panel_index': index, 'group_A': panel['group_A'], 'group_B': panel['group_B'], 'image_sha256': panel['sha256'], 'expected_title_from_outer_labels': expected, 'ocr_first_line': lines[0], 'exact_ocr_match': lines[0] == expected}
            rows.append(row)
            if not row['exact_ocr_match']: print(json.dumps(row), flush=True)
report = {'paper_sha256': inventory['paper_sha256'], 'inventory_sha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(), 'tesseract_version': subprocess.check_output(['/opt/homebrew/bin/tesseract', '--version'], text=True).splitlines()[0], 'panels': rows, 'scope': 'OCR is a screening aid. Nonmatching titles require direct visual examination; title agreement does not validate curve data.'}
(root / 'ocr-screen.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'panels': len(rows), 'exact_ocr_matches': sum(r['exact_ocr_match'] for r in rows)}), flush=True)
