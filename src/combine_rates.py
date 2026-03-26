from pathlib import Path

import pandas as pd


RATES_DIR = Path(__file__).resolve().parent.parent / "rates"
OUTPUT_PATH = RATES_DIR / "combined_allocation_of_units_of_study.csv"


def normalize_label(value: object, prefix: str, negative_label: str) -> str:
    if pd.isna(value):
        return negative_label

    text = str(value).strip()
    if not text:
        return negative_label

    lowered = text.lower()
    if lowered in {"nan", "none", "", negative_label.lower()}:
        return negative_label
    if text.isdigit() or lowered.endswith(".0"):
        try:
            return str(int(float(text)))
        except ValueError:
            return f"{prefix}{text}"
    return text


def build_category_lookup() -> pd.DataFrame:
    category_frames = []

    for path in sorted(RATES_DIR.glob("*.xlsx")):
        year = int("".join(ch for ch in path.name if ch.isdigit())[:4])
        sheet_name = [sheet for sheet in pd.ExcelFile(path).sheet_names if sheet != "Index"][0]
        df = pd.read_excel(path, sheet_name=sheet_name)
        categories = df[
            [
                "Discipline Code\n(FOE)",
                "DETAILED Discipline (FOE) - Title",
                "DETAILED Discipline (FOE) ",
                "NARROW Discipline (FOE) ",
                "BROAD Discipline (FOE) ",
            ]
        ].copy()
        categories.columns = [
            "foe_code",
            "detailed_discipline_title",
            "detailed_discipline",
            "narrow_discipline",
            "broad_discipline",
        ]
        categories["foe_code"] = categories["foe_code"].astype(str).str.extract(r"(\d+)")[0].str.zfill(6)
        categories["year"] = year
        category_frames.append(categories.drop_duplicates())

    all_categories = pd.concat(category_frames, ignore_index=True)
    all_categories = all_categories.sort_values("year").drop_duplicates(subset=["foe_code"], keep="last")
    return all_categories.drop(columns=["year"])


def load_csv_year(path: Path, lookup: pd.DataFrame) -> pd.DataFrame:
    year = int(path.name[:4])
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "FundingCluster": "funding_cluster",
            "E312of27": "special_course_type_code",
            "FOE": "foe_code",
            f"{year}MaximumStudentContibution": "maximum_student_contribution",
            f"{year}CommonwealthContribution": "commonwealth_contribution",
        }
    )
    df["year"] = year
    df["foe_code"] = df["foe_code"].astype(str).str.extract(r"(\d+)")[0].str.zfill(6)
    df["special_course_type_code"] = df["special_course_type_code"].apply(
        lambda value: normalize_label(value, "", "Not E312=27")
    )
    df["maximum_student_contribution_indicator"] = "Not E392=8"
    df["funding_cluster_varies"] = df["special_course_type_code"].ne("Not E312=27").map({True: "Yes", False: "No"})
    df["grandfathered_maximum_student_contribution"] = pd.NA
    df["grandfathered_commonwealth_contribution"] = pd.NA

    df = df.merge(lookup, on="foe_code", how="left")
    return df[
        [
            "year",
            "foe_code",
            "funding_cluster",
            "special_course_type_code",
            "maximum_student_contribution_indicator",
            "funding_cluster_varies",
            "maximum_student_contribution",
            "commonwealth_contribution",
            "grandfathered_maximum_student_contribution",
            "grandfathered_commonwealth_contribution",
            "detailed_discipline_title",
            "detailed_discipline",
            "narrow_discipline",
            "broad_discipline",
        ]
    ]


def load_excel_year(path: Path) -> pd.DataFrame:
    year = int("".join(ch for ch in path.name if ch.isdigit())[:4])
    sheet_name = [sheet for sheet in pd.ExcelFile(path).sheet_names if sheet != "Index"][0]
    df = pd.read_excel(path, sheet_name=sheet_name)
    df = df.rename(
        columns={
            "Funding Cluster": "funding_cluster",
            f"{year} \nFunding Cluster": "funding_cluster",
            "Discipline Code\n(FOE)": "foe_code",
            f"{year} Maximum Student Contibution": "maximum_student_contribution",
            f"{year} Commonwealth Contribution": "commonwealth_contribution",
            f"{year} Grandfathered Maximum Student Contibution": "grandfathered_maximum_student_contribution",
            f"{year} Grandfathered Commonwealth Contribution": "grandfathered_commonwealth_contribution",
            "Funding Cluster varies for FOE depending on E327 or E392 (Yes/No)": "funding_cluster_varies",
            "Funding Cluster varies for FOE depending on E312 or E392 (Yes/No)": "funding_cluster_varies",
            "Special Course Type Code for the Course of Study\n(E312 of 27)": "special_course_type_code",
            "Maximum student contribution indicator\n(E392 =8)": "maximum_student_contribution_indicator",
            "DETAILED Discipline (FOE) - Title": "detailed_discipline_title",
            "DETAILED Discipline (FOE) ": "detailed_discipline",
            "NARROW Discipline (FOE) ": "narrow_discipline",
            "BROAD Discipline (FOE) ": "broad_discipline",
        }
    )
    df["year"] = year
    df["foe_code"] = df["foe_code"].astype(str).str.extract(r"(\d+)")[0].str.zfill(6)
    df["special_course_type_code"] = df["special_course_type_code"].apply(
        lambda value: normalize_label(value, "", "Not E312=27")
    )
    df["maximum_student_contribution_indicator"] = df["maximum_student_contribution_indicator"].apply(
        lambda value: normalize_label(value, "", "Not E392=8")
    )
    return df[
        [
            "year",
            "foe_code",
            "funding_cluster",
            "special_course_type_code",
            "maximum_student_contribution_indicator",
            "funding_cluster_varies",
            "maximum_student_contribution",
            "commonwealth_contribution",
            "grandfathered_maximum_student_contribution",
            "grandfathered_commonwealth_contribution",
            "detailed_discipline_title",
            "detailed_discipline",
            "narrow_discipline",
            "broad_discipline",
        ]
    ]


def main() -> None:
    lookup = build_category_lookup()
    frames = []

    for path in sorted(RATES_DIR.iterdir()):
        suffix = path.suffix.lower()
        if suffix == ".csv" and path.name[:4].isdigit():
            frames.append(load_csv_year(path, lookup))
        elif suffix in {".xlsx", ".xls"} and any(ch.isdigit() for ch in path.name):
            frames.append(load_excel_year(path))

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(
        [
            "year",
            "foe_code",
            "special_course_type_code",
            "maximum_student_contribution_indicator",
            "funding_cluster",
        ]
    ).reset_index(drop=True)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(combined)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
