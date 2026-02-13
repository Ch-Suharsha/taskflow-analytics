-- Analysis 1.3: Undermonetized Segments
-- Find Free tier users behaving like Professional tier users (e.g. large teams)

SELECT 
    u.workspace_id,
    u.industry,
    u.team_size,
    COUNT(DISTINCT u.user_id) as active_users,
    MAX(u.last_login_date) as last_active,
    u.country
FROM users u
WHERE u.account_tier = 'free'
  AND u.is_active = TRUE
GROUP BY 1, 2, 3, 6
HAVING COUNT(DISTINCT u.user_id) >= 5 -- More than 5 users is typical for paid
   AND MAX(u.last_login_date) > CURRENT_DATE - INTERVAL '14 days'
ORDER BY active_users DESC
LIMIT 100;
