-- Analysis 1.1: Power Feature Paradox
-- Find features with low adoption but high retention impact

WITH user_retention AS (
    SELECT 
        u.user_id,
        u.signup_date,
        u.last_login_date,
        CASE WHEN u.last_login_date > u.signup_date + INTERVAL '30 days' THEN 1 ELSE 0 END as retained_30_days
    FROM users u
),
feature_adoption AS (
    SELECT 
        f.feature_name,
        COUNT(DISTINCT f.user_id) as adopters
    FROM feature_usage f
    GROUP BY 1
),
total_users AS (
    SELECT COUNT(*) as total FROM users
),
retention_by_feature AS (
    SELECT 
        f.feature_name,
        AVG(ur.retained_30_days) as retention_rate_adopters
    FROM feature_usage f
    JOIN user_retention ur ON f.user_id = ur.user_id
    GROUP BY 1
),
overall_retention AS (
    SELECT AVG(retained_30_days) as avg_retention FROM user_retention
)

SELECT 
    f.feature_name,
    ROUND(100.0 * fa.adopters / t.total, 2) || '%' as adoption_rate,
    ROUND(100.0 * rf.retention_rate_adopters, 2) || '%' as adopters_retention,
    ROUND(100.0 * o.avg_retention, 2) || '%' as avg_overall_retention,
    ROUND(rf.retention_rate_adopters / o.avg_retention, 2) as retention_lift
FROM feature_adoption fa
JOIN retention_by_feature rf ON fa.feature_name = rf.feature_name
CROSS JOIN total_users t
CROSS JOIN overall_retention o
ORDER BY retention_lift DESC;
