from pathlib import Path

import pandas as pd


RATES_DIR = Path(__file__).resolve().parent.parent / "rates"
INPUT_PATH = RATES_DIR / "allocation_of_units_of_study_year_comparison.csv"
OUTPUT_PATH = RATES_DIR / "allocation_of_units_of_study_year_comparison_by_foe_code.csv"


def merge_values(series: pd.Series):
    values = [value for value in series if pd.notna(value) and str(value).strip() != ""]
    if not values:
        return pd.NA

    unique_values = []
    seen = set()
    for value in values:
        normalized = str(value).strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_values.append(value)

    if len(unique_values) == 1:
        return unique_values[0]

    return " | ".join(str(value) for value in unique_values)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    ordered_columns = [
        "foe_code",
        "detailed_discipline_title",
        "detailed_discipline",
        "narrow_discipline",
        "broad_discipline",
    ] + [column for column in df.columns if column not in {
        "foe_code",
        "detailed_discipline_title",
        "detailed_discipline",
        "narrow_discipline",
        "broad_discipline",
    }]

    merged = (
        df.groupby("foe_code", dropna=False, as_index=False)
        .agg({column: merge_values for column in df.columns if column != "foe_code"})
    )

    merged = merged[ordered_columns].sort_values("foe_code").reset_index(drop=True)
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(merged)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
