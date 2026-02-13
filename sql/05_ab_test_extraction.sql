-- Analysis 2: A/B Test Extraction
-- Extract A/B test data for statistical analysis in Python

SELECT 
    variant,
    COUNT(*) as total_users,
    SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions,
    ROUND(100.0 * SUM(CASE WHEN converted THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
FROM ab_test_assignments
WHERE test_name = 'simplified_onboarding_q4_2025'
GROUP BY variant;
