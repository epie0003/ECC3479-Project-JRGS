# ECC3479 Project - JRGS

## Project Question

Did the Job-ready Graduates Package increase student enrollments in STEM, languages, education, and healthcare compared with arts and humanities?

## Software Information

- Language: Python 3.10+
- Main packages: pandas, openpyxl, jupyter, matplotlib, numpy, selenium
- Environment: virtual environment (`.venv`)
- OS tested: Windows (PowerShell)

Install commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas openpyxl jupyter matplotlib numpy selenium
```

## Repository Structure

- `data/raw/`: source/raw files where available
- `data/intermediary/`: intermediate outputs produced during cleaning and reshaping
- `data/clean/`: cleaned/analysis-ready datasets with category keys
- `docs/`: Jupyter notebooks for extraction, cleaning, and analysis setup
- `code/`: reproducible transformation scripts
- `rates/`: annual fee/rate files and generated rate-comparison outputs
- `EmploymentShortages/`: yearly occupation shortage list files
- `EmploymentOutcomes/`: employment-related outputs/assets
- `UniEnrollmentsUK/`: UK source files used in the pipeline

## data/raw Requirements

`data/raw/` contains raw source data where possible. If a file is not purely raw, it is included because the public source provides pre-aggregated exports rather than record-level dumps.

If any raw file is missing, obtain it as follows:

1. Australian university enrollment/funding source:
	- https://app.powerbi.com/view?r=eyJrIjoiN2Y1ZTM1Y2YtYzYxNC00MWI0LWFhNTktYTI3NWU2OWI3NGFkIiwidCI6ImRkMGNmZDE1LTQ1NTgtNGIxMi04YmFkLWVhMjY5ODRmYzQxNyJ9
2. UK subject enrollment source:
	- https://www.hesa.ac.uk/news/27-01-2026/sb273-higher-education-student-statistics/subjects
3. Save downloaded files into:
	- `data/raw/`
	- `data/raw/UniEnrollmentsUK/` (and `UniEnrollmentsUK/` where notebook paths expect it)

Reason some files may not be strictly raw:

- Several sources are published as already-tabulated exports (CSV/XLSX), so the nearest available original download is stored.

## data/clean Requirements

`data/clean/` contains cleaned and merged datasets used for analysis.

Primary cleaned datasets:

1. `data/clean/AnnualFundingAUS2019-2026_with_category_key.csv`
2. `data/clean/EnrollmentsAUS_category_with_numeric_key.csv`
3. `data/clean/employment_by_industry_20y+keys.csv`
4. `data/clean/uk_grouped/with_categorykey/UK_enrollments_grouped_comparison_all_years_with_categorykey.csv`

### Data Codebook (Variables)

`data/clean/AnnualFundingAUS2019-2026_with_category_key.csv`

- `Year`: calendar/funding year
- `FOE`: field of education code
- `FOE_Description`: field of education description
- `FundingCluster`: funding cluster assignment
- `MaximumStudentContribution`: max student contribution amount
- `CommonwealthContribution`: commonwealth contribution amount
- `FOE_Broad`: broad FOE grouping
- `CategoryKey`: numeric category identifier used for joins
- `Category`: analysis category label

`data/clean/EnrollmentsAUS_category_with_numeric_key.csv`

- `Category`: analysis category label
- `2016` ... `2024`: annual enrollment counts by category
- `CategoryKey`: numeric category identifier used for joins

`data/clean/employment_by_industry_20y+keys.csv`

- `Industry`: industry name
- `Category`: mapped analysis category
- `CategoryKey`: numeric category identifier used for joins
- `Nov-05` ... `Nov-25`: quarterly employment count timeseries columns

## code Requirements

Project transformation scripts are in `code/`.

Scripts that transform source/rates data into cleaned comparison outputs:

1. `code/combine_rates.py`
2. `code/reshape_rates_comparison.py`
3. `code/merge_rates_by_foe_code.py`

These scripts reproduce outputs on another machine when the README steps are followed.

## Reproducibility: Run From Scratch

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd ECC3479-Project-JRGS
```

### 2. Set up Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas openpyxl jupyter matplotlib numpy selenium
```

### 3. Confirm required input data exists

Check these folders contain expected source files:

- `data/raw/`
- `data/raw/UniEnrollmentsUK/`
- `rates/` (yearly CSV/XLSX files)

### 4. Run notebook data preparation (manual step)

Open and run these notebooks in order:

1. `docs/Raw Uni Enrollments AUS.ipynb`
2. `docs/UK Uni Enrollments RAW.ipynb`
3. `docs/AUS Uni Funding.ipynb`
4. `docs/Employment Shortages AUS.ipynb`

### 5. Run scripts in required order

```bash
python code/combine_rates.py
python code/reshape_rates_comparison.py
python code/merge_rates_by_foe_code.py
```

Pipeline dependencies:

1. `code/combine_rates.py`
	- Input: yearly files in `rates/`
	- Output: `rates/combined_allocation_of_units_of_study.csv`
2. `code/reshape_rates_comparison.py`
	- Input: `rates/combined_allocation_of_units_of_study.csv`
	- Output: `rates/allocation_of_units_of_study_year_comparison.csv`
3. `code/merge_rates_by_foe_code.py`
	- Input: `rates/allocation_of_units_of_study_year_comparison.csv`
	- Output: `rates/allocation_of_units_of_study_year_comparison_by_foe_code.csv`

## Submission Rules Coverage

- All project files are intended to be tracked and submitted via GitHub.
- The analysis-ready data can be reproduced by following this README (manual source download + notebook preparation + script pipeline).

Recommended pre-submission checks:

```bash
git status
git ls-files
```

## Author

Individual project submission.
