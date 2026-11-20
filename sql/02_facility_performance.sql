
-- ONTARIO HEALTH INTELLIGENCE
-- Analysis 02: Facility Reporting Overview
--
-- Metric: 90th percentile ED length of stay
-- Unit: Hours
-- Reporting level: Facility
-- Goal: Examine coverage and variation by peer group

SELECT
    fiscal_year,
    hospital_peer_group,

    COUNT(*) AS facility_records,

    SUM(
        CASE
            WHEN p90_hours IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS numeric_records,

    SUM(
        CASE
            WHEN p90_hours IS NULL THEN 1
            ELSE 0
        END
    ) AS suppressed_records,

    ROUND(
        MIN(p90_hours), 1
    ) AS lowest_reported_p90_hours,

    ROUND(
        MAX(p90_hours), 1
    ) AS highest_reported_p90_hours

FROM ed_wait_times

WHERE reporting_level = 'Facility'

GROUP BY
    fiscal_year,
    hospital_peer_group

ORDER BY
    fiscal_year,
    hospital_peer_group;
