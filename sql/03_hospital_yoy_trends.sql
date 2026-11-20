
-- ONTARIO HEALTH INTELLIGENCE
-- Analysis 03: Hospital Year-over-Year Trends
--
-- Metric: 90th percentile ED length of stay
-- Population: Admitted emergency department patients
-- Unit: Hours
--
-- Only compare consecutive fiscal years.
-- Do not use suppressed measurements.
-- Exclude duplicate facility-year identities.

WITH facility_records AS (

    SELECT
        place_or_organization AS hospital,
        corporation,
        hospital_peer_group,
        fiscal_year,
        fiscal_start_year,
        p90_hours,

        COUNT(*) OVER (
            PARTITION BY
                place_or_organization,
                corporation,
                fiscal_start_year
        ) AS records_per_facility_year

    FROM ed_wait_times

    WHERE reporting_level = 'Facility'
),

unique_facility_records AS (

    SELECT *
    FROM facility_records

    WHERE records_per_facility_year = 1
),

yearly_comparison AS (

    SELECT
        hospital,
        corporation,
        hospital_peer_group,
        fiscal_year,
        fiscal_start_year,
        p90_hours,

        LAG(p90_hours) OVER (
            PARTITION BY hospital, corporation
            ORDER BY fiscal_start_year
        ) AS previous_p90_hours,

        LAG(fiscal_start_year) OVER (
            PARTITION BY hospital, corporation
            ORDER BY fiscal_start_year
        ) AS previous_start_year

    FROM unique_facility_records
)

SELECT
    hospital,
    corporation,
    hospital_peer_group,
    fiscal_year,

    ROUND(previous_p90_hours, 1)
        AS previous_p90_hours,

    ROUND(p90_hours, 1)
        AS current_p90_hours,

    ROUND(
        p90_hours - previous_p90_hours,
        1
    ) AS change_hours,

    ROUND(
        100.0 * (
            p90_hours - previous_p90_hours
        ) / NULLIF(previous_p90_hours, 0),
        2
    ) AS change_percent,

    CASE
        WHEN p90_hours < previous_p90_hours
            THEN 'Decreased'
        WHEN p90_hours > previous_p90_hours
            THEN 'Increased'
        ELSE 'Unchanged'
    END AS trend_direction

FROM yearly_comparison

WHERE p90_hours IS NOT NULL
  AND previous_p90_hours IS NOT NULL
  AND previous_p90_hours > 0
  AND fiscal_start_year = previous_start_year + 1

ORDER BY
    fiscal_start_year DESC,
    change_hours DESC,
    hospital;
