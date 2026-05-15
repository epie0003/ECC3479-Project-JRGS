import json, copy
from pathlib import Path

ROOT = Path('c:/Users/neddp/ECC3479-Project-JRGS/docs/Report')

NOTEBOOKS = [
    'Introduction.ipynb',
    'Literature Review.ipynb',
    'Data and Methodology.ipynb',
    'Results.ipynb',
    'Discussion.ipynb',
    'Conclusion.ipynb',
]

all_cells = []

for nb_name in NOTEBOOKS:
    with open(ROOT / nb_name, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    for cell in nb['cells']:
        c = copy.deepcopy(cell)

        # Clear stale outputs so the draft runs clean
        if c['cell_type'] == 'code':
            c['outputs'] = []
            c['execution_count'] = None

        # Results-specific fixes
        if nb_name == 'Results.ipynb':
            cell_id = c.get('id', '')

            # Shorten the Results section title for consistency
            if cell_id == 'res_title':
                c['source'] = ['# Results\n']

            # Rename "## Discussion" inside Results to "## Summary"
            # so it does not collide with the standalone Discussion section
            if cell_id == 'res_takeaway':
                c['source'] = [
                    ln.replace('## Discussion', '## Summary')
                    for ln in c['source']
                ]

        all_cells.append(c)

combined = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python (ECC3479)",
            "language": "python",
            "name": "ecc3479-venv"
        },
        "language_info": {
            "name": "python",
            "version": "3.14.0"
        }
    },
    "cells": all_cells,
}

out = ROOT / 'Draft 1.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=1, ensure_ascii=False)

print(f"Written: {out}")
print(f"Total cells: {len(all_cells)}")
print()
for i, c in enumerate(all_cells):
    print(f"  [{i:2d}] {c['cell_type']:8s}  {c.get('id','')}")
