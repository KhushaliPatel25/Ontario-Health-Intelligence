
from pathlib import Path
import pandas as pd

# ============================================================
# ONTARIO HEALTH INTELLIGENCE
# Final Analytics Insights Report
# ============================================================

project_dir = Path(__file__).resolve().parent.parent
data_dir = project_dir / "data" / "processed"
reports_dir = project_dir / "reports"

output_file = reports_dir / "final_insights.md"

print("ONTARIO HEALTH INTELLIGENCE")
print("GENERATING FINAL INSIGHTS REPORT")
print("=" * 60)

# Step 1: Load verified analytics datasets
files = {
    "provincial": "provincial_wait_time_trends.csv",
    "hospital": "hospital_yoy_trends.csv",
    "regional": "regional_wait_time_trends.csv",
    "quality": "data_quality_by_level_year.csv",
    "scenarios": "forecast_scenarios.csv"
}

data = {}

for name, filename in files.items():
    path = data_dir / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required dataset missing: {filename}"
        )

    data[name] = pd.read_csv(path)
    print(f"Loaded: {filename}")

provincial = data["provincial"].copy()
hospital = data["hospital"].copy()
regional = data["regional"].copy()
quality = data["quality"].copy()
scenarios = data["scenarios"].copy()

# Step 2: Provincial analysis
provincial["start_year"] = (
    provincial["fiscal_year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

provincial = provincial.sort_values("start_year")

if len(provincial) != 5:
    raise ValueError("Expected five provincial observations.")

first = provincial.iloc[0]
latest = provincial.iloc[-1]

latest_year = latest["fiscal_year"]

first_p90 = float(first["p90_wait_hours"])
latest_p90 = float(latest["p90_wait_hours"])

overall_change = latest_p90 - first_p90
overall_percent = overall_change / first_p90 * 100

mean_p90 = provincial["p90_wait_hours"].mean()
median_p90 = provincial["p90_wait_hours"].median()
std_p90 = provincial["p90_wait_hours"].std(ddof=1)

latest_yoy = float(latest["yoy_change_percent"])

# Step 3: Hospital-level analysis
latest_hospitals = hospital[
    hospital["fiscal_year"] == latest_year
]

total_comparisons = len(latest_hospitals)

decreased = int(
    (latest_hospitals["trend_direction"] == "Decreased").sum()
)

increased = int(
    (latest_hospitals["trend_direction"] == "Increased").sum()
)

unchanged = int(
    (latest_hospitals["trend_direction"] == "Unchanged").sum()
)

if total_comparisons == 0:
    raise ValueError("No latest-year hospital comparisons.")

decreased_percent = decreased / total_comparisons * 100

# Step 4: Regional analysis
latest_regions = regional[
    regional["fiscal_year"] == latest_year
].sort_values("p90_wait_hours")

if latest_regions.empty:
    raise ValueError("No latest-year regional data found.")

lowest_region = latest_regions.iloc[0]
highest_region = latest_regions.iloc[-1]

# Step 5: Data quality analysis
total_records = int(quality["total_records"].sum())
numeric_records = int(quality["numeric_records"].sum())
suppressed_records = int(
    quality["suppressed_records"].sum()
)

completeness = numeric_records / total_records * 100

if (total_records, numeric_records, suppressed_records) != (
    1204, 1163, 41
):
    raise ValueError("Data quality totals do not match audit.")

# Step 6: Build final report
lines = [
    "# Ontario Health Intelligence",
    "",
    "## Executive Summary",
    "",
    "Analysis of Ontario emergency department length of stay "
    "for admitted patients, using the reported 90th percentile "
    "measured in hours.",
    "",
    "The analysis covers five fiscal years from "
    "2021–2022 through 2025–2026.",
    "",
    "## 1. Provincial Performance",
    "",
    f"- First reported P90: {first_p90:.1f} hours.",
    f"- Latest reported P90: {latest_p90:.1f} hours.",
    f"- Overall change: {overall_change:+.1f} hours "
    f"({overall_percent:+.2f}%).",
    f"- Latest year-over-year change: {latest_yoy:+.2f}%.",
    f"- Mean of annual P90 measurements: {mean_p90:.2f} hours.",
    f"- Median annual P90: {median_p90:.2f} hours.",
    f"- Sample standard deviation: {std_p90:.2f} hours.",
    "",
    "These statistics describe annual reported percentiles, "
    "not individual patient observations.",
    "",
    "## 2. Hospital Year-over-Year Trends",
    "",
    f"Fiscal year: {latest_year}",
    "",
    f"- Valid facility comparisons: {total_comparisons}.",
    f"- Decreased P90: {decreased}.",
    f"- Increased P90: {increased}.",
    f"- Unchanged P90: {unchanged}.",
    f"- Percentage with decreased P90: "
    f"{decreased_percent:.2f}%.",
    "",
    "Comparisons use consecutive fiscal years and exclude "
    "suppressed numeric measurements.",
    "",
    "## 3. Regional Comparison",
    "",
    f"Fiscal year: {latest_year}",
    "",
    f"- Regions included: {len(latest_regions)}.",
    f"- Lowest reported regional P90: "
    f"{lowest_region['health_region']} "
    f"({lowest_region['p90_wait_hours']:.1f} hours).",
    f"- Highest reported regional P90: "
    f"{highest_region['health_region']} "
    f"({highest_region['p90_wait_hours']:.1f} hours).",
    "",
    "Regional comparisons describe the selected indicator "
    "and do not establish overall healthcare quality.",
    "",
    "## 4. Data Quality",
    "",
    f"- Total Ontario reporting records: {total_records:,}.",
    f"- Numeric records: {numeric_records:,}.",
    f"- Suppressed records: {suppressed_records}.",
    f"- Numeric completeness: {completeness:.2f}%.",
    "",
    "Suppressed observations were not imputed as zero.",
    "",
    "## 5. Exploratory Forecasting Scenarios",
    "",
    "Two simple baseline methods were explored using "
    "five annual observations.",
    ""
]

for _, row in scenarios.iterrows():
    lines.append(
        f"- {row['method']}: "
        f"{row['projected_p90_hours']:.2f} hours "
        f"for {row['fiscal_year']}."
    )

lines.extend([
    "",
    "These are illustrative scenarios, not reliable "
    "predictions or official forecasts.",
    "",
    "## 6. Analytical Limitations",
    "",
    "- The dataset contains reporting observations, "
    "not patient-level records.",
    "- P90 values must not be interpreted as average waits.",
    "- Reporting levels must not be combined or summed.",
    "- Numeric completeness is not equivalent to "
    "complete Ontario hospital coverage.",
    "- Facility identities and coverage may vary over time.",
    "- Only five annual observations inform the scenarios.",
    "- No causal conclusions are supported.",
    "",
    "## 7. Tools and Methods",
    "",
    "- Python: ingestion, cleaning, validation, "
    "descriptive statistics and baseline forecasting.",
    "- SQL (SQLite): reporting-level analysis, "
    "window functions and year-over-year comparisons.",
    "- Power BI: interactive performance dashboards.",
    "- Matplotlib: historical and exploratory visualization.",
    "",
    "## 8. Data Provenance",
    "",
    "Source: Canadian Institute for Health Information "
    "(CIHI), emergency department total time spent "
    "for admitted patients data table.",
    "",
    "The original downloaded workbook is retained "
    "in the data/raw folder.",
    "",
    "All reported results are subject to the original "
    "data source's reporting and methodology limitations."
])

# Step 7: Save the report
reports_dir.mkdir(parents=True, exist_ok=True)

output_file.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("\nFINAL REPORT SUMMARY")
print("=" * 60)
print(f"Latest provincial P90: {latest_p90:.1f} hours")
print(f"Hospital YoY comparisons: {total_comparisons}")
print(f"Regions: {len(latest_regions)}")
print(f"Numeric completeness: {completeness:.2f}%")

print("\nFinal insights report created successfully!")
print(f"Saved to: {output_file}")
