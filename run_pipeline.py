"""Run the complete reviewed analysis pipeline via VS Code's Run Python File button.

Requirements: pip packages listed in requirements.txt; source workbook can be
downloaded automatically if it is not already present in data/raw/.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "data" / "raw" / "cihi_ed_wait_times.xlsx"

PIPELINE = [
    "02_clean_data.py", "03_validate_data.py", "04_build_database.py",
    "05_run_sql_analyses.py", "06_prepare_data_quality.py",
    "07_forecast_baselines.py", "08_plot_forecasts.py",
    "09_statistical_analysis.py", "10_generate_insights.py",
]

try:
    import pandas, openpyxl, matplotlib  # noqa: F401
except ImportError as exc:
    raise SystemExit(
        f"Missing Python package: {exc}. Install packages from requirements.txt "
        "in the active VS Code interpreter, then run this file again."
    ) from exc

# Do not open a GUI plot window when orchestrating the whole pipeline.
env = dict(os.environ)
env["MPLBACKEND"] = "Agg"

if not RAW_FILE.exists():
    print("Raw workbook not found; downloading from CIHI.", flush=True)
    subprocess.run(
        [sys.executable, str(ROOT / "python" / "01_download_data.py")],
        cwd=ROOT, env=env, check=True
    )

for filename in PIPELINE:
    print(f"\n>>> Running {filename}", flush=True)
    subprocess.run(
        [sys.executable, str(ROOT / "python" / filename)],
        cwd=ROOT, env=env, check=True
    )

print("\nPIPELINE COMPLETE: validated CSVs, SQLite database, figure and reports regenerated.")
