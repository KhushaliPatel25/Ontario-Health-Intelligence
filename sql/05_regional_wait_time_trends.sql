
-- ONTARIO HEALTH INTELLIGENCE
-- Analysis 05: Regional ED Wait-Time Trends
--
-- Metric: 90th percentile ED length of stay
-- Population: Admitted emergency department patients
-- Unit: Hours
-- Reporting level: Health region

WITH regional_data AS (

    SELECT
        place_or_organization AS health_region,
        fiscal_year,
        fiscal_start_year,
        p90_hours,

        LAG(p90_hours) OVER (
            PARTITION BY place_or_organization
            ORDER BY fiscal_start_year
        ) AS previous_p90_hours,

        LAG(fiscal_start_year) OVER (
            PARTITION BY place_or_organization
            ORDER BY fiscal_start_year
        ) AS previous_start_year

    FROM ed_wait_times

    WHERE reporting_level = 'Health region'
      AND province = 'Ontario'
),

regional_comparison AS (

    SELECT
        health_region,
        fiscal_year,
        fiscal_start_year,
        p90_hours,
        previous_p90_hours,

        CASE
            WHEN fiscal_start_year =
                 previous_start_year + 1
             AND p90_hours IS NOT NULL
             AND previous_p90_hours IS NOT NULL
            THEN p90_hours - previous_p90_hours
            ELSE NULL
        END AS yoy_change_hours

    FROM regional_data
)

SELECT
    health_region,
    fiscal_year,

    ROUND(p90_hours, 1)
        AS p90_wait_hours,

    ROUND(previous_p90_hours, 1)
        AS previous_year_hours,

    ROUND(yoy_change_hours, 1)
        AS yoy_change_hours,

    ROUND(
        100.0 * yoy_change_hours
        / NULLIF(previous_p90_hours, 0),
        2
    ) AS yoy_change_percent,

    RANK() OVER (
        PARTITION BY fiscal_start_year
        ORDER BY p90_hours ASC
    ) AS regional_p90_rank

FROM regional_comparison

ORDER BY
    fiscal_start_year,
    regional_p90_rank;
