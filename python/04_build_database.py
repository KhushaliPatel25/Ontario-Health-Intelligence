
from pathlib import Path
import sqlite3
import pandas as pd

# Project paths
project_dir = Path(__file__).resolve().parent.parent

csv_file = (
    project_dir / "data" / "processed"
    / "ontario_ed_all_records.csv"
)

db_file = (
    project_dir / "data" / "processed"
    / "ontario_health.db"
)

print("ONTARIO HEALTH INTELLIGENCE")
print("BUILDING SQL DATABASE")
print("=" * 55)

# Load the cleaned Ontario records
df = pd.read_csv(
    csv_file,
    dtype=str,
    keep_default_na=False
)

# Standardize SQL column names
column_mapping = {
    "Indicator": "indicator",
    "Reporting level": "reporting_level",
    "Place or organization": "place_or_organization",
    "Hospital Peer Group": "hospital_peer_group",
    "Corporation": "corporation",
    "Region": "region",
    "Province/Territory": "province",
    "Urban or rural/remote": "urban_rural",
    "Trend note": "trend_note",
    "Time Scale": "time_scale",
    "Time frame": "fiscal_year",
    "90th percentile": "p90_original",
    "90th percentile: Performance trend": "performance_trend",
    "90th percentile: Performance comparison": "performance_comparison",
    "90th percentile: Data coverage": "data_coverage"
}

missing = [
    col for col in column_mapping
    if col not in df.columns
]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df[list(column_mapping)].rename(
    columns=column_mapping
)

# Create numeric measurement
# Suppressed observations remain missing.
df["p90_hours"] = pd.to_numeric(
    df["p90_original"].str.replace(
        ",", "", regex=False
    ),
    errors="coerce"
)

# Preserve original suppression information
df["value_status"] = df["p90_original"].where(
    df["p90_hours"].isna(),
    "Numeric"
)

# Extract starting year for easier sorting
df["fiscal_start_year"] = pd.to_numeric(
    df["fiscal_year"].str.extract(
        r"(\d{4})"
    )[0],
    errors="coerce"
).astype("Int64")

# Create SQL database
with sqlite3.connect(db_file) as conn:

    df.to_sql(
        "ed_wait_times",
        conn,
        if_exists="replace",
        index=False
    )

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_level_year
        ON ed_wait_times (
            reporting_level,
            fiscal_year
        )
    """)

    # Facility results for hospital comparisons
    conn.execute("""
        CREATE VIEW IF NOT EXISTS ed_facility_numeric AS
        SELECT *
        FROM ed_wait_times
        WHERE reporting_level = 'Facility'
          AND p90_hours IS NOT NULL
    """)

    # Province-level results for Ontario trends
    conn.execute("""
        CREATE VIEW IF NOT EXISTS ed_province_numeric AS
        SELECT *
        FROM ed_wait_times
        WHERE reporting_level = 'Province/territory'
          AND p90_hours IS NOT NULL
    """)

    # Verify database records
    total_records = conn.execute("""
        SELECT COUNT(*) FROM ed_wait_times
    """).fetchone()[0]

    facility_records = conn.execute("""
        SELECT COUNT(*) FROM ed_facility_numeric
    """).fetchone()[0]

    province_records = conn.execute("""
        SELECT COUNT(*) FROM ed_province_numeric
    """).fetchone()[0]

print(f"Total database records: {total_records}")
print(f"Numeric facility records: {facility_records}")
print(f"Numeric province records: {province_records}")

if (
    total_records != 1204
    or facility_records != 798
    or province_records != 5
):
    raise ValueError(
        "Database counts do not match the quality audit."
    )

print("\nSQL database created successfully!")
print(f"Database location: {db_file}")
