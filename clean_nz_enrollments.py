"""
Clean NZ university enrollment data.

Source:  data/raw/2016-2025 New Zealand University Enrollments.xlsx  (FOS_ENR.2)
Output:  data/clean/NZ_bachelors_enrollments_2016_2025.csv

Extracts broad field of study rows for Bachelor's degrees (NZQF level 7) only,
years 2016-2025, with domestic, international, and total enrollment columns.

NOTE: FOS_ENR.2 covers ALL tertiary providers (universities, polytechnics, wananga,
private training establishments). University-specific historical data is not available
in this file — FOS_ENR.3 provides a sub-sector split but only for 2025. Based on the
2025 split, universities account for approximately 77% of bachelor enrollments across
all providers. This is flagged in the output.
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent
RAW  = ROOT / 'data' / 'raw' / '2016-2025 New Zealand University Enrollments.xlsx'
OUT  = ROOT / 'data' / 'clean' / 'NZ_bachelors_enrollments_2016_2025.csv'

# ── 1. Load FOS_ENR.2 ─────────────────────────────────────────────────────────
xl = pd.ExcelFile(RAW)
df = pd.read_excel(xl, sheet_name='FOS_ENR.2', header=None)

# ── 2. Locate Bachelor's degree columns ───────────────────────────────────────
# Row 2: qual type headers starting at col 3, stepping 30 cols each
# 'Bachelors degrees 7' starts at col 153
# Within that block: Domestic = cols 153-162, International = 163-172, Total = 173-182
# Years 2016-2025 map to offsets 0-9 within each 10-col block

YEARS = list(range(2016, 2026))

BACH_DOM_START  = 153   # Domestic bachelor cols
BACH_INTL_START = 163   # International bachelor cols
BACH_TOT_START  = 173   # Total bachelor cols

# ── 3. Define broad field rows and their category key mappings ────────────────
# Row index in df -> (clean label, category_key)
BROAD_FIELDS = {
    5:  ('Natural and Physical Sciences',              1),
    12: ('Information Technology',                     2),
    16: ('Engineering and Related Technologies',       3),
    27: ('Architecture and Building',                  4),
    30: ('Agriculture, Environmental and Related',     5),
    37: ('Health',                                     6),
    49: ('Education',                                  7),
    53: ('Management and Commerce',                    8),
    61: ('Society and Culture',                        9),
    74: ('Creative Arts',                             10),
    80: ('Food, Hospitality and Personal Services',   11),
    83: ('Mixed Field Programmes',                    11),
    88: ('Total (all fields)',                         0),
}

# ── 4. Extract data ───────────────────────────────────────────────────────────
records = []
for row_idx, (label, cat_key) in BROAD_FIELDS.items():
    for yr_offset, year in enumerate(YEARS):
        dom  = df.iloc[row_idx, BACH_DOM_START  + yr_offset]
        intl = df.iloc[row_idx, BACH_INTL_START + yr_offset]
        tot  = df.iloc[row_idx, BACH_TOT_START  + yr_offset]
        records.append({
            'field_of_study':         label,
            'category_key':           cat_key,
            'year':                   year,
            'domestic_bachelors':     int(dom)  if pd.notna(dom)  else None,
            'international_bachelors':int(intl) if pd.notna(intl) else None,
            'total_bachelors':        int(tot)  if pd.notna(tot)  else None,
        })

clean = pd.DataFrame(records)

# ── 5. Audit checks ───────────────────────────────────────────────────────────
print('=== NZ Bachelor Enrollment Data Audit ===')
print(f'Rows extracted: {len(clean)}')
print(f'Fields: {clean["field_of_study"].nunique()}')
print(f'Years: {sorted(clean["year"].unique())}')
print()

# Check for missing values
missing = clean[clean['total_bachelors'].isna()]
if len(missing):
    print(f'WARNING: {len(missing)} rows with missing total_bachelors:')
    print(missing[['field_of_study','year']].to_string())
else:
    print('No missing values in total_bachelors.')
print()

# Spot check: 2025 totals should match FOS_ENR.2 values we verified
print('2025 total_bachelors (spot check vs. raw file):')
for _, row in clean[clean['year'] == 2025].iterrows():
    print(f'  {row["field_of_study"]:45s} | dom={row["domestic_bachelors"]:>7} '
          f'| intl={row["international_bachelors"]:>6} | total={row["total_bachelors"]:>7}')
print()

# Cross-check domestic + international ~ total (within rounding)
clean['dom_intl_sum'] = (
    clean['domestic_bachelors'].fillna(0) + clean['international_bachelors'].fillna(0)
)
clean['rounding_gap'] = (clean['total_bachelors'] - clean['dom_intl_sum']).abs()
large_gaps = clean[clean['rounding_gap'] > 10]
if len(large_gaps):
    print(f'WARNING: {len(large_gaps)} rows where dom+intl differs from total by >10:')
    print(large_gaps[['field_of_study','year','domestic_bachelors',
                       'international_bachelors','total_bachelors','rounding_gap']].to_string())
else:
    print('Rounding check passed: dom + intl ~= total for all rows (within 10 students).')
print()

clean = clean.drop(columns=['dom_intl_sum', 'rounding_gap'])

# ── 6. University-only note (2025 ratios from FOS_ENR.3) ─────────────────────
df3 = pd.read_excel(xl, sheet_name='FOS_ENR.3', header=None)
# In FOS_ENR.3: Bachelors Total block — Universities=col88, All=col92 (2025 only)
print('=== University-Only Share (2025, from FOS_ENR.3) ===')
print('NOTE: FOS_ENR.2 (used for 2016-2025 data) includes ALL tertiary providers.')
print('FOS_ENR.3 provides a 2025-only breakdown. University share by field:')
for row_idx, (label, _) in BROAD_FIELDS.items():
    if row_idx == 88:
        continue
    uni   = df3.iloc[row_idx, 88]
    total = df3.iloc[row_idx, 92]
    if pd.notna(total) and total > 0:
        share = uni / total * 100
        print(f'  {label:45s} | Uni={int(uni):>6} | All={int(total):>6} | {share:.0f}% at universities')

grand_uni = df3.iloc[88, 88]
grand_all = df3.iloc[88, 92]
print(f'  {"Total":45s} | Uni={int(grand_uni):>6} | All={int(grand_all):>6} | {grand_uni/grand_all*100:.0f}% at universities')
print()
print('Recommendation: These ratios are relatively stable and could be used to')
print('scale the 2016-2025 totals to a university-only estimate if needed.')
print()

# ── 7. Save ───────────────────────────────────────────────────────────────────
OUT.parent.mkdir(parents=True, exist_ok=True)
clean.to_csv(OUT, index=False)
print(f'Saved: {OUT}')
print(f'Shape: {clean.shape}')
print()
print('Columns:', clean.columns.tolist())
