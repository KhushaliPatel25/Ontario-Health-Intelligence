
from pathlib import Path
import pandas as pd

# Project locations
project_dir = Path(__file__).resolve().parent.parent

input_file = (
    project_dir / "data" / "processed"
    / "ontario_ed_all_records.csv"
)

output_file = (
    project_dir / "data" / "processed"
    / "data_quality_by_level_year.csv"
)

print("ONTARIO HEALTH INTELLIGENCE")
print("DATA QUALITY DATASET PREPARATION")
print("=" * 60)

# Step 1: Load cleaned Ontario records
df = pd.read_csv(
    input_file,
    dtype=str,
    keep_default_na=False
)

df.columns = df.columns.str.strip()

# Step 2: Identify numeric measurements
df["numeric_value"] = pd.to_numeric(
    df["wait_time_p90"],
    errors="coerce"
)

df["numeric_record"] = (
    df["numeric_value"].notna().astype(int)
)

# Step 3: Identify suppressed measurements
df["suppressed_record"] = (
    df["90th percentile"]
    .str.strip()
    .str.casefold()
    .eq("suppressed")
    .astype(int)
)

# Step 4: Detect any other missing values
df["other_missing_record"] = (
    (df["numeric_record"] == 0)
    & (df["suppressed_record"] == 0)
).astype(int)

# Step 5: Summarize by year and reporting level
summary = df.groupby(
    ["Time frame", "Reporting level"],
    dropna=False
).agg(
    total_records=("numeric_record", "size"),
    numeric_records=("numeric_record", "sum"),
    suppressed_records=("suppressed_record", "sum"),
    other_missing_records=("other_missing_record", "sum")
).reset_index()

# Step 6: Rename columns
summary = summary.rename(columns={
    "Time frame": "fiscal_year",
    "Reporting level": "reporting_level"
})

# Step 7: Calculate numeric completeness
summary["completeness_percent"] = (
    summary["numeric_records"]
    / summary["total_records"] * 100
).round(2)

# Step 8: Create fiscal year sorting column
summary["fiscal_start_year"] = (
    pd.to_numeric(
        summary["fiscal_year"].str.extract(
            r"(\d{4})"
        )[0],
        errors="coerce"
    ).astype("Int64")
)

summary = summary.sort_values(
    ["fiscal_start_year", "reporting_level"]
)

# Step 9: Verify dataset totals
total = int(summary["total_records"].sum())
numeric = int(summary["numeric_records"].sum())
suppressed = int(summary["suppressed_records"].sum())
other_missing = int(
    summary["other_missing_records"].sum()
)

if (
    total != 1204
    or numeric != 1163
    or suppressed != 41
    or other_missing != 0
):
    raise ValueError(
        "Data quality totals do not match "
        "the previously validated audit."
    )

# Step 10: Export the Power BI dataset
summary.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

# Display results
print(f"\nTotal Ontario records: {total}")
print(f"Numeric records: {numeric}")
print(f"Suppressed records: {suppressed}")
print(f"Other missing records: {other_missing}")

print(
    f"Numeric completeness: "
    f"{numeric / total * 100:.2f}%"
)

print("\nDATA QUALITY BY REPORTING LEVEL")
print("=" * 60)

level_summary = summary.groupby(
    "reporting_level"
)[
    ["total_records",
     "numeric_records",
     "suppressed_records"]
].sum()

print(level_summary.to_string())

print("\nDATASET PREPARATION COMPLETED!")
print(f"Output saved to: {output_file}")
