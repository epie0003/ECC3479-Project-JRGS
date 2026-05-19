"""
Assembles Draft 2.ipynb from selected cells across section notebooks.

Structure:
  Introduction
  Data           (fee table, summary stats, sample construction)
  Empirical Strategy (hypothesis, DiD equation, pre-trends)
  Results        (table 1, coefficient plot; excludes res_robustness and res_takeaway)
  Robustness     (Table 2, prose)
  Discussion, Limitations, and Conclusion
  References
"""

import json
import copy
from pathlib import Path

ROOT = Path('c:/Users/neddp/ECC3479-Project-JRGS/docs/Report')


def load_nb(name):
    with open(ROOT / name, encoding='utf-8') as f:
        return json.load(f)


def cell_by_id(nb, cell_id):
    for c in nb['cells']:
        if c.get('id') == cell_id:
            return copy.deepcopy(c)
    raise KeyError(f"Cell '{cell_id}' not found")


def cells_by_id(nb, *ids):
    cell_map = {c.get('id'): c for c in nb['cells']}
    result = []
    for cid in ids:
        if cid not in cell_map:
            raise KeyError(f"Cell '{cid}' not found")
        result.append(copy.deepcopy(cell_map[cid]))
    return result


def src(c):
    return ''.join(c['source'])


def set_src(c, text):
    c['source'] = [text]


# ── Load notebooks ────────────────────────────────────────────
intro_nb = load_nb('Introduction.ipynb')
dm_nb    = load_nb('Data and Methodology.ipynb')
res_nb   = load_nb('Results.ipynb')
rob_nb   = load_nb('Robustness.ipynb')
dc_nb    = load_nb('Discussion_Conclusion.ipynb')
ref_nb   = load_nb('References.ipynb')

all_cells = []

# ── Title Page ────────────────────────────────────────────────
all_cells.append({
    'cell_type': 'markdown',
    'id': 'd2_title_page',
    'metadata': {},
    'source': [
        '<div class="title-page" style="text-align:center;padding:120px 0 80px 0;">\n\n'
        '<p style="font-size:1.5em;font-weight:bold;line-height:1.4;margin-bottom:0.3em;">'
        'Price Signals and Enrolment Decisions:<br>'
        'Evidence from Australia\'s Job-Ready Graduates Scheme'
        '</p>\n\n'
        '<br><br><br>\n\n'
        '<p>Edward Pierre-Humbert</p>\n\n'
        '<p>31496903</p>\n\n'
        '<p>ECC3479 Data and Evidence in Economics</p>\n\n'
        '</div>'
    ],
})

# ── Introduction ──────────────────────────────────────────────
all_cells += cells_by_id(intro_nb, 'intro_body')

# ── Data ──────────────────────────────────────────────────────
# Rename "# Data and Methodology" → "# Data"
dm_intro = cell_by_id(dm_nb, 'dm_intro')
dm_intro_text = src(dm_intro)
dm_intro_text = dm_intro_text.replace('# Data and Methodology\n', '# Data\n', 1)
# Remove the "## Data" subheading that duplicates the renamed section heading
dm_intro_text = dm_intro_text.replace('\n\n## Data\n\n', '\n\n', 1)
set_src(dm_intro, dm_intro_text)
all_cells.append(dm_intro)

all_cells += cells_by_id(dm_nb,
    'dm_fee_header',
    'dm_fee_code',
    'dm_fee_prose',
    'dm_sumstats_header',
    'dm_sumstats_code',
    'dm_excl_header',
    'dm_excl_code',
)

# ── Empirical Strategy ────────────────────────────────────────
all_cells.append({
    'cell_type': 'markdown',
    'id': 'd2_emp_strategy',
    'metadata': {},
    'source': ['# Empirical Strategy'],
})

# dm_hypothesis: strip the "## Data Relation to Hypothesis" heading, keep body
dm_hyp = cell_by_id(dm_nb, 'dm_hypothesis')
hyp_text = src(dm_hyp)
# Body starts after the first blank line following the heading
hyp_body = hyp_text.split('\n\n', 1)[1] if '\n\n' in hyp_text else hyp_text
set_src(dm_hyp, hyp_body)
all_cells.append(dm_hyp)

all_cells += cells_by_id(dm_nb, 'dm_methodology')

# Pre-trends figure: add "Figure 1." prefix to the suptitle
dm_pre_code = cell_by_id(dm_nb, 'dm_pretrend_code')
set_src(dm_pre_code, src(dm_pre_code).replace(
    "'Pre-treatment log-enrolment trends",
    "'Figure 1. Pre-treatment log-enrolment trends",
    1,
))
all_cells.append(dm_pre_code)

all_cells += cells_by_id(dm_nb, 'dm_pretrend_prose')

# ── Results ───────────────────────────────────────────────────
res_title = cell_by_id(res_nb, 'res_title')
set_src(res_title, '# Results\n')
all_cells.append(res_title)

all_cells += cells_by_id(res_nb, 'res_setup', 'res_run')

# res_s1_header: remove "---\n" section divider
res_s1 = cell_by_id(res_nb, 'res_s1_header')
set_src(res_s1, src(res_s1).replace('---\n', '', 1))
all_cells.append(res_s1)

all_cells += cells_by_id(res_nb, 'res_table1', 'res_prose')

# res_s2_header: remove divider, replace with self-contained Figure 2 caption
res_s2 = cell_by_id(res_nb, 'res_s2_header')
set_src(res_s2, (
    '## Coefficient Plot\n\n'
    'Figure 2 plots DiD coefficient estimates (β̂₃) and 95% confidence intervals '
    'for all eleven disciplines, sorted by effect size. '
    'Priority disciplines receiving fee reductions under the JRGS are shown in blue, '
    'discouraged disciplines facing fee increases in red, and non-priority disciplines in grey. '
    'The horizontal axis measures log-point deviations of Australian enrolments from the '
    'pooled UK-NZ counterfactual trend post-2021; the dashed line at zero indicates no change relative to trend.\n'
))
all_cells.append(res_s2)

# Coefficient plot: update title from "Figure 1." to "Figure 2."
res_plot = cell_by_id(res_nb, 'res_plot')
set_src(res_plot, src(res_plot).replace(
    'Figure 1. JRG Effect on Enrolments by Discipline',
    'Figure 2. JRG Effect on Enrolments by Discipline',
    1,
))
all_cells.append(res_plot)

all_cells += cells_by_id(res_nb, 'res_plot_prose')

# Excluded from Draft 2: res_takeaway, res_robustness

# ── Robustness ────────────────────────────────────────────────
for c in rob_nb['cells']:
    all_cells.append(copy.deepcopy(c))

# ── Discussion, Limitations, and Conclusion ───────────────────
for c in dc_nb['cells']:
    all_cells.append(copy.deepcopy(c))

# ── References ────────────────────────────────────────────────
# Force page break before references so they sit on a separate page
for i, c in enumerate(ref_nb['cells']):
    c = copy.deepcopy(c)
    if i == 0 and c['cell_type'] == 'markdown':
        c['source'] = ['<div style="page-break-before: always;"></div>\n\n'] + c['source']
    all_cells.append(c)

# ── Clear code cell outputs ───────────────────────────────────
for c in all_cells:
    if c['cell_type'] == 'code':
        c['outputs'] = []
        c['execution_count'] = None

# ── Assemble and write ────────────────────────────────────────
combined = {
    'nbformat': 4,
    'nbformat_minor': 5,
    'metadata': {
        'kernelspec': {
            'display_name': 'Python (ECC3479)',
            'language': 'python',
            'name': 'ecc3479-venv',
        },
        'language_info': {
            'name': 'python',
            'version': '3.14.0',
        },
    },
    'cells': all_cells,
}

out = ROOT / 'Draft 2.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=1, ensure_ascii=False)

print(f'Written: {out}')
print(f'Total cells: {len(all_cells)}')
print()
for i, c in enumerate(all_cells):
    print(f'  [{i:2d}] {c["cell_type"]:8s}  {c.get("id", "")}')
