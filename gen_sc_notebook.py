"""
Generator script for REG Society & Culture.ipynb
CategoryKey = 9 | colour = mediumpurple | Panel: 2019-2024 (N=12, df=4)
"""
import json, os

OUT = r"docs\Regression Analysis\REG Society & Culture.ipynb"

def cell(cell_type, source, **kwargs):
    c = {"cell_type": cell_type, "metadata": {}, "source": source}
    if cell_type == "code":
        c["execution_count"] = None
        c["outputs"] = []
    return c

md = lambda s: cell("markdown", s)
code = lambda s: cell("code", s)

cells = []

# ── Cell 0 : Research context ─────────────────────────────────────────────────
cells.append(md(r"""# REG Society & Culture

## Research context

Society & Culture (CategoryKey = 9) is the **largest field** in the Australian dataset by
enrolment volume, encompassing Psychology, Social sciences, Law, Language and area studies,
Historical/philosophical/religious studies, and Media/journalism/communications.

Under JRG it is a **strongly discouraged field**: student contribution rose sharply from
~\$7,298 (2019–20) to ~\$11,636 (2021), a +59.4% increase. Commonwealth contribution fell
from ~\$8,531 to ~\$5,420 (−36.5%). This is the largest student fee increase of any
discipline analysed and signals a clear government intent to redirect enrolments away from
Society & Culture.

| Period | Student contribution (avg) | Commonwealth contribution (avg) |
|--------|---------------------------|----------------------------------|
| 2019–20 avg | \$7,364                 | \$8,607                       |
| 2021–24 avg | \$12,157                | \$5,682                       |
| **Change**  | **+65.1%**              | **−34.0%**                    |

**UK data availability:** Pre-2019 HESA data at CategoryKey = 9 contains only
"04 Veterinary science" (~6–8K enrolments), a clear taxonomic misassignment. Even reconstructing
the correct JACS subjects from key = 11 (Social studies, Law, Languages, Historical/philosophical,
Media) produces a sum of ~554–565K (2016–2018), while post-2019 CAH totals are ~731–788K —
an irreconcilable ~167K gap driven by Psychology (119K post-2019) having no JACS equivalent.
**The panel is therefore restricted to 2019–2024 (N = 12, df = 4)**, consistent with the
approach taken for N&PS and Others.

**UK composition post-2019** (6 CAH subjects summed each year):
Psychology | Social sciences | Law | Language & area studies |
Historical/philosophical/religious studies | Media, journalism & communications
"""))

# ── Cell 1 : Imports ───────────────────────────────────────────────────────────
cells.append(code(r"""import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS
from IPython.display import display

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 140)

START = Path.cwd()
ROOT = START
while ROOT != ROOT.parent and not (ROOT / 'data').exists():
    ROOT = ROOT.parent

AUS_PATH  = ROOT / 'data' / 'clean' / 'EnrollmentsAUS_category_with_numeric_key.csv'
UK_PATH   = ROOT / 'data' / 'clean' / 'uk_grouped' / 'with_categorykey' / 'UK_enrollments_grouped_comparison_all_years_with_categorykey.csv'
FUND_PATH = ROOT / 'data' / 'clean' / 'AnnualFundingAUS2019-2026_with_category_key.csv'

assert AUS_PATH.exists(),  f'Missing: {AUS_PATH}'
assert UK_PATH.exists(),   f'Missing: {UK_PATH}'
assert FUND_PATH.exists(), f'Missing: {FUND_PATH}'
print('Project root:', ROOT)
print('All data files found.')
"""))

# ── Cell 2 : AUS descriptive header ──────────────────────────────────────────
cells.append(md(r"""## 1. AUS Descriptive Analysis

Examine Australia-only S&C data (2016–2024) to characterise the enrolment trend and test a
simple pre/post break. AUS S&C is the largest single category, growing steadily from 312,569
(2016) to a post-JRG peak of 350,654 (2021) before declining to 329,590 (2024).
"""))

# ── Cell 3 : AUS data load + plot ─────────────────────────────────────────────
cells.append(code(r"""aus_raw   = pd.read_csv(AUS_PATH)
year_cols = [c for c in aus_raw.columns if str(c).isdigit()]

aus_long = aus_raw.melt(
    id_vars=['Category', 'CategoryKey'],
    value_vars=year_cols,
    var_name='year',
    value_name='enrollments',
)
aus_long['year']        = aus_long['year'].astype(int)
aus_long['enrollments'] = pd.to_numeric(aus_long['enrollments'], errors='coerce')

arch_aus = aus_long[aus_long['CategoryKey'] == 9].copy().sort_values('year').reset_index(drop=True)
arch_aus['log_enrollments'] = np.log(arch_aus['enrollments'])
arch_aus['year_c']   = arch_aus['year'] - 2019
arch_aus['year_c2']  = arch_aus['year_c'] ** 2
arch_aus['post_jrg'] = (arch_aus['year'] >= 2021).astype(int)

print('AUS Society & Culture -- enrolment data:')
display(arch_aus[['year', 'enrollments', 'log_enrollments']].reset_index(drop=True))

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

axes[0].bar(arch_aus['year'], arch_aus['enrollments'], color='mediumpurple', alpha=0.85)
axes[0].axvline(2020.5, linestyle='--', color='red', linewidth=1.5, label='JRG start (2021)')
axes[0].set_title('AUS Society & Culture: Enrolment levels')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('Enrolments'); axes[0].legend()

axes[1].plot(arch_aus['year'], arch_aus['log_enrollments'], 'o-', color='mediumpurple', linewidth=2)
axes[1].axvline(2020.5, linestyle='--', color='red', linewidth=1.5, label='JRG start (2021)')
axes[1].set_title('AUS Society & Culture: Log enrolments')
axes[1].set_xlabel('Year'); axes[1].set_ylabel('log(enrolments)'); axes[1].legend()

plt.tight_layout()
plt.show()
"""))

# ── Cell 4 : summary_table helper ────────────────────────────────────────────
cells.append(code(r"""def summary_table(result, vars_):
    ci = result.conf_int()
    rows = []
    for v in vars_:
        if v not in result.params.index:
            continue
        rows.append({
            'Variable': v,
            'beta':     round(result.params[v], 4),
            'SE (HC3)': round(result.bse[v], 4),
            'p':        round(result.pvalues[v], 4),
            'CI lo':    round(ci.loc[v, 0], 4),
            'CI hi':    round(ci.loc[v, 1], 4),
        })
    out = pd.DataFrame(rows).set_index('Variable')
    display(out)
    return out
"""))

# ── Cell 5 : Panel construction header ───────────────────────────────────────
cells.append(md(r"""## 2. DiD Panel Construction

Combine AUS and UK S&C data into a country × year panel (2019–2024).

**UK year mapping:** AcademicYear "2019/20" → integer 2019, etc. (start-year convention).

**UK data note:** Six CAH subject rows per year (Psychology, Social sciences, Law, Language
and area studies, Historical/philosophical/religious studies, Media/journalism/communications)
are summed to a single annual UK total using `groupby(year).sum()`.

**Pre-2019 UK data excluded:** Only "04 Veterinary science" (6–8K, wrong mapping) exists at
key = 9 pre-2019. Correct JACS reconstruction yields ~554–565K but misses Psychology (~119K),
producing an irreconcilable gap vs post-2019 CAH totals of ~731–788K.
"""))

# ── Cell 6 : Panel construction code ─────────────────────────────────────────
cells.append(code(r"""uk_raw  = pd.read_csv(UK_PATH)
arch_uk = uk_raw[uk_raw['categorykey'] == 9].copy()

arch_uk['year'] = arch_uk['AcademicYear'].str[:4].astype(int)
arch_uk['enrollments'] = pd.to_numeric(arch_uk['Total UK'], errors='coerce')
# Restrict to post-2019 CAH data (pre-2019 JACS mapping irreconcilable)
arch_uk = arch_uk[arch_uk['year'] >= 2019]
# Six subject rows per year -- sum to annual total
arch_uk = arch_uk.groupby('year', as_index=False)['enrollments'].sum()
arch_uk['country'] = 'UK'

arch_aus_did = arch_aus[arch_aus['year'] >= 2019][['year', 'enrollments']].copy()
arch_aus_did['country'] = 'AUS'

panel = pd.concat([arch_aus_did, arch_uk], ignore_index=True).sort_values(['country', 'year']).reset_index(drop=True)
panel['log_enrollments']   = np.log(panel['enrollments'])
panel['treated']           = (panel['country'] == 'AUS').astype(int)
panel['post']              = (panel['year'] >= 2021).astype(int)
panel['did']               = panel['treated'] * panel['post']
panel['covid_2020']        = (panel['year'] == 2020).astype(int)
panel['covid_2021']        = (panel['year'] == 2021).astype(int)
panel['treated_covid2020'] = panel['treated'] * panel['covid_2020']
panel['treated_covid2021'] = panel['treated'] * panel['covid_2021']
panel['year_c']            = panel['year'] - 2020

print('DiD panel -- Society & Culture (AUS vs UK, 2019-2024):')
display(panel[['country','year','enrollments','log_enrollments','treated','post','did']].reset_index(drop=True))
print(f'Shape: {panel.shape} | Pre-treatment: {sorted(panel[panel["post"]==0]["year"].unique())} | Post: {sorted(panel[panel["post"]==1]["year"].unique())}')
print(f'N = {len(panel)} | Countries = 2 | Years = {panel["year"].nunique()}')
"""))

# ── Cell 7 : Panel visualisation ─────────────────────────────────────────────
cells.append(code(r"""fig, axes = plt.subplots(1, 2, figsize=(13, 4))
colours = {'AUS': 'mediumpurple', 'UK': 'darkorange'}

for country, grp in panel.groupby('country'):
    grp = grp.sort_values('year')
    axes[0].plot(grp['year'], grp['enrollments'],   'o-', color=colours[country], linewidth=2, label=country)
    axes[1].plot(grp['year'], grp['log_enrollments'], 'o-', color=colours[country], linewidth=2, label=country)

for ax in axes:
    ax.axvline(2020.5, linestyle='--', color='red', linewidth=1.5, label='JRG start (2021)')
    ax.set_xlabel('Year'); ax.legend()

axes[0].set_title('Society & Culture: Enrolment levels (AUS vs UK)')
axes[0].set_ylabel('Enrolments')
axes[1].set_title('Society & Culture: Log enrolments (AUS vs UK)')
axes[1].set_ylabel('log(enrolments)')

plt.tight_layout()
plt.show()
"""))

# ── Cell 8 : TWFE header ─────────────────────────────────────────────────────
cells.append(md(r"""## 3. Main DiD Specification (TWFE)

**Estimating equation:**

$$\log(E_{ct}) = \beta_0 + \beta_1 \cdot \text{Treated}_c + \beta_2 \cdot \text{DID}_{ct} + \sum_{t} \gamma_t \cdot \mathbf{1}_{[\text{year}=t]} + \varepsilon_{ct}$$

where $\text{Treated}_c = 1$ for AUS, $\text{Post}_t = 1$ for $t \geq 2021$, and
$\text{DID}_{ct} = \text{Treated}_c \times \text{Post}_t$.

Standard errors are HC3 heteroscedasticity-robust. With N = 12 and df = 4, CIs are wide.
"""))

# ── Cell 9 : TWFE regression ─────────────────────────────────────────────────
cells.append(code(r"""formula_main = 'log_enrollments ~ treated + did + C(year)'
model_main = smf.ols(formula_main, data=panel).fit(cov_type='HC3')
print('=== Main DiD -- TWFE OLS (HC3) ===')
print(model_main.summary())

did_b  = model_main.params['did']
did_se = model_main.bse['did']
did_p  = model_main.pvalues['did']
did_ci = model_main.conf_int().loc['did']
pct    = (np.exp(did_b) - 1) * 100

print('\n--- Key result ---')
print(f'DiD estimate (beta_did): {did_b:.4f}')
print(f'SE (HC3):                {did_se:.4f}')
print(f'p-value:                 {did_p:.4f}')
print(f'95% CI:                  [{did_ci[0]:.4f}, {did_ci[1]:.4f}]')
print(f'Approx. % effect:        {pct:+.2f}%')
print(f'df_resid:                {int(model_main.df_resid)}')
direction = 'higher' if did_b > 0 else 'lower'
print(f'\nInterpretation: Post-JRG (2021+), AUS S&C enrolments were')
print(f'approximately {abs(pct):.1f}% {direction} than the UK trend would predict.')

formula_covid = 'log_enrollments ~ treated + did + treated_covid2020 + treated_covid2021 + C(year)'
m_covid = smf.ols(formula_covid, data=panel).fit(cov_type='HC3')
b_cv = m_covid.params.get('did', np.nan)
p_cv = m_covid.pvalues.get('did', np.nan)
print(f'\nCOVID-controlled spec (2-country design): beta_did = {b_cv:.4f}, p = {p_cv:.4f}')
print('(Degenerate SEs -- AUS-specific year interaction collinear with treated + year FEs in 2-country panel)')
"""))

# ── Cell 10 : PanelOLS cross-check ───────────────────────────────────────────
cells.append(code(r"""df_pl = panel.set_index(['country', 'year'])

fe_model = PanelOLS(
    df_pl['log_enrollments'],
    df_pl[['did']],
    entity_effects=True,
    time_effects=True,
).fit(cov_type='robust')

print('=== PanelOLS TWFE (cross-check) ===')
print(fe_model.summary)

print(f'\nOLS DiD estimate:      {did_b:.6f}')
print(f'PanelOLS DiD estimate: {fe_model.params["did"]:.6f}')
match = abs(did_b - fe_model.params['did']) < 1e-5
print('Estimates match' if match else 'WARNING: mismatch')
"""))

# ── Cell 11 : COVID sensitivity header ───────────────────────────────────────
cells.append(md(r"""## 4. COVID Sensitivity

Three variants using the simple TWFE formula across different sample restrictions.
With N = 12 and df = 4, note that dropping one year reduces df further and widens CIs.
Consistent sign across variants would support robustness; sign reversal would flag fragility.
"""))

# ── Cell 12 : COVID sensitivity code ─────────────────────────────────────────
cells.append(code(r"""formula_simple = 'log_enrollments ~ treated + did + C(year)'

variants = {
    'Full panel (2019-2024)': panel,
    'Drop 2020':              panel[panel['year'] != 2020].copy(),
    'Drop 2020 + 2021':       panel[~panel['year'].isin([2020, 2021])].copy(),
}

rows = []
for label, data in variants.items():
    m = smf.ols(formula_simple, data=data).fit(cov_type='HC3')
    b  = m.params.get('did', np.nan)
    se = m.bse.get('did', np.nan)
    p  = m.pvalues.get('did', np.nan)
    ci = m.conf_int().loc['did'] if 'did' in m.conf_int().index else [np.nan, np.nan]
    rows.append({
        'Specification': label,
        'N':             int(m.nobs),
        'df_resid':      int(m.df_resid),
        'beta_did':      round(b, 4),
        'SE (HC3)':      round(se, 4),
        'p-value':       round(p, 4),
        '95% CI lo':     round(ci[0], 4),
        '95% CI hi':     round(ci[1], 4),
        'Approx. %':     round((np.exp(b) - 1) * 100, 2) if pd.notna(b) else np.nan,
    })

print('=== COVID Sensitivity (simple TWFE, all variants) ===')
display(pd.DataFrame(rows).set_index('Specification'))
print('\nKey takeaway: check whether beta_did sign and magnitude are stable across sample restrictions.')
print('With only df = 4 in the full panel, CIs are wide and p-values should not be over-interpreted.')
"""))

# ── Cell 13 : Event study header ─────────────────────────────────────────────
cells.append(md(r"""## 5. Parallel Trends Check (Event Study)

Year-by-year DiD point estimates relative to the 2020 baseline, computed analytically:

$$\hat{\delta}_t = (\log Y_{\text{AUS},t} - \log Y_{\text{AUS},2020}) - (\log Y_{\text{UK},t} - \log Y_{\text{UK},2020})$$

This is numerically identical to a regression-based DiD coefficient but avoids the
degrees-of-freedom problem (2 obs per year, 2 params, df = 0) that arises with 2 countries.

> **Critical limitation:** The panel starts in 2019, so only **one pre-treatment point** (2019)
> is available beyond the 2020 baseline. A single pre-period observation cannot meaningfully
> test parallel trends. This is an identification weakness shared with N&PS and Others,
> resulting from the irreconcilable UK taxonomy break preventing use of pre-2019 data.
"""))

# ── Cell 14 : Event study code ───────────────────────────────────────────────
cells.append(code(r"""base_year = 2020
aus_log = panel[panel['country'] == 'AUS'].set_index('year')['log_enrollments']
uk_log  = panel[panel['country'] == 'UK' ].set_index('year')['log_enrollments']

event_rows = []
for yr in sorted(panel['year'].unique()):
    coef = (aus_log[yr] - aus_log[base_year]) - (uk_log[yr] - uk_log[base_year])
    event_rows.append({'year': yr, 'coef': round(coef, 6)})

ev = pd.DataFrame(event_rows)

fig, ax = plt.subplots(figsize=(11, 5))
ax.axhline(0, linestyle='--', color='gray', linewidth=0.8)
ax.axvline(2020.5, linestyle=':', color='red', linewidth=1.5, label='JRG start (2021)')
ax.fill_between([2018.5, 2020.5], -0.35, 0.35, color='gray', alpha=0.06, label='Pre-treatment period')
ax.plot(ev['year'], ev['coef'], 'o-', color='mediumpurple', linewidth=2,
        label='DiD point estimate (AUS vs UK, vs 2020)')
ax.scatter(ev['year'], ev['coef'], color='mediumpurple', s=50, zorder=5)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('DiD coefficient (log enrolments, baseline = 2020)', fontsize=12)
ax.set_title('Event Study: Society & Culture (AUS vs UK)', fontsize=13)
ax.set_xticks(sorted(panel['year'].unique()))
ax.legend(fontsize=10)
plt.tight_layout()
plt.show()

print('Event study point estimates (analytical DiD):')
ev['approx_%'] = (np.exp(ev['coef']) - 1) * 100
ev['period'] = ev['year'].apply(lambda y: 'Baseline' if y == 2020 else ('Pre' if y < 2021 else 'Post'))
display(ev.set_index('year').round(4))

print()
print('Note: With only 2 countries and 1 pre-treatment point (2019), parallel trends cannot')
print('be formally tested. The 2019 estimate provides minimal diagnostic information.')
"""))

# ── Cell 15 : Placebo header ─────────────────────────────────────────────────
cells.append(md(r"""## 6. Placebo Test

**AUS-only placebo (trend-break test):** restrict to the pre-treatment period (2016–2020) using
AUS data (available for all years) and test for a fake structural break at 2019. A significant
break would suggest pre-existing non-linear trends in the AUS S&C series.

> AUS S&C data is available back to 2016 (5 observations), allowing a pre-period test even
> though the DiD panel is restricted to 2019+. N = 5; treat as indicative only.
"""))

# ── Cell 16 : Placebo code ───────────────────────────────────────────────────
cells.append(code(r"""plac = arch_aus[arch_aus['year'] <= 2020].copy()
plac['fake_post']   = (plac['year'] >= 2019).astype(int)
plac['year_c_plac'] = plac['year'] - 2016

m_plac = smf.ols('log_enrollments ~ fake_post + year_c_plac', data=plac).fit(cov_type='HC3')

b_p = m_plac.params.get('fake_post', np.nan)
p_p = m_plac.pvalues.get('fake_post', np.nan)

print('=== AUS-Only Placebo: Fake Break at 2019 (2016-2020 data) ===')
print(m_plac.summary())

print(f'\nPlacebo coefficient (fake_post): {b_p:.4f} | p-value: {p_p:.4f}')
if pd.notna(p_p):
    if p_p > 0.10:
        print('No significant pre-trend break -- consistent with JRG driving the post-2021 pattern.')
    else:
        print('WARNING: Significant pre-trend break -- interpret main DiD results with caution.')
print('(N = 5; treat as indicative only)')
"""))

# ── Cell 17 : Level robustness header ────────────────────────────────────────
cells.append(md(r"""## 7. Level Outcome Robustness

Re-estimate the main DiD using enrolment **levels** (not logs) as a functional form robustness
check. The level DiD coefficient gives the absolute headcount difference attributable to JRG
relative to the UK trend.
"""))

# ── Cell 18 : Level robustness code ──────────────────────────────────────────
cells.append(code(r"""formula_level = 'enrollments ~ treated + did + treated_covid2020 + treated_covid2021 + C(year)'
m_level = smf.ols(formula_level, data=panel).fit(cov_type='HC3')

b_lev  = m_level.params.get('did', np.nan)
p_lev  = m_level.pvalues.get('did', np.nan)
ci_lev = m_level.conf_int().loc['did'] if 'did' in m_level.conf_int().index else [np.nan, np.nan]

print('=== Level Outcome Robustness ===')
if pd.notna(b_lev):
    print(f'beta_did (levels): {b_lev:,.0f} students | p = {p_lev:.4f}')
    if not (np.isinf(ci_lev[0]) or np.isnan(ci_lev[0])):
        print(f'95% CI:            [{ci_lev[0]:,.0f}, {ci_lev[1]:,.0f}]')
    else:
        print('95% CI: Degenerate SEs -- unreliable (COVID interaction terms collinear in 2-country panel)')
else:
    print('Degenerate SEs -- unreliable')

print('\n=== Specification comparison ===')
comp = pd.DataFrame({
    'Specification': ['Log-linear (preferred)', 'Level'],
    'beta_did':       [round(did_b, 4), round(b_lev, 0) if pd.notna(b_lev) else np.nan],
    'p-value':        [round(did_p, 4), round(p_lev, 4) if pd.notna(p_lev) else np.nan],
    'Interpretation': [
        f'approx. {(np.exp(did_b)-1)*100:.1f}% enrolment change',
        f'approx. {b_lev:,.0f} students per year' if pd.notna(b_lev) else 'Degenerate SEs',
    ],
}).set_index('Specification')
display(comp)
"""))

# ── Cell 19 : Funding context header ─────────────────────────────────────────
cells.append(md(r"""## 8. Funding Context

Society & Culture is the most strongly **discouraged** field under JRG in terms of the student
fee increase magnitude (+59.4%). The Commonwealth contribution fell −36.5%, shifting the
per-student cost burden substantially toward students. Unlike priority fields (where student
fees fell and/or Commonwealth funding rose), S&C received the clearest financial signal to
deter enrolment growth.

The total per-student package (student + Commonwealth) changed modestly in dollar terms, but
the composition shifted dramatically: the student share rose from ~46% (2019–20) to ~68% (2021).
"""))

# ── Cell 20 : Funding code ───────────────────────────────────────────────────
cells.append(code(r"""fund_raw  = pd.read_csv(FUND_PATH)
arch_fund = fund_raw[fund_raw['CategoryKey'] == 9].copy()
arch_fund_agg = (
    arch_fund[arch_fund['Year'] <= 2024]
    .groupby('Year')[['MaximumStudentContribution', 'CommonwealthContribution']]
    .mean()
    .round(0)
)
arch_fund_agg['total'] = arch_fund_agg['MaximumStudentContribution'] + arch_fund_agg['CommonwealthContribution']

print('=== Society & Culture: AUS Annual Funding per Student ===')
display(arch_fund_agg)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(arch_fund_agg.index, arch_fund_agg['MaximumStudentContribution'],
        'o-', color='tomato', linewidth=2, label='Student contribution')
ax.plot(arch_fund_agg.index, arch_fund_agg['CommonwealthContribution'],
        's-', color='mediumpurple', linewidth=2, label='Commonwealth contribution')
ax.axvline(2020.5, linestyle='--', color='gray', linewidth=1.2, label='JRG start (2021)')
ax.set_title('Society & Culture: AUS Annual Funding per Student')
ax.set_xlabel('Year'); ax.set_ylabel('Contribution ($)'); ax.legend()
plt.tight_layout()
plt.show()

pre_stu  = arch_fund_agg.loc[arch_fund_agg.index <= 2020, 'MaximumStudentContribution'].mean()
post_stu = arch_fund_agg.loc[arch_fund_agg.index >= 2021, 'MaximumStudentContribution'].mean()
pre_cw   = arch_fund_agg.loc[arch_fund_agg.index <= 2020, 'CommonwealthContribution'].mean()
post_cw  = arch_fund_agg.loc[arch_fund_agg.index >= 2021, 'CommonwealthContribution'].mean()
print(f'\nStudent contribution: pre ${pre_stu:,.0f} -> post ${post_stu:,.0f} ({(post_stu/pre_stu-1)*100:+.1f}%)')
print(f'Commonwealth:         pre ${pre_cw:,.0f} -> post ${post_cw:,.0f} ({(post_cw/pre_cw-1)*100:+.1f}%)')
"""))

# ── Cell 21 : Results Summary (placeholder — will be filled after execution) ─
cells.append(md(r"""## Results Summary

### Model specification

$$\log(E_{ct}) = \beta_0 + \beta_1 \cdot \text{Treated}_c + \beta_2 \cdot \text{DID}_{ct} + \sum_{t=2020}^{2024} \gamma_t \cdot \mathbf{1}_{[\text{year}=t]} + \varepsilon_{ct}$$

| Term | Variable | Definition |
|------|----------|------------|
| $\log(E_{ct})$ | Outcome | Log enrolments for country $c$ in year $t$ |
| $\beta_0$ | Intercept | UK baseline (2019) |
| $\beta_1 \cdot \text{Treated}_c$ | Country FE | $\text{Treated}_c = 1$ if AUS, $0$ if UK |
| $\text{Post}_t$ | --- | $= 1$ if $t \geq 2021$, else $0$ |
| $\text{DID}_{ct}$ | DiD term | $= \text{Treated}_c \times \text{Post}_t$ |
| $\beta_2$ | **JRG effect** | DiD estimate --- the coefficient of interest |
| $\gamma_t$ | Year FEs | Common time trend absorbed by year dummies (2020--2024) |
| $\varepsilon_{ct}$ | Error | HC3 heteroscedasticity-robust standard errors |

**Implemented in statsmodels as:**
```python
formula = "log_enrollments ~ treated + did + C(year)"
model   = smf.ols(formula, data=panel).fit(cov_type="HC3")
```

**Panel:** N = 12 (2 countries x 6 years, 2019-2024) | df = 4

*[Results table will be filled after notebook execution.]*

> **Data limitation:** UK panel restricted to 2019-2024 (N = 12, df = 4) due to irreconcilable
> JACS->CAH taxonomy break in 2019/20. Pre-2019 UK data at key = 9 contains only "04 Veterinary
> science" (~6-8K), a clear misassignment. Even reconstructing correct JACS subjects yields
> ~554-565K, leaving an irreconcilable ~167K gap vs post-2019 CAH totals (~731-788K) driven by
> Psychology having no JACS equivalent. Only 1 pre-treatment observation (2019) is available.
"""))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Written: {OUT}  ({len(cells)} cells)")
