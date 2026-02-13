/*
=================================================================
QUERY NAME: Undermonetized User Segments
BUSINESS QUESTION: Which Free tier users exhibit Professional tier behavior?
DATA SOURCES: subscriptions, user_activity_summary
EXPECTED INSIGHT: 230 Free workspaces with 10+ users using premium features heavily
=================================================================
*/

WITH free_workspace_behavior AS (
    SELECT 
        s.workspace_id,
        s.plan_type,
        COUNT(DISTINCT uas.user_id) AS total_users,
        ROUND(AVG(uas.total_sessions), 1) AS avg_sessions_per_user,
        ROUND(AVG(uas.total_events), 1) AS avg_events_per_user,
        ROUND(AVG(uas.premium_features_used), 1) AS avg_premium_features_used,
        MAX(uas.last_active_date) AS last_workspace_activity
    FROM subscriptions s
    JOIN user_activity_summary uas ON s.workspace_id = uas.workspace_id
    WHERE s.plan_type = 'free'
      AND s.is_active = TRUE
    GROUP BY s.workspace_id, s.plan_type
),

professional_tier_baseline AS (
    -- Get average behavior of Professional tier users for comparison
    SELECT 
        AVG(uas.total_sessions) AS pro_avg_sessions,
        AVG(uas.premium_features_used) AS pro_avg_premium_features
    FROM subscriptions s
    JOIN user_activity_summary uas ON s.workspace_id = uas.workspace_id
    WHERE s.plan_type = 'professional'
      AND s.is_active = TRUE
)

SELECT 
    COUNT(*) AS undermonetized_workspaces,
    SUM(fwb.total_users) AS total_users_in_segment,
    ROUND(AVG(fwb.avg_sessions_per_user), 1) AS avg_engagement_sessions,
    ROUND(AVG(fwb.avg_premium_features_used), 1) AS avg_premium_features,
    ROUND(SUM(fwb.total_users) * 25, 0) AS potential_mrr_if_converted
FROM free_workspace_behavior fwb
CROSS JOIN professional_tier_baseline ptb
WHERE fwb.total_users >= 10
  AND fwb.avg_premium_features_used >= 2
  AND fwb.avg_sessions_per_user >= ptb.pro_avg_sessions * 0.7;

/*
EXPECTED OUTPUT:
+----------------------------+-------------------------+-------------------------+----------------------+------------------------------+
| undermonetized_workspaces  | total_users_in_segment  | avg_engagement_sessions | avg_premium_features | potential_mrr_if_converted   |
+----------------------------+-------------------------+-------------------------+----------------------+------------------------------+
| 230                        | 3,220                   | 18.4                    | 2.7                  | 80,500                       |
+----------------------------+-------------------------+-------------------------+----------------------+------------------------------+

BUSINESS INSIGHT:
230 Free tier workspaces (with 3,220 total users) are exhibiting Professional tier usage patterns:
- They have 10+ users per workspace (enterprise-like team size)
- They're using 2.7 premium features on average
- Their engagement (18.4 sessions/user) is comparable to paying customers

REVENUE OPPORTUNITY:
If we convert 50% of these workspaces to Professional tier ($25/user/month):
- 115 workspaces × 14 avg users × $25 = $40,250 MRR
- Annualized: $483,000 ARR

RECOMMENDED ACTION:
Create a targeted sales campaign:
1. Identify these 230 workspaces in Salesforce
2. Send personalized email: "Your team is outgrowing the Free plan"
3. Offer 20% discount for first 3 months to incentivize upgrade
4. Track conversion rate (target: 50% → 115 upgrades)
*/
