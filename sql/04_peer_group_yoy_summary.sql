
-- ONTARIO HEALTH INTELLIGENCE
-- Analysis 04: Peer Group Year-over-Year Summary
--
-- Metric: 90th percentile ED length of stay
-- Unit: Hours
-- Compare consecutive years for the same facility
-- Do not include suppressed measurements

WITH facility_records AS (

    SELECT
        place_or_organization,
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

unique_facilities AS (

    SELECT *
    FROM facility_records
    WHERE records_per_facility_year = 1
),

matched_years AS (

    SELECT
        current.fiscal_year,
        current.fiscal_start_year,
        current.hospital_peer_group,
        current.p90_hours AS current_hours,
        previous.p90_hours AS previous_hours

    FROM unique_facilities AS current

    INNER JOIN unique_facilities AS previous
        ON current.place_or_organization =
           previous.place_or_organization

       AND current.corporation =
           previous.corporation

       AND previous.fiscal_start_year =
           current.fiscal_start_year - 1

    WHERE current.p90_hours IS NOT NULL
      AND previous.p90_hours IS NOT NULL
      AND previous.p90_hours > 0
)

SELECT
    fiscal_year,
    hospital_peer_group,

    COUNT(*) AS valid_comparisons,

    SUM(
        CASE WHEN current_hours < previous_hours
        THEN 1 ELSE 0 END
    ) AS decreased_count,

    SUM(
        CASE WHEN current_hours > previous_hours
        THEN 1 ELSE 0 END
    ) AS increased_count,

    SUM(
        CASE WHEN current_hours = previous_hours
        THEN 1 ELSE 0 END
    ) AS unchanged_count,

    ROUND(
        100.0 * SUM(
            CASE WHEN current_hours < previous_hours
            THEN 1 ELSE 0 END
        ) / COUNT(*),
        1
    ) AS percent_decreased,

    ROUND(
        AVG(current_hours - previous_hours),
        2
    ) AS mean_change_hours

FROM matched_years

GROUP BY
    fiscal_year,
    fiscal_start_year,
    hospital_peer_group

ORDER BY
    fiscal_start_year,
    hospital_peer_group;
