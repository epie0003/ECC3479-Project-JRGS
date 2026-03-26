from pathlib import Path

import pandas as pd


RATES_DIR = Path(__file__).resolve().parent.parent / "rates"
INPUT_PATH = RATES_DIR / "combined_allocation_of_units_of_study.csv"
OUTPUT_PATH = RATES_DIR / "allocation_of_units_of_study_year_comparison.csv"


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    index_columns = [
        "foe_code",
        "detailed_discipline_title",
        "detailed_discipline",
        "narrow_discipline",
        "broad_discipline",
        "special_course_type_code",
        "maximum_student_contribution_indicator",
    ]

    value_columns = [
        "funding_cluster",
        "funding_cluster_varies",
        "maximum_student_contribution",
        "commonwealth_contribution",
        "grandfathered_maximum_student_contribution",
        "grandfathered_commonwealth_contribution",
    ]

    comparison = (
        df.pivot_table(
            index=index_columns,
            columns="year",
            values=value_columns,
            aggfunc="first",
        )
        .sort_index(axis=1, level=[0, 1])
        .reset_index()
    )

    comparison.columns = [
        f"{value}_{year}" if isinstance(year, (int, float)) else value
        for value, year in comparison.columns.to_flat_index()
    ]

    comparison = comparison.sort_values(
        [
            "broad_discipline",
            "narrow_discipline",
            "detailed_discipline",
            "foe_code",
            "special_course_type_code",
            "maximum_student_contribution_indicator",
        ]
    ).reset_index(drop=True)

    comparison.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(comparison)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()