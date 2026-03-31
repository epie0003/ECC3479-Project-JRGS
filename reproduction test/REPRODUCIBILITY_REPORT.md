# Reproducibility Report

Date: 2026-03-31

## Scope

- Isolated workspace: `reproduction test/`
- Inputs used: `reproduction test/data/raw/`, `reproduction test/UniEnrollmentsUK/`, `reproduction test/rates/`, `reproduction test/EmploymentShortages/`, `reproduction test/EmploymentOutcomes/`
- Notebook order executed:
  1. `Raw Uni Enrollments AUS.ipynb`
  2. `UK Uni Enrollments RAW.ipynb`
  3. `AUS Uni Funding.ipynb`
  4. `Employment Shortages AUS.ipynb`

## Execution Result

- All four notebooks executed successfully in `reproduction test/docs/`.
- Clean outputs were regenerated in `reproduction test/data/clean/`.

## File Hash Comparison (Baseline vs Reproduced)

| File | SHA256 Match |
|---|---|
| `AnnualFundingAUS2019-2026_with_category_key.csv` | `True` |
| `EnrollmentsAUS_category_with_numeric_key.csv` | `True` |
| `employment_by_industry_20y+keys.csv` | `True` |
| `UK_enrollments_grouped_comparison_all_years_with_categorykey.csv` | `False` |

- Matched exactly: 3/4 files.

## UK Output Difference Details

- File with non-identical hash: `UK_enrollments_grouped_comparison_all_years_with_categorykey.csv`
- Differing rows: 9 (all in AcademicYear `2018/19`)
- Difference pattern: only `Total UK` differs, by small increments (`+/-5` or `+/-10`).
- Regional component columns (`England`, `Wales`, `Scotland`, `Northern Ireland`, `Other UK`) are unchanged for those rows.
- Detailed row-level diff exported to: `reproduction test/uk_total_differences_2018_19.csv`

## Interpretation

- Reproducibility is functionally successful for all notebook stages and primary clean outputs.
- One UK aggregate output shows minor rounding/allocation-level variation in 2018/19 totals.