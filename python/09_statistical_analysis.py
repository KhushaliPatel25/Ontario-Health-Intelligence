
from pathlib import Path
import pandas as pd

# ============================================================
# ONTARIO HEALTH INTELLIGENCE
# Statistical Analysis of Provincial ED P90 Measurements
# ============================================================

project_dir = Path(__file__).resolve().parent.parent

input_file = (
    project_dir / "data" / "processed"
    / "provincial_wait_time_trends.csv"
)

reports_dir = project_dir / "reports"
processed_dir = project_dir / "data" / "processed"

reports_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

print("ONTARIO HEALTH INTELLIGENCE")
print("PROVINCIAL STATISTICAL ANALYSIS")
print("=" * 60)

# Step 1: Load historical observations
df = pd.read_csv(input_file)

required_columns = [
    "fiscal_year",
    "p90_wait_hours"
]

if not all(col in df.columns for col in required_columns):
    raise ValueError("Required columns are missing.")

df["p90_wait_hours"] = pd.to_numeric(
    df["p90_wait_hours"],
    errors="raise"
)

df["fiscal_start_year"] = pd.to_numeric(
    df["fiscal_year"].astype(str).str.extract(
        r"(\d{4})"
    )[0],
    errors="raise"
)

df = df.sort_values(
    "fiscal_start_year"
).reset_index(drop=True)

if len(df) != 5:
    raise ValueError("Expected five annual observations.")

if df["fiscal_start_year"].duplicated().any():
    raise ValueError("Duplicate fiscal years found.")

if df["p90_wait_hours"].isna().any():
    raise ValueError("Missing P90 values found.")

if not df["fiscal_start_year"].diff().iloc[1:].eq(1).all():
    raise ValueError("Fiscal years must be consecutive.")

# Step 2: Descriptive statistics
values = df["p90_wait_hours"]

statistics = {
    "Observations": len(values),
    "Minimum P90 hours": values.min(),
    "Maximum P90 hours": values.max(),
    "Median annual P90 hours": values.median(),
    "Mean of annual P90 values": values.mean(),
    "Sample standard deviation": values.std(ddof=1),
    "Range in hours": values.max() - values.min()
}

# Step 3: Historical changes
df["change_hours"] = values.diff()

df["change_percent"] = (
    values.pct_change(fill_method=None) * 100
).round(2)

# Step 4: Overall change
first_value = float(values.iloc[0])
latest_value = float(values.iloc[-1])

overall_change = latest_value - first_value

overall_percent = (
    overall_change / first_value * 100
)

# Step 5: Identify largest annual changes
valid_changes = df.dropna(
    subset=["change_hours"]
)

largest_increase = valid_changes.loc[
    valid_changes["change_hours"].idxmax()
]

largest_decrease = valid_changes.loc[
    valid_changes["change_hours"].idxmin()
]

# Step 6: Display statistics
print("\nDESCRIPTIVE STATISTICS")
print("=" * 60)

for name, value in statistics.items():
    if name == "Observations":
        print(f"{name}: {value}")
    else:
        print(f"{name}: {value:.2f}")

print("\nYEAR-OVER-YEAR ANALYSIS")
print("=" * 60)

print(
    df[
        [
            "fiscal_year",
            "p90_wait_hours",
            "change_hours",
            "change_percent"
        ]
    ].to_string(index=False)
)

print("\nOVERALL HISTORICAL CHANGE")
print("=" * 60)

print(f"First reported P90: {first_value:.2f} hours")
print(f"Latest reported P90: {latest_value:.2f} hours")
print(f"Overall change: {overall_change:+.2f} hours")
print(f"Overall percentage change: {overall_percent:+.2f}%")

print(
    f"Largest annual increase: "
    f"{largest_increase['change_hours']:+.2f} hours "
    f"({largest_increase['fiscal_year']})"
)

print(
    f"Largest annual decrease: "
    f"{largest_decrease['change_hours']:+.2f} hours "
    f"({largest_decrease['fiscal_year']})"
)

# Step 7: Save the statistical report
report_lines = [
    "ONTARIO HEALTH INTELLIGENCE",
    "PROVINCIAL STATISTICAL ANALYSIS",
    "=" * 60,
    "",
    "METRIC",
    "90th percentile ED length of stay",
    "for admitted patients, measured in hours.",
    "",
    "DESCRIPTIVE STATISTICS"
]

for name, value in statistics.items():
    if name == "Observations":
        report_lines.append(f"{name}: {value}")
    else:
        report_lines.append(f"{name}: {value:.2f}")

report_lines.extend([
    "",
    "HISTORICAL YEAR-OVER-YEAR RESULTS",
    df[
        [
            "fiscal_year",
            "p90_wait_hours",
            "change_hours",
            "change_percent"
        ]
    ].to_string(index=False),
    "",
    "OVERALL CHANGE",
    f"First P90: {first_value:.2f} hours",
    f"Latest P90: {latest_value:.2f} hours",
    f"Change: {overall_change:+.2f} hours",
    f"Percentage change: {overall_percent:+.2f}%",
    "",
    "LARGEST ANNUAL CHANGES",
    f"Largest increase: "
    f"{largest_increase['change_hours']:+.2f} hours "
    f"({largest_increase['fiscal_year']})",
    f"Largest decrease: "
    f"{largest_decrease['change_hours']:+.2f} hours "
    f"({largest_decrease['fiscal_year']})",
    "",
    "ANALYTICAL LIMITATIONS",
    "- Only five annual P90 observations are available.",
    "- The mean describes annual P90 values,",
    "  not average patient length of stay.",
    "- Standard deviation describes variation",
    "  across annual reported P90 measurements.",
    "- No statistical significance is claimed.",
    "- The results do not establish causation.",
    "- Reporting and coverage limitations remain."
])

report_file = (
    reports_dir / "statistical_summary.txt"
)

report_file.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

# Step 8: Export detailed annual changes
output_file = (
    processed_dir / "provincial_statistical_changes.csv"
)

df[
    [
        "fiscal_year",
        "p90_wait_hours",
        "change_hours",
        "change_percent"
    ]
].to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nStatistical analysis completed successfully!")
print(f"Report saved to: {report_file}")
print(f"CSV saved to: {output_file}")
