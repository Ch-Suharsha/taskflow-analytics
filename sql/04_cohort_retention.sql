-- Analysis 3: Monthly Cohort Retention
-- Calculate retention for Month 0, 1, 3, 6, 12

WITH cohort_users AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', signup_date) as cohort_month
    FROM users
),
user_activities AS (
    -- Assuming we interpret 'last_login_date' as a proxy for activity for this synthetic set
    -- In a real scenario, we'd join with the events table.
    -- For this generated data, we simply check if they are still active or when they churned.
    SELECT 
        u.user_id,
        u.signup_date,
        u.last_login_date,
        u.is_active
    FROM users u
),
retention_calc AS (
    SELECT 
        c.cohort_month,
        COUNT(DISTINCT c.user_id) as cohort_size,
        COUNT(DISTINCT CASE WHEN ua.last_login_date >= c.cohort_month + INTERVAL '1 month' THEN c.user_id END) as month_1,
        COUNT(DISTINCT CASE WHEN ua.last_login_date >= c.cohort_month + INTERVAL '3 months' THEN c.user_id END) as month_3,
        COUNT(DISTINCT CASE WHEN ua.last_login_date >= c.cohort_month + INTERVAL '6 months' THEN c.user_id END) as month_6,
        COUNT(DISTINCT CASE WHEN ua.last_login_date >= c.cohort_month + INTERVAL '12 months' THEN c.user_id END) as month_12
    FROM cohort_users c
    JOIN user_activities ua ON c.user_id = ua.user_id
    GROUP BY 1
)

SELECT 
    TO_CHAR(cohort_month, 'YYYY-MM') as month,
    cohort_size,
    ROUND(100.0 * month_1 / cohort_size, 1) || '%' as m1_ret,
    ROUND(100.0 * month_3 / cohort_size, 1) || '%' as m3_ret,
    ROUND(100.0 * month_6 / cohort_size, 1) || '%' as m6_ret,
    ROUND(100.0 * month_12 / cohort_size, 1) || '%' as m12_ret
FROM retention_calc
ORDER BY cohort_month DESC;
