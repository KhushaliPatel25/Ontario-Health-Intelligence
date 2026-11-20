# Ontario Health Intelligence

## Executive Summary

Analysis of Ontario emergency department length of stay for admitted patients, using the reported 90th percentile measured in hours.

The analysis covers five fiscal years from 2021–2022 through 2025–2026.

## 1. Provincial Performance

- First reported P90: 32.5 hours.
- Latest reported P90: 38.3 hours.
- Overall change: +5.8 hours (+17.85%).
- Latest year-over-year change: -13.74%.
- Mean of annual P90 measurements: 40.78 hours.
- Median annual P90: 43.70 hours.
- Sample standard deviation: 5.34 hours.

These statistics describe annual reported percentiles, not individual patient observations.

## 2. Hospital Year-over-Year Trends

Fiscal year: 2025–2026

- Valid facility comparisons: 159.
- Decreased P90: 108.
- Increased P90: 51.
- Unchanged P90: 0.
- Percentage with decreased P90: 67.92%.

Comparisons use consecutive fiscal years and exclude suppressed numeric measurements.

## 3. Regional Comparison

Fiscal year: 2025–2026

- Regions included: 6.
- Lowest reported regional P90: North West Region (Ont.) (28.1 hours).
- Highest reported regional P90: Central Region (Ont.) (48.0 hours).

Regional comparisons describe the selected indicator and do not establish overall healthcare quality.

## 4. Data Quality

- Total Ontario reporting records: 1,204.
- Numeric records: 1,163.
- Suppressed records: 41.
- Numeric completeness: 96.59%.

Suppressed observations were not imputed as zero.

## 5. Exploratory Forecasting Scenarios

Two simple baseline methods were explored using five annual observations.

- Previous-year baseline: 38.30 hours for 2026–2027.
- Two-year moving average: 41.35 hours for 2026–2027.

These are illustrative scenarios, not reliable predictions or official forecasts.

## 6. Analytical Limitations

- The dataset contains reporting observations, not patient-level records.
- P90 values must not be interpreted as average waits.
- Reporting levels must not be combined or summed.
- Numeric completeness is not equivalent to complete Ontario hospital coverage.
- Facility identities and coverage may vary over time.
- Only five annual observations inform the scenarios.
- No causal conclusions are supported.

## 7. Tools and Methods

- Python: ingestion, cleaning, validation, descriptive statistics and baseline forecasting.
- SQL (SQLite): reporting-level analysis, window functions and year-over-year comparisons.
- Power BI: interactive performance dashboards.
- Matplotlib: historical and exploratory visualization.

## 8. Data Provenance

Source: Canadian Institute for Health Information (CIHI), emergency department total time spent for admitted patients data table.

The original downloaded workbook is retained in the data/raw folder.

All reported results are subject to the original data source's reporting and methodology limitations.