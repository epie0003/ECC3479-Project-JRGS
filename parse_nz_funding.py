"""
Parse NZ TEC SAC funding rates (government subsidy per EFTS, excl. GST) from all available files.
Also parses Universities NZ domestic tuition fee PDFs.

TEC SAC = Student Achievement Component = government subsidy per EFTS at each qualification level.
Level 2 = undergraduate degree programmes (bachelors) — the column we extract.

Output: data/raw/NZ Funding/NZ_TEC_SAC_rates_all_years.csv
        data/raw/NZ Funding/NZ_UniversitiesNZ_domestic_fees_all_years.csv
"""

import pdfplumber
import pandas as pd
import numpy as np
import re
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

RAW = Path(r'C:\Users\neddp\ECC3479-Project-JRGS\data\raw\NZ Funding')

def clean_dollar(s):
    if s is None: return None
    s = str(s).replace('$','').replace(',','').strip()
    # Period-as-thousands-separator (e.g. '17.602' in 2016 PDF → 17602)
    if re.match(r'^\d+\.\d{3}$', s):
        s = s.replace('.', '')
    try:
        v = float(s)
        return v if v > 0 else None
    except:
        return None

def clean_text(s):
    if s is None: return ''
    return re.sub(r'\s+', ' ', str(s).strip()).strip()

# ══════════════════════════════════════════════════════════════════════════════
# PART 1 — TEC SAC Government Subsidy Rates
# ══════════════════════════════════════════════════════════════════════════════

def parse_tec_pdf(path, year):
    """
    Robust TEC PDF parser. Handles column layout variations and multi-page tables.
    Identifies the Level 2 (undergraduate degree) column from any header row,
    then applies those column positions across ALL tables in the PDF.
    """
    rows = []
    lvl2_col = None        # persist across pages once found
    header_col_count = None  # column count of the table where header was found

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for tbl in tables:
                if not tbl: continue
                tbl_col_count = len(tbl[0])

                # Scan for a header row with level number markers
                header_ri = None
                for ri, row in enumerate(tbl):
                    cells = [clean_text(c) for c in row]
                    if '2' in cells and '1' in cells:
                        lvl2_col = cells.index('2')
                        header_ri = ri
                        header_col_count = tbl_col_count
                        break

                # Process data rows — skip the header block if found on this table
                start_row = (header_ri + 1) if header_ri is not None else 0

                if lvl2_col is None:
                    continue  # Haven't found header yet anywhere

                # Adjust lvl2_col when continuation pages have more columns than the
                # header page (e.g. 2019 PDF: page 1 = 16 cols, page 2 = 18 cols → +2)
                if header_col_count and tbl_col_count != header_col_count:
                    effective_lvl2_col = lvl2_col + (tbl_col_count - header_col_count)
                else:
                    effective_lvl2_col = lvl2_col

                current_code = None
                for row in tbl[start_row:]:
                    cells = [clean_text(c) for c in row]
                    if not any(cells): continue

                    # Skip descriptor-only continuation header rows
                    if all(len(c) > 20 or c == '' for c in cells[:3]):
                        continue

                    # Category code: check cells[0], then cells[1] (some PDFs put code at index 1)
                    code_cand = cells[0] if cells else ''
                    col_offset = 0
                    if not re.match(r'^[A-Z]', code_cand) and len(cells) > 1:
                        code_cand = cells[1]
                        col_offset = 1  # code shifted right → data columns also shift right

                    code_match = re.match(r'^([A-Z]{1,2})', code_cand)
                    if code_match:
                        current_code = code_match.group(1)

                    # Description: first cell with meaningful length
                    desc = next((c for c in cells if len(c) > 5), '')

                    # Level 2 value — apply col_offset for rows where code is at cells[1]
                    lvl2_idx = effective_lvl2_col + col_offset
                    lvl2_raw = cells[lvl2_idx] if 0 <= lvl2_idx < len(cells) else ''
                    lvl2 = clean_dollar(lvl2_raw)

                    if current_code and desc and lvl2:
                        rows.append({
                            'year': year,
                            'category_code': current_code,
                            'description': desc,
                            'sac_rate_level2_excl_gst': lvl2,
                        })
    return rows


def parse_tec_xlsx(path, years_wanted):
    """
    Extract SAC rates from TEC XLSX DQ7+ / DQ7-10 sheet for one or more years.
    Returns dict: {year: [rows]}.
    """
    xl = pd.ExcelFile(path)
    sheet = 'DQ7+' if 'DQ7+' in xl.sheet_names else 'DQ7-10'
    df = pd.read_excel(xl, sheet_name=sheet, header=None)

    # Row 0: e.g. '2024 DQ7+ Funding Rates', '2023 DQ7+ Funding Rates'
    header_row = df.iloc[0]
    year_col_starts = {}
    for ci, val in enumerate(header_row):
        if pd.notna(val):
            m = re.search(r'(\d{4})', str(val))
            if m:
                yr = int(m.group(1))
                if yr not in year_col_starts:
                    year_col_starts[yr] = ci

    results = {yr: [] for yr in years_wanted}

    for yr in years_wanted:
        if yr not in year_col_starts:
            continue
        base = year_col_starts[yr]
        # Cols: base=cat, base+1=desc, base+2=L1, base+3=L2, base+4=L3, base+5=L4
        current_code = None
        for ri in range(3, len(df)):
            row = df.iloc[ri]
            code = clean_text(row.iloc[base]) if base < len(row) else ''
            desc = clean_text(row.iloc[base+1]) if base+1 < len(row) else ''
            lvl2_raw = row.iloc[base+3] if base+3 < len(row) else None

            if re.match(r'^[A-Z]{1,2}$', code):
                current_code = code

            lvl2 = None
            if pd.notna(lvl2_raw):
                try:
                    lvl2 = float(lvl2_raw)
                    if lvl2 <= 0: lvl2 = None
                except:
                    pass

            if current_code and len(desc) > 5 and lvl2:
                results[yr].append({
                    'year': yr,
                    'category_code': current_code,
                    'description': desc,
                    'sac_rate_level2_excl_gst': lvl2,
                })
    return results


# ── Process TEC PDFs (2016-2022) ──────────────────────────────────────────────
print('=== TEC SAC Rates ===')
tec_records = []

pdf_years = {
    2016: RAW / 'TEC_SAC_funding_rates_2016.pdf',
    2017: RAW / 'TEC_SAC_funding_rates_2017.pdf',
    2018: RAW / 'TEC_SAC_funding_rates_2018.pdf',
    2019: RAW / 'TEC_SAC_funding_rates_2019.pdf',
    2020: RAW / 'TEC_SAC_funding_rates_2020.pdf',
    2021: RAW / 'TEC_SAC_funding_rates_2021.pdf',
    2022: RAW / 'TEC_SAC_funding_rates_2022.pdf',
}

for year, path in pdf_years.items():
    if path.exists():
        recs = parse_tec_pdf(path, year)
        tec_records.extend(recs)
        print(f'  PDF {year}: {len(recs)} rows  | categories: {sorted(set(r["category_code"] for r in recs))}')
    else:
        print(f'  PDF {year}: FILE NOT FOUND')

# ── Process TEC XLSXs (2023-2025) ─────────────────────────────────────────────
xlsx_map = {
    (RAW / 'TEC_SAC_funding_rates_2023_2024.xlsx'): [2023, 2024],
    (RAW / 'TEC_SAC_funding_rates_2024_2025.xlsx'): [2025],
}

for path, years in xlsx_map.items():
    if path.exists():
        res = parse_tec_xlsx(path, years)
        for yr, recs in res.items():
            tec_records.extend(recs)
            print(f'  XLSX {yr}: {len(recs)} rows  | categories: {sorted(set(r["category_code"] for r in recs))}')
    else:
        print(f'  XLSX {path.name}: FILE NOT FOUND')

tec_df = pd.DataFrame(tec_records).sort_values(['year','category_code']).reset_index(drop=True)
tec_out = RAW / 'NZ_TEC_SAC_rates_all_years.csv'
tec_df.to_csv(tec_out, index=False, encoding='utf-8')
print(f'\nSaved: {tec_out}  ({len(tec_df)} rows, {tec_df["year"].nunique()} years)')

# Preview: Level-2 rate for key categories across years
print('\n=== Level 2 SAC rates for key categories (govt subsidy per EFTS, excl GST) ===')
pivot = tec_df[tec_df['category_code'].isin(['A','B','C','H','I','J','N','V'])].copy()
pivot['first_desc'] = pivot.groupby(['year','category_code'])['description'].transform('first')
pt = pivot.drop_duplicates(['year','category_code']).pivot(
    index='category_code', columns='year', values='sac_rate_level2_excl_gst'
)
print(pt.to_string())
print()

# ══════════════════════════════════════════════════════════════════════════════
# PART 2 — Universities NZ Domestic Tuition Fees
# ══════════════════════════════════════════════════════════════════════════════

def parse_uninz_pdf(path, year):
    """
    Extract domestic undergraduate tuition fees from a Universities NZ PDF.
    PDFs are organised per-university: University header → Undergraduate section → rows.
    Fee format is '$X,XXX - $Y,YYY' or '$X,XXX $Y,YYY' or '$X,XXX' within one cell.
    Returns one row per university per programme with min/max fees.
    """
    UNI_MARKERS = [
        'university of auckland', 'auckland university of technology', 'aut university',
        'university of waikato', 'massey university', 'victoria university',
        'university of canterbury', 'lincoln university', 'university of otago',
    ]
    PG_MARKERS = ['postgraduate', 'honours', '*master', '*phd', '*doctor', '*graduate',
                  'research degree', 'tuition fees are for']

    rows = []
    current_uni = None
    in_undergrad = False

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for tbl in tables:
                for row in tbl:
                    if not row: continue
                    cells = [clean_text(c) for c in row]
                    field = cells[0] if cells else ''
                    if not field: continue

                    flower = field.lower()

                    # Detect university header
                    if any(u in flower for u in UNI_MARKERS):
                        current_uni = field
                        in_undergrad = False
                        continue

                    # Detect start of undergraduate section
                    if 'undergraduate' in flower and 'post' not in flower:
                        in_undergrad = True
                        continue

                    # Detect end of undergraduate section (postgrad or notes rows)
                    if in_undergrad and any(m in flower for m in PG_MARKERS):
                        in_undergrad = False
                        continue

                    if not in_undergrad or not current_uni:
                        continue

                    # Skip notes/disclaimers (very long lines)
                    if len(field) > 120:
                        in_undergrad = False
                        continue

                    # Extract dollar amounts from all cells using regex
                    # Handles: '$5,767', '$ 6,418 - $ 6,418', '$5,767 $6,652', etc.
                    nums = []
                    for c in cells:
                        for m in re.findall(r'\$\s*([\d,]+)', c):
                            try:
                                v = float(m.replace(',', ''))
                                if 1000 < v < 75000:
                                    nums.append(v)
                            except:
                                pass

                    if nums:
                        rows.append({
                            'year': year,
                            'university': current_uni,
                            'programme': field[:100],
                            'min_fee_nzd': int(min(nums)),
                            'max_fee_nzd': int(max(nums)),
                        })
    return rows


print('=== Universities NZ Domestic Fees ===')
uninz_records = []

uninz_files = {
    2016: RAW / 'UniversitiesNZ_domestic_fees_2016.pdf',
    2017: RAW / 'UniversitiesNZ_domestic_fees_2017.pdf',
    2022: RAW / 'UniversitiesNZ_domestic_fees_2022.pdf',
    2023: RAW / 'UniversitiesNZ_domestic_fees_2023.pdf',
    2024: RAW / 'UniversitiesNZ_domestic_fees_2024.pdf',
}

for year, path in sorted(uninz_files.items()):
    if path.exists():
        recs = parse_uninz_pdf(path, year)
        uninz_records.extend(recs)
        unis = sorted(set(r['university'] for r in recs))
        print(f'  {year}: {len(recs)} rows across {len(unis)} universities')
        if recs:
            # Summary: overall fee range across all undergraduate programmes
            all_mins = [r['min_fee_nzd'] for r in recs]
            all_maxs = [r['max_fee_nzd'] for r in recs]
            print(f'    Fee range: ${min(all_mins):,} - ${max(all_maxs):,}  '
                  f'avg_min=${int(np.mean(all_mins)):,}  avg_max=${int(np.mean(all_maxs)):,}')
        for r in recs[:4]:
            print(f'    {r["university"][:30]:30s} | {r["programme"][:40]:40s} '
                  f'| ${r["min_fee_nzd"]:,}-${r["max_fee_nzd"]:,}')
        if len(recs) > 4: print(f'    ... ({len(recs)-4} more)')
    else:
        print(f'  {year}: FILE NOT FOUND')
    print()

if uninz_records:
    uninz_df = pd.DataFrame(uninz_records)
    # Also save an annual summary (avg min/max across all programmes × universities)
    summary = uninz_df.groupby('year').agg(
        n_records=('min_fee_nzd','count'),
        overall_min_fee=('min_fee_nzd','min'),
        overall_max_fee=('max_fee_nzd','max'),
        avg_of_min_fees=('min_fee_nzd', lambda x: int(x.mean())),
        avg_of_max_fees=('max_fee_nzd', lambda x: int(x.mean())),
    ).reset_index()
    uninz_out = RAW / 'NZ_UniversitiesNZ_domestic_fees_all_years.csv'
    uninz_df.to_csv(uninz_out, index=False, encoding='utf-8')
    summary_out = RAW / 'NZ_UniversitiesNZ_domestic_fees_summary.csv'
    summary.to_csv(summary_out, index=False, encoding='utf-8')
    print(f'Saved: {uninz_out}  ({len(uninz_df)} rows)')
    print(f'Saved: {summary_out}')
    print()
    print('Annual summary:')
    print(summary.to_string(index=False))
else:
    print('No Universities NZ fee records extracted — PDFs may need manual review.')
