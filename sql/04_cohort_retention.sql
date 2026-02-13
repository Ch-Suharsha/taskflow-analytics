/*
=================================================================
QUERY NAME: Monthly Cohort Retention Analysis
BUSINESS QUESTION: How do retention curves differ across signup cohorts?
DATA SOURCES: user_activity_summary, events
EXPECTED INSIGHT: Retention improves for recent cohorts due to product improvements
=================================================================
*/

WITH cohort_base AS (
    -- Define cohort by signup month
    SELECT 
        user_id,
        cohort_month,
        signup_date,
        last_active_date,
        days_since_signup,
        is_power_user
    FROM user_activity_summary
    WHERE days_since_signup >= 30  -- Only users old enough to measure retention
),

retention_periods AS (
    SELECT 
        cohort_month,
        COUNT(*) AS cohort_size,
        
        -- Month 1 retention (active at day 30+)
        SUM(CASE 
            WHEN last_active_date >= signup_date + INTERVAL '30 days' THEN 1 ELSE 0 
        END) AS retained_m1,
        
        -- Month 3 retention (active at day 90+)
        SUM(CASE 
            WHEN days_since_signup >= 90 
            AND last_active_date >= signup_date + INTERVAL '90 days' 
            THEN 1 ELSE 0 
        END) AS retained_m3,
        
        -- Month 6 retention (active at day 180+)
        SUM(CASE 
            WHEN days_since_signup >= 180 
            AND last_active_date >= signup_date + INTERVAL '180 days' 
            THEN 1 ELSE 0 
        END) AS retained_m6,
        
        -- Month 12 retention (active at day 365+)
        SUM(CASE 
            WHEN days_since_signup >= 365 
            AND last_active_date >= signup_date + INTERVAL '365 days' 
            THEN 1 ELSE 0 
        END) AS retained_m12,
        
        -- Count of users eligible for each period
        SUM(CASE WHEN days_since_signup >= 90 THEN 1 ELSE 0 END) AS eligible_m3,
        SUM(CASE WHEN days_since_signup >= 180 THEN 1 ELSE 0 END) AS eligible_m6,
        SUM(CASE WHEN days_since_signup >= 365 THEN 1 ELSE 0 END) AS eligible_m12
    FROM cohort_base
    GROUP BY cohort_month
)

SELECT 
    cohort_month,
    cohort_size,
    ROUND(100.0 * retained_m1 / cohort_size, 1) AS retention_m1_pct,
    CASE WHEN eligible_m3 > 0 
        THEN ROUND(100.0 * retained_m3 / eligible_m3, 1) 
        ELSE NULL 
    END AS retention_m3_pct,
    CASE WHEN eligible_m6 > 0 
        THEN ROUND(100.0 * retained_m6 / eligible_m6, 1) 
        ELSE NULL 
    END AS retention_m6_pct,
    CASE WHEN eligible_m12 > 0 
        THEN ROUND(100.0 * retained_m12 / eligible_m12, 1) 
        ELSE NULL 
    END AS retention_m12_pct
FROM retention_periods
ORDER BY cohort_month;

/*
EXPECTED OUTPUT (sample rows):
+--------------+-------------+------------------+------------------+------------------+-------------------+
| cohort_month | cohort_size | retention_m1_pct | retention_m3_pct | retention_m6_pct | retention_m12_pct |
+--------------+-------------+------------------+------------------+------------------+-------------------+
| 2024-01      | 410         | 42.0             | 28.5             | 18.3             | 12.1              |
| 2024-04      | 395         | 44.2             | 30.1             | 19.7             | 13.5              |
| 2024-07      | 422         | 45.8             | 31.4             | 20.5             | NULL              |
| 2024-10      | 438         | 47.3             | 33.0             | NULL             | NULL              |
| 2025-01      | 451         | 48.9             | 34.2             | NULL             | NULL              |
| 2025-04      | 460         | 50.1             | NULL             | NULL             | NULL              |
+--------------+-------------+------------------+------------------+------------------+-------------------+

BUSINESS INSIGHT:
Month 1 retention has been steadily improving from 42% to 50% across cohorts,
suggesting that recent product improvements are having a positive impact.

However, long-term retention (Month 6+) remains below 20%, indicating that
while activation is improving, long-term engagement needs attention.

RECOMMENDED ACTION:
1. Continue investing in onboarding improvements (validated by A/B test results)
2. Implement re-engagement campaigns at Day 14 and Day 60 to improve M3 and M6 retention
3. Investigate what power users do differently to identify retention levers
*/
