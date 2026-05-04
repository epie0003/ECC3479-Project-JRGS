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

## EDA Notebooks

The EDA notebooks are in `docs/EDA analysis/`. The two most important ones are:

- **`EDA Questions.ipynb`** — the primary analysis notebook; answers 10 structured EDA questions across all four datasets with visualisations and statistical tests.
- **`EDA Summary and Modelling Implications.ipynb`** — synthesises all EDA findings into concrete modelling requirements (fixed effects, log transformation, JRG indicator, COVID dummy, DiD specification).

Each individual dataset also has its own EDA notebook. Each of these ends with a short "What Is Learned" or "Data Characteristics" section that concisely summarises the key findings relevant to that dataset:

- `AUS Enrollments EDA.ipynb`
- `UK Enrollments EDA.ipynb`
- `AUS Student and Commonwealth Contributions EDA.ipynb` — per-unit funding rates by cluster and FOE
- `AUS Commonwealth Funding EDA.ipynb` — total funding aggregated by category and year
- `Employment by Industry EDA.ipynb`
- `AUS_Enrollments_Funding_Multivariate_EDA.ipynb`

A `Limitations.ipynb` notebook in `docs/` documents known data limitations (coverage gaps, missing values, structural breaks, aggregation decisions).

> **Note:** All EDA notebooks must be run top-to-bottom from a fresh kernel. `EDA Questions.ipynb` in particular depends on a setup cell that must execute first.

## Regression Analysis Notebooks

All regression notebooks are in `docs/Regression Analysis/`.

### Template and methodology

- **`DiD Modelling.ipynb`** — the foundational template notebook. Establishes the two-way fixed effects (TWFE) difference-in-differences specification (`log_enrollments ~ treated + nz_dummy + did + C(year)`, HC3 robust SEs), builds the 3-country panel (AUS vs UK + NZ), and documents all modelling decisions. All individual discipline notebooks follow this template directly.

### Data changes

- **`Data Changes During Regression Stage.ipynb`** — documents all data changes made after the EDA stage, including the addition of New Zealand as a second control country, the NZ category-key mapping, and any panel construction decisions that differ from the original two-country setup.

### Individual discipline notebooks

Each discipline has its own self-contained regression notebook that runs the full analysis pipeline — panel construction, main DiD, COVID sensitivity, event study, placebo test, level robustness, and funding context — for that field specifically:

| Notebook | Discipline | CategoryKey |
|----------|-----------|-------------|
| `REG Architecture & Building.ipynb` | Architecture & Building | 4 |
| `REG Creative Arts.ipynb` | Creative Arts | 10 |
| `REG Education.ipynb` | Education | 7 |
| `REG Engineering & Related Tech.ipynb` | Engineering & Related Tech | 3 |
| `REG Environment & Related.ipynb` | Environment & Related | 5 |
| `REG Health.ipynb` | Health | 6 |
| `REG Information Technology.ipynb` | Information Technology | 2 |
| `REG Management & Commerce.ipynb` | Management & Commerce | 8 |
| `REG Natural & Physical Science.ipynb` | Natural & Physical Science | 1 |
| `REG Others.ipynb` | Others | 11 |
| `REG Society & Culture.ipynb` | Society & Culture | 9 |

### Cross-discipline summaries

- **`REG All.ipynb`** — the master summary notebook. Runs the TWFE DiD for all 11 disciplines in a single pass and consolidates results into a unified comparison table with significance stars. Also includes the pooled triple-difference (DDD) test (`treated:post:priority`) that directly tests whether JRG produced a stronger enrolment shift in priority fields versus non-priority fields.
- **`REG Priority vs Non-Priority Disciplines.ipynb`** — standalone DDD regression notebook with full output for the priority vs non-priority specification.

> **Note:** Each discipline notebook is self-contained and can be run independently. All notebooks use the same TWFE formula and HC3 standard errors. Results in the individual notebooks match the corresponding rows in `REG All.ipynb` exactly.

## Using the Reproducible Code Scripts

The `code/` folder contains Python scripts that transform rates data into analysis-ready formats. These scripts are reproducible and can be run independently:

```powershell
# From the project root, activate the environment first
.\.venv\Scripts\Activate.ps1

# Run the rate-combination script (combines all yearly rate files)
python code\combine_rates.py

# Run the FOE-code merge script (merges discipline info by FOE code)
python code\merge_rates_by_foe_code.py

# Run the reshaping script (creates year-by-year comparison table)
python code\reshape_rates_comparison.py
```

Each script reads inputs from `rates/`, performs transformations, and outputs consolidated/reshaped CSVs back to `rates/`. They must be run in order (combine → merge → reshape).

## Raw Data Requirements

`data/raw/` contains source data where possible. Some files are not fully raw because the public source is only available as a pre-aggregated CSV or Excel export.

Before running the pipeline:

- Run notebooks from either the project root or the `docs/` folder. The notebook path logic only checks those two locations.
- If a downloaded file has a different name from the filenames below, rename it before running the notebooks.
- The notebooks create output directories automatically, but they do not create missing source-data folders or recreate missing prerequisite input files.

If any source file is missing, obtain it as follows:

1. Australian university enrollment/funding source:
	- https://app.powerbi.com/view?r=eyJrIjoiN2Y1ZTM1Y2YtYzYxNC00MWI0LWFhNTktYTI3NWU2OWI3NGFkIiwidCI6ImRkMGNmZDE1LTQ1NTgtNGIxMi04YmFkLWVhMjY5ODRmYzQxNyJ9
2. UK subject enrollment source:
	- https://www.hesa.ac.uk/news/27-01-2026/sb273-higher-education-student-statistics/subjects
3. Save downloaded files into:
	- `data/raw/`
	- `data/raw/UniEnrollmentsUK/` (and `UniEnrollmentsUK/` where notebook paths expect it)

Required input files and folders:

1. Australian enrollments notebook inputs
	- `data/raw/EnrollmentsAUS_category.csv`
	- `data/raw/EnrollmentsAUS_category_with_key.csv`
	- `data/raw/EnrollmentsAUS_attached.csv`
	- If either enrollment CSV is missing under `data/raw/`, seed it from `data/intermediary/raw/` before running notebooks.
2. UK enrollments notebook inputs
	- Place the UK CSV source files in both `data/raw/UniEnrollmentsUK/` and the top-level `UniEnrollmentsUK/` folder
	- The notebook reads from the top-level `UniEnrollmentsUK/` folder. The duplicate under `data/raw/UniEnrollmentsUK/` is kept as the raw-data copy.
	- The current repository uses these source files:
		- `2015-2019.csv`
		- `2016-2018.csv`
		- `2019.csv`
		- `2020-2025.csv`
3. Funding/rates notebook inputs
	- Place the yearly rate files in `rates/`
	- Excel rate files must preserve the workbook structure expected by the notebook, including a usable non-`Index` sheet with the required funding and discipline columns
	- The current repository uses these exact files:
		- `2019_allocation_of_units_of_study.csv`
		- `2020_allocation_of_units_of_study.csv`
		- `2021_allocation_of_units_of_study_Update07122021.xlsx`
		- `2022_allocation_of_units_of_study_Update07122021.xlsx`
		- `2023-allocation-of-units-of-study.xlsx`
		- `2024 allocation of units of study.xlsx`
		- `2025 Allocation of Units of Study.xlsx`
		- `2026 Allocation of Units of Study.xlsx`
4. Employment notebook inputs
	- `EmploymentShortages/` must contain the yearly OSL CSV files
	- `EmploymentOutcomes/industry_data_-_november_2025_revised (1).xlsx` must exist with that exact filename
	- The employment workbook must preserve the sheet structure expected by the notebook, including `Table_1`, `Table_2`, and `Table_3`
	- If you only have `data/raw/industry_data_-_november_2025_revised.xlsx`, copy or rename it to `EmploymentOutcomes/industry_data_-_november_2025_revised (1).xlsx` before running `docs/Employment Shortages AUS.ipynb`

Why some files are not strictly raw:

- Several sources are published only as already-tabulated exports, so the nearest available original download is stored.

## Clean Data Requirements

`data/clean/` contains the cleaned and merged datasets used in the analysis.

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

## Code Requirements

Project transformation scripts are stored in `code/`.

Scripts that transform source/rates data into cleaned comparison outputs:

1. `code/combine_rates.py`
2. `code/reshape_rates_comparison.py`
3. `code/merge_rates_by_foe_code.py`

These scripts reproduce the rate-comparison outputs when the README steps are followed.

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

Confirm the following inputs exist before running any notebooks:

- `data/raw/EnrollmentsAUS_category.csv`
- `data/raw/EnrollmentsAUS_category_with_key.csv`
- `data/raw/EnrollmentsAUS_attached.csv`
- `data/raw/UniEnrollmentsUK/`
- `UniEnrollmentsUK/`
- `rates/` with the yearly rate files listed above
- `EmploymentShortages/` with yearly OSL CSV files
- `EmploymentOutcomes/industry_data_-_november_2025_revised (1).xlsx`

If the two Australian enrollment CSVs are missing in `data/raw/`, run this once:

```powershell
Copy-Item data/intermediary/raw/EnrollmentsAUS_category.csv data/raw/EnrollmentsAUS_category.csv -Force
Copy-Item data/intermediary/raw/EnrollmentsAUS_category_with_key.csv data/raw/EnrollmentsAUS_category_with_key.csv -Force
```

Important notes:

- `EnrollmentsAUS_category_with_key.csv` is a required input to the enrollments notebook.
- The UK CSV files must be available in the top-level `UniEnrollmentsUK/` folder.
- If downloaded files use different names, rename them to the filenames listed in this README.

### 4. Run notebook data preparation (manual step)

Open and run these notebooks in order:

1. `docs/Data Collecting Notes/Raw Uni Enrollments AUS.ipynb`
2. `docs/Data Collecting Notes/UK Uni Enrollments RAW.ipynb`
3. `docs/Data Collecting Notes/AUS Uni Funding.ipynb`
4. `docs/Data Collecting Notes/Employment Shortages AUS.ipynb`

Notebook outputs and notes:

1. `docs/Data Collecting Notes/Raw Uni Enrollments AUS.ipynb`
	- Input: `data/raw/EnrollmentsAUS_category.csv`
	- Input: `data/raw/EnrollmentsAUS_category_with_key.csv`
	- Output: `data/clean/EnrollmentsAUS_category_with_numeric_key.csv`
2. `docs/Data Collecting Notes/UK Uni Enrollments RAW.ipynb`
	- Input: top-level `UniEnrollmentsUK/` folder and UK source CSV files
	- Output: `data/clean/uk_grouped/with_categorykey/UK_enrollments_grouped_comparison_all_years_with_categorykey.csv`
	- Output: year-by-year grouped UK files in `data/clean/uk_grouped/with_categorykey/`
	- Output: uncategorised grouped UK comparison file in `data/clean/uk_grouped/UK_enrollments_grouped_comparison_all_years.csv`
	- Output: category-name-enriched grouped UK files in `data/clean/uk_grouped/with_categorykey/with_category_name/`
3. `docs/Data Collecting Notes/AUS Uni Funding.ipynb`
	- Input: yearly rate files in `rates/`
	- Note: Excel workbooks must preserve the sheet and header structure expected by the notebook parser
	- Output: `data/clean/AnnualFundingAUS2019-2026_with_category_key.csv`
	- Output: `data/clean/AnnualFundingAUS2019-2026.csv`
	- Output: `data/intermediary/clean/AnnualFundingAUS2019-2026_category_summary.csv`
4. `docs/Data Collecting Notes/Employment Shortages AUS.ipynb`
	- Input: yearly OSL CSV files in `EmploymentShortages/`
	- Input: `EmploymentOutcomes/industry_data_-_november_2025_revised (1).xlsx`
	- Note: the employment workbook must preserve the expected `Table_1`/`Table_2`/`Table_3` structure, and `Table_2` must contain an `Industry` header row
	- Output: `data/clean/employment_by_industry_20y+keys.csv`
	- Output: `data/intermediary/clean/employment_by_industry_20y.csv`
	- Output: `data/intermediary/clean/employment_by_industry_20y_transposed.csv`

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

### 6. Verify primary clean outputs exist

After the notebooks and scripts finish, confirm that these primary analysis-ready files exist:

1. `data/clean/AnnualFundingAUS2019-2026_with_category_key.csv`
2. `data/clean/EnrollmentsAUS_category_with_numeric_key.csv`
3. `data/clean/employment_by_industry_20y+keys.csv`
4. `data/clean/uk_grouped/with_categorykey/UK_enrollments_grouped_comparison_all_years_with_categorykey.csv`
5. `rates/combined_allocation_of_units_of_study.csv`
6. `rates/allocation_of_units_of_study_year_comparison.csv`
7. `rates/allocation_of_units_of_study_year_comparison_by_foe_code.csv`

## Submission Rules Coverage

- All project files are intended to be tracked and submitted via GitHub.
- The analysis-ready data can be reproduced by following this README when the required source files are present under the filenames and folders listed above.

Recommended pre-submission checks:

```bash
git status
git ls-files
```

## Author

Individual project submission.
