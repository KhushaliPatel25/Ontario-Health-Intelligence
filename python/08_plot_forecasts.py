
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# ONTARIO HEALTH INTELLIGENCE
# Historical P90 and Exploratory Forecast Visualization
# ============================================================

# Step 1: Define project paths
project_dir = Path(__file__).resolve().parent.parent

historical_file = (
    project_dir / "data" / "processed"
    / "provincial_wait_time_trends.csv"
)

scenario_file = (
    project_dir / "data" / "processed"
    / "forecast_scenarios.csv"
)

output_file = (
    project_dir / "reports"
    / "forecast_visualization.png"
)

print("ONTARIO HEALTH INTELLIGENCE")
print("FORECAST VISUALIZATION")
print("=" * 60)

# ============================================================
# Step 2: Load historical Ontario data
# ============================================================

historical = pd.read_csv(historical_file)

historical["start_year"] = (
    historical["fiscal_year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

historical = historical.sort_values(
    "start_year"
).reset_index(drop=True)

# ============================================================
# Step 3: Load exploratory forecasting scenarios
# ============================================================

scenarios = pd.read_csv(scenario_file)

if len(historical) != 5 or len(scenarios) != 2:
    raise ValueError(
        "Unexpected number of historical or scenario rows."
    )

historical_values = historical[
    "p90_wait_hours"
].astype(float)

scenarios["projected_p90_hours"] = pd.to_numeric(
    scenarios["projected_p90_hours"],
    errors="raise"
)

if scenarios["fiscal_year"].nunique() != 1:
    raise ValueError(
        "Scenarios have different fiscal years."
    )

# ============================================================
# Step 4: Prepare chart positions
# ============================================================

years = historical["fiscal_year"].tolist()

forecast_year = scenarios["fiscal_year"].iloc[0]

x_actual = list(range(len(years)))
x_future = len(years)

# ============================================================
# Step 5: Create chart
# ============================================================

fig, ax = plt.subplots(figsize=(12, 6))

# Plot historical observations
ax.plot(
    x_actual,
    historical_values,
    marker="o",
    linewidth=2.5,
    markersize=7,
    label="Historical P90 (Observed)"
)

# Add historical data labels
for x, value in zip(x_actual, historical_values):
    ax.annotate(
        f"{value:.1f}",
        (x, value),
        textcoords="offset points",
        xytext=(0, 9),
        ha="center",
        fontsize=9
    )

# ============================================================
# Step 6: Plot exploratory scenarios
# ============================================================

last_value = float(
    historical_values.iloc[-1]
)

for _, scenario in scenarios.iterrows():

    projected = float(
        scenario["projected_p90_hours"]
    )

    method = scenario["method"]

    ax.plot(
        [x_actual[-1], x_future],
        [last_value, projected],
        linestyle="--",
        marker="D",
        linewidth=2,
        label=f"Exploratory: {method}"
    )

    ax.annotate(
        f"{projected:.2f}",
        (x_future, projected),
        textcoords="offset points",
        xytext=(8, 0),
        ha="left",
        fontsize=9
    )

# ============================================================
# Step 7: Separate observed data from future scenarios
# ============================================================

ax.axvline(
    x=len(years) - 0.5,
    linestyle=":",
    alpha=0.6
)

# ============================================================
# Step 8: Format chart
# ============================================================

ax.set_title(
    "Ontario ED Length of Stay: "
    "Historical P90 and Exploratory Scenarios",
    fontsize=14,
    fontweight="bold",
    pad=18
)

ax.set_xlabel(
    "Fiscal Year",
    fontsize=11
)

ax.set_ylabel(
    "90th Percentile (Hours)",
    fontsize=11
)

ax.set_xticks(
    x_actual + [x_future]
)

ax.set_xticklabels(
    years + [forecast_year]
)

ax.set_xlim(
    -0.3,
    x_future + 0.8
)

max_value = max(
    historical_values.max(),
    scenarios["projected_p90_hours"].max()
)

ax.set_ylim(
    0,
    max_value * 1.25
)

ax.grid(
    axis="y",
    alpha=0.25
)

# ============================================================
# Step 9: Legend placement - UPDATED
# ============================================================

# Position the legend in the upper-right corner.
# This avoids overlapping the historical 45.0 label.

ax.legend(
    loc="upper right",
    fontsize=9
)

# ============================================================
# Step 10: Add forecasting limitations
# ============================================================

ax.text(
    0.5,
    -0.20,
    "Dashed lines are exploratory scenarios, "
    "not official forecasts. "
    "Historical sample: five annual observations.",
    transform=ax.transAxes,
    ha="center",
    fontsize=9
)

plt.tight_layout()

plt.subplots_adjust(
    bottom=0.22
)

# ============================================================
# Step 11: Save visualization
# ============================================================

output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

print("\nForecast visualization created successfully!")
print(f"Saved to: {output_file}")

# ============================================================
# Step 12: Display visualization
# ============================================================

if "agg" not in plt.get_backend().lower():
    plt.show()
