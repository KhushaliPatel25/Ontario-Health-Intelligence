"""Execute the five reviewed SQLite analyses and export their results."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "processed" / "ontario_health.db"
OUTPUT = ROOT / "data" / "processed"

ANALYSES = [
    ("01_provincial_wait_time_trends.sql", "provincial_wait_time_trends.csv"),
    ("02_facility_performance.sql", "facility_performance_by_peer_group.csv"),
    ("03_hospital_yoy_trends.sql", "hospital_yoy_trends.csv"),
    ("04_peer_group_yoy_summary.sql", "peer_group_yoy_summary.csv"),
    ("05_regional_wait_time_trends.sql", "regional_wait_time_trends.csv"),
]

print("ONTARIO HEALTH INTELLIGENCE | SQL ANALYSES")
results_by_file = {}
with sqlite3.connect(DB) as db:
    for query_file, csv_name in ANALYSES:
        sql = (ROOT / "sql" / query_file).read_text(encoding="utf-8")
        result = pd.read_sql_query(sql, db)
        if result.empty:
            raise ValueError(f"{query_file} returned no rows")
        result.to_csv(OUTPUT / csv_name, index=False, encoding="utf-8-sig")
        results_by_file[csv_name] = result
        print(f"{csv_name}: {len(result)} rows")

provincial = results_by_file["provincial_wait_time_trends.csv"]
regional = results_by_file["regional_wait_time_trends.csv"]
facility = results_by_file["facility_performance_by_peer_group.csv"]
hospital = results_by_file["hospital_yoy_trends.csv"]
peer = results_by_file["peer_group_yoy_summary.csv"]

assert len(provincial) == 5, "Provincial time-series row count changed"
assert len(regional) == 30, "Regional row count changed"
assert facility["facility_records"].sum() == 839, "Facility count changed"
assert facility["numeric_records"].sum() == 798, "Numeric facility count changed"
assert facility["suppressed_records"].sum() == 41, "Suppressed count changed"
assert len(hospital) == 636, "Matched facility comparisons changed"
assert peer["valid_comparisons"].sum() == len(hospital), "Peer group total mismatch"
assert peer["increased_count"].sum() == (hospital["trend_direction"] == "Increased").sum()
assert peer["decreased_count"].sum() == (hospital["trend_direction"] == "Decreased").sum()
assert peer["unchanged_count"].sum() == (hospital["trend_direction"] == "Unchanged").sum()
print("All five SQL analyses passed record-count reconciliation.")
