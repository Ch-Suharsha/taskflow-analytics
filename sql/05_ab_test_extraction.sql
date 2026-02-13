/*
=================================================================
QUERY NAME: A/B Test Data Extraction
BUSINESS QUESTION: Extract clean data for statistical analysis of the onboarding experiment
DATA SOURCES: ab_test_assignments, onboarding_funnel, user_activity_summary
EXPECTED INSIGHT: Data preparation for Chi-Square test in Python
=================================================================
*/

-- Main extraction: join A/B test assignments with onboarding and activity data
WITH test_data AS (
    SELECT 
        ab.user_id,
        ab.test_name,
        ab.variant,
        ab.assignment_date,
        ab.converted,
        ab.conversion_date,
        
        -- Onboarding details
        ob.step_1_completed,
        ob.step_2_completed,
        ob.step_3_completed,
        ob.step_4_completed,
        ob.time_to_complete_hours,
        
        -- User context
        u.account_tier,
        u.signup_source,
        u.industry,
        u.team_size,
        
        -- Post-onboarding engagement
        uas.total_sessions,
        uas.total_events,
        uas.is_power_user,
        uas.is_at_risk_churn
    FROM ab_test_assignments ab
    JOIN onboarding_funnel ob ON ab.user_id = ob.user_id
    JOIN users u ON ab.user_id = u.user_id
    JOIN user_activity_summary uas ON ab.user_id = uas.user_id
    WHERE ab.test_name = 'simplified_onboarding_q4_2025'
)

-- Summary by variant
SELECT 
    variant,
    COUNT(*) AS total_users,
    SUM(CASE WHEN converted THEN 1 ELSE 0 END) AS conversions,
    ROUND(100.0 * SUM(CASE WHEN converted THEN 1 ELSE 0 END) / COUNT(*), 1) AS conversion_rate,
    ROUND(AVG(CASE WHEN converted THEN time_to_complete_hours END), 1) AS avg_time_to_complete_hrs,
    
    -- Post-onboarding engagement (guardrail metrics)
    ROUND(AVG(total_sessions), 1) AS avg_sessions_post_onboarding,
    ROUND(AVG(total_events), 1) AS avg_events_post_onboarding,
    ROUND(100.0 * SUM(CASE WHEN is_at_risk_churn THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_at_risk
FROM test_data
GROUP BY variant
ORDER BY variant;

/*
EXPECTED OUTPUT:
+-----------+-------------+-------------+-----------------+--------------------------+-----------------------------+----------------------------+-------------+
| variant   | total_users | conversions | conversion_rate | avg_time_to_complete_hrs | avg_sessions_post_onboarding| avg_events_post_onboarding | pct_at_risk |
+-----------+-------------+-------------+-----------------+--------------------------+-----------------------------+----------------------------+-------------+
| control   | 1,523       | 533         | 35.0            | 8.2                      | 28.4                        | 312.5                      | 42.1        |
| variant_a | 1,522       | 715         | 47.0            | 5.1                      | 31.2                        | 345.8                      | 38.3        |
+-----------+-------------+-------------+-----------------+--------------------------+-----------------------------+----------------------------+-------------+

GUARDRAIL CHECK:
The variant group shows HIGHER post-onboarding engagement (31.2 vs 28.4 sessions)
and LOWER churn risk (38.3% vs 42.1%), confirming that the simplified onboarding
doesn't just improve completion - it also leads to better long-term engagement.

This data is exported to Python for Chi-Square significance testing.
See: python/ab_test_analysis.py
*/
