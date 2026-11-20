
from pathlib import Path
import pandas as pd

# Project locations
project_dir = Path(__file__).resolve().parent.parent

input_file = (
    project_dir / "data" / "processed"
    / "provincial_wait_time_trends.csv"
)

processed_dir = project_dir / "data" / "processed"
reports_dir = project_dir / "reports"

print("ONTARIO HEALTH INTELLIGENCE")
print("EXPLORATORY FORECASTING ANALYSIS")
print("=" * 60)

# Step 1: Load provincial historical data
df = pd.read_csv(input_file)

df["fiscal_start_year"] = pd.to_numeric(
    df["fiscal_year"].astype(str).str.extract(
        r"(\d{4})"
    )[0],
    errors="coerce"
)

df["p90_wait_hours"] = pd.to_numeric(
    df["p90_wait_hours"],
    errors="coerce"
)

df = df.sort_values(
    "fiscal_start_year"
).reset_index(drop=True)

# Step 2: Validate historical observations
if len(df) != 5:
    raise ValueError("Expected five fiscal-year observations.")

if df[["fiscal_start_year", "p90_wait_hours"]].isna().any().any():
    raise ValueError("Historical values are missing.")

if df["fiscal_start_year"].duplicated().any():
    raise ValueError("Duplicate fiscal years found.")

if not df["fiscal_start_year"].diff().iloc[1:].eq(1).all():
    raise ValueError("Fiscal years are not consecutive.")

print("\nHISTORICAL ONTARIO P90 HOURS")
print(
    df[["fiscal_year", "p90_wait_hours"]]
    .to_string(index=False)
)

# Step 3: Create historical forecast comparisons
backtest = df[
    ["fiscal_year", "p90_wait_hours"]
].copy()

backtest = backtest.rename(columns={
    "p90_wait_hours": "actual_p90_hours"
})

# Baseline 1: predict the previous year's value
backtest["previous_year_prediction"] = (
    df["p90_wait_hours"].shift(1)
)

# Baseline 2: average the previous two years
backtest["two_year_average_prediction"] = (
    df["p90_wait_hours"]
    .shift(1)
    .rolling(2)
    .mean()
)

# Absolute prediction errors
backtest["previous_year_abs_error"] = (
    backtest["actual_p90_hours"]
    - backtest["previous_year_prediction"]
).abs()

backtest["two_year_abs_error"] = (
    backtest["actual_p90_hours"]
    - backtest["two_year_average_prediction"]
).abs()

# Step 4: Compare models on identical years
common_years = backtest.dropna(
    subset=[
        "previous_year_prediction",
        "two_year_average_prediction"
    ]
)

naive_mae = (
    common_years["previous_year_abs_error"].mean()
)

average_mae = (
    common_years["two_year_abs_error"].mean()
)

print("\nFORECAST BACKTEST RESULTS")
print("=" * 60)
print(backtest.to_string(index=False))

print("\nMODEL COMPARISON")
print(f"Common evaluation years: {len(common_years)}")
print(f"Previous-year MAE: {naive_mae:.2f} hours")
print(f"Two-year average MAE: {average_mae:.2f} hours")

# Step 5: Create illustrative next-year scenarios
last_year = int(df["fiscal_start_year"].iloc[-1])

next_fiscal_year = (
    f"{last_year + 1}–{last_year + 2}"
)

latest_value = float(
    df["p90_wait_hours"].iloc[-1]
)

recent_average = float(
    df["p90_wait_hours"].tail(2).mean()
)

scenarios = pd.DataFrame({
    "fiscal_year": [
        next_fiscal_year,
        next_fiscal_year
    ],
    "method": [
        "Previous-year baseline",
        "Two-year moving average"
    ],
    "projected_p90_hours": [
        round(latest_value, 2),
        round(recent_average, 2)
    ],
    "projection_type": [
        "Exploratory scenario",
        "Exploratory scenario"
    ]
})

# Step 6: Save results
backtest_file = (
    processed_dir / "forecast_baseline_backtest.csv"
)

scenario_file = (
    processed_dir / "forecast_scenarios.csv"
)

report_file = (
    reports_dir / "forecast_methodology.txt"
)

backtest.to_csv(
    backtest_file,
    index=False,
    encoding="utf-8-sig"
)

scenarios.to_csv(
    scenario_file,
    index=False,
    encoding="utf-8-sig"
)

report_lines = [
    "ONTARIO HEALTH INTELLIGENCE",
    "EXPLORATORY FORECASTING METHODOLOGY",
    "=" * 60,
    "",
    "Metric: Provincial ED length of stay,",
    "90th percentile, admitted patients, hours",
    "",
    f"Historical observations: {len(df)}",
    f"Common backtest years: {len(common_years)}",
    f"Previous-year MAE: {naive_mae:.2f} hours",
    f"Two-year average MAE: {average_mae:.2f} hours",
    "",
    "EXPLORATORY NEXT-YEAR SCENARIOS",
    scenarios.to_string(index=False),
    "",
    "LIMITATIONS",
    "- Only five annual observations are available.",
    "- Three years are used in the common backtest.",
    "- Results do not establish reliable predictive accuracy.",
    "- Scenarios are not official CIHI forecasts.",
    "- No confidence intervals are estimated.",
    "- Changes in hospital operations or reporting",
    "  practices are not modeled."
]

report_file.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print("\nEXPLORATORY SCENARIOS")
print("=" * 60)
print(scenarios.to_string(index=False))

print("\nForecast baseline analysis completed!")
print("Created forecast_baseline_backtest.csv")
print("Created forecast_scenarios.csv")
print("Created forecast_methodology.txt")
