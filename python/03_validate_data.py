
from pathlib import Path
import pandas as pd

# Project locations
project_dir = Path(__file__).resolve().parent.parent

input_file = (
    project_dir / "data" / "processed"
    / "ontario_ed_all_records.csv"
)

report_file = (
    project_dir / "reports"
    / "data_quality_audit.txt"
)

print("ONTARIO HEALTH INTELLIGENCE")
print("DATA QUALITY VALIDATION")
print("=" * 55)

# Load the processed Ontario dataset
df = pd.read_csv(input_file, dtype=str)

for column in df.columns:
    df[column] = df[column].astype("string").str.strip()

df["wait_time_p90"] = pd.to_numeric(
    df["wait_time_p90"],
    errors="coerce"
)

# Basic data quality checks
total = len(df)
valid = df["wait_time_p90"].notna().sum()
missing = df["wait_time_p90"].isna().sum()
negative = (df["wait_time_p90"] < 0).sum()
zero = (df["wait_time_p90"] == 0).sum()
over_100 = (df["wait_time_p90"] > 100).sum()

# Reporting-level summary
level_summary = df.groupby(
    "Reporting level",
    dropna=False
).agg(
    total_records=("wait_time_p90", "size"),
    numeric_records=("wait_time_p90", "count")
)

# Year-by-year summary
year_summary = df.groupby(
    "Time frame",
    dropna=False
).agg(
    total_records=("wait_time_p90", "size"),
    numeric_records=("wait_time_p90", "count")
).sort_index()

# Identify codes in non-numeric observations
missing_codes = df.loc[
    df["wait_time_p90"].isna(),
    "90th percentile"
].value_counts(dropna=False)

# Check data coverage notes
coverage_summary = df[
    "90th percentile: Data coverage"
].value_counts(dropna=False)

# Review numeric facility records separately
facilities = df[
    df["Reporting level"].str.lower() == "facility"
].copy()

facility_numeric = facilities[
    facilities["wait_time_p90"].notna()
]

# Build report
lines = [
    "ONTARIO HEALTH INTELLIGENCE",
    "DATA QUALITY AUDIT",
    "=" * 55,
    "",
    f"Total Ontario records: {total}",
    f"Valid numeric records: {valid}",
    f"Missing/non-numeric: {missing}",
    f"Negative wait-time values: {negative}",
    f"Zero wait-time values: {zero}",
    f"Values above 100 hours: {over_100}",
    "",
    "REPORTING LEVEL VALIDATION",
    "=" * 55,
    level_summary.to_string(),
    "",
    "FISCAL YEAR VALIDATION",
    "=" * 55,
    year_summary.to_string(),
    "",
    "MISSING VALUE CODES",
    "=" * 55,
    missing_codes.to_string(),
    "",
    "DATA COVERAGE LABELS",
    "=" * 55,
    coverage_summary.to_string(),
    "",
    "FACILITY-LEVEL RECORDS",
    "=" * 55,
    f"Total facility records: {len(facilities)}",
    f"Numeric facility records: {len(facility_numeric)}",
    "",
    "NOTES",
    "- Indicator unit: hours",
    "- Metric: 90th percentile, not average",
    "- No missing values have been imputed",
    "- High values require review, not automatic deletion",
    "- Different reporting levels must not be combined",
    "- Coverage labels require careful interpretation"
]

report_file.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print(f"Total Ontario records: {total}")
print(f"Valid numeric records: {valid}")
print(f"Missing/non-numeric records: {missing}")
print(f"Negative values: {negative}")
print(f"Values above 100 hours: {over_100}")
print(f"Numeric facility records: {len(facility_numeric)}")

print("\nData quality validation completed!")
print(f"Report saved to: {report_file}")
