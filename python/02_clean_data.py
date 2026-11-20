
from pathlib import Path
import pandas as pd

# Project folders
project_dir = Path(__file__).resolve().parent.parent
raw_file = project_dir / "data" / "raw" / "cihi_ed_wait_times.xlsx"
processed_dir = project_dir / "data" / "processed"
reports_dir = project_dir / "reports"

processed_dir.mkdir(parents=True, exist_ok=True)
reports_dir.mkdir(parents=True, exist_ok=True)

print("ONTARIO HEALTH INTELLIGENCE")
print("DATA CLEANING")
print("=" * 55)

# Step 1: Read worksheet using Excel row 2 as headers
df = pd.read_excel(
    raw_file,
    sheet_name="Table 1",
    header=1,
    dtype=str
)

print(f"\nOriginal records: {len(df)}")

# Step 2: Standardize column names and text values
df.columns = df.columns.astype(str).str.strip()

df = df.dropna(how="all").copy()

for column in df.columns:
    df[column] = df[column].astype("string").str.strip()

# Step 3: Confirm required columns exist
required_columns = [
    "Indicator",
    "Reporting level",
    "Place or organization",
    "Province/Territory",
    "Time frame",
    "90th percentile"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Step 4: Filter Ontario records
ontario = df[
    df["Province/Territory"]
    .str.fullmatch("Ontario", case=False, na=False)
].copy()

print(f"Ontario records: {len(ontario)}")

if ontario.empty:
    raise ValueError("No Ontario records found.")

# Step 5: Convert reported values to numeric
ontario["wait_time_p90"] = pd.to_numeric(
    ontario["90th percentile"]
    .str.replace(",", "", regex=False),
    errors="coerce"
)

# Step 6: Flag usable numeric measurements
ontario["has_numeric_wait_time"] = (
    ontario["wait_time_p90"].notna()
)

# Keep original fields and reporting metadata
# so missing values and coverage can be audited.
all_output = (
    processed_dir / "ontario_ed_all_records.csv"
)

ontario.to_csv(
    all_output,
    index=False,
    encoding="utf-8-sig"
)

# Save numeric observations separately
numeric_data = ontario[
    ontario["has_numeric_wait_time"]
].copy()

numeric_output = (
    processed_dir / "ontario_ed_numeric_records.csv"
)

numeric_data.to_csv(
    numeric_output,
    index=False,
    encoding="utf-8-sig"
)

# Step 7: Generate basic data-quality summary
summary = [
    "ONTARIO HEALTH INTELLIGENCE - CLEANING REPORT",
    "=" * 55,
    f"Original worksheet records: {len(df)}",
    f"Ontario records: {len(ontario)}",
    f"Numeric wait-time records: {len(numeric_data)}",
    f"Missing/non-numeric values: "
    f"{ontario['wait_time_p90'].isna().sum()}",
    "",
    "REPORTING LEVELS",
    ontario["Reporting level"]
    .value_counts(dropna=False).to_string(),
    "",
    "TIME FRAMES",
    ontario["Time frame"]
    .value_counts(dropna=False).to_string(),
    "",
    "SAMPLE ONTARIO RECORD",
    ontario.head(1).to_string(index=False),
    "",
    "Note: Numeric values are not yet validated "
    "for unit, reporting coverage, or comparability."
]

report_file = reports_dir / "cleaning_summary.txt"

report_file.write_text(
    "\n".join(summary),
    encoding="utf-8"
)

print(f"Numeric records: {len(numeric_data)}")
print(f"Missing/non-numeric: "
      f"{ontario['wait_time_p90'].isna().sum()}")

print("\nFiles successfully created:")
print("1. ontario_ed_all_records.csv")
print("2. ontario_ed_numeric_records.csv")
print("3. cleaning_summary.txt")

print("\nData cleaning stage completed!")
