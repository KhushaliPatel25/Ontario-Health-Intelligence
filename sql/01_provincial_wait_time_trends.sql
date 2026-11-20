
-- ONTARIO HEALTH INTELLIGENCE
-- Analysis 01: Provincial Emergency Department Trends
--
-- Metric: 90th percentile ED length of stay
-- Population: Admitted emergency department patients
-- Unit: Hours
-- Reporting level: Province/territory

WITH provincial_trends AS (
    SELECT
        fiscal_year,
        fiscal_start_year,
        place_or_organization AS province,
        p90_hours,

        LAG(p90_hours) OVER (
            ORDER BY fiscal_start_year
        ) AS previous_year_hours

    FROM ed_province_numeric

    WHERE province = 'Ontario'
)

SELECT
    fiscal_year,
    province,

    ROUND(p90_hours, 1)
        AS p90_wait_hours,

    ROUND(previous_year_hours, 1)
        AS previous_year_hours,

    ROUND(
        p90_hours - previous_year_hours,
        1
    ) AS yoy_change_hours,

    ROUND(
        100.0 * (
            p90_hours - previous_year_hours
        ) / NULLIF(previous_year_hours, 0),
        2
    ) AS yoy_change_percent

FROM provincial_trends

ORDER BY fiscal_start_year;
