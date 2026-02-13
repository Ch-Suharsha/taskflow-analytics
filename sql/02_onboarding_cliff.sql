/*
=================================================================
QUERY NAME: Onboarding Funnel Drop-off Analysis
BUSINESS QUESTION: Where are users abandoning the onboarding process?
DATA SOURCES: onboarding_funnel
EXPECTED INSIGHT: 36% drop-off at Step 3 (Create First Board)
=================================================================
*/

WITH funnel_metrics AS (
    -- Step 1: Team Setup
    SELECT 
        1 AS step_number,
        'Step 1: Team Setup' AS step_name,
        COUNT(*) AS users_reached,
        SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END) AS users_completed,
        ROUND(100.0 * SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_rate,
        ROUND(100.0 * (1 - SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END)::FLOAT / COUNT(*)), 1) AS drop_off_rate
    FROM onboarding_funnel
    
    UNION ALL
    
    -- Step 2: Invite Team Members
    SELECT 
        2,
        'Step 2: Invite Members',
        SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
    
    UNION ALL
    
    -- Step 3: Create First Board (THE PROBLEM STEP)
    SELECT 
        3,
        'Step 3: Create Board',
        SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
    
    UNION ALL
    
    -- Step 4: Create First Task
    SELECT 
        4,
        'Step 4: Create Task',
        SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
)
SELECT 
    step_number,
    step_name,
    users_reached,
    users_completed,
    completion_rate,
    drop_off_rate,
    CASE 
        WHEN drop_off_rate > 30 THEN '🚨 HIGH DROP-OFF'
        WHEN drop_off_rate > 20 THEN '⚠️ MODERATE DROP-OFF'
        ELSE '✅ NORMAL'
    END AS alert_status
FROM funnel_metrics
ORDER BY step_number;

/*
EXPECTED OUTPUT:
+-------------+---------------------+---------------+-----------------+-----------------+--------------+-------------------+
| step_number | step_name           | users_reached | users_completed | completion_rate | drop_off_rate| alert_status      |
+-------------+---------------------+---------------+-----------------+-----------------+--------------+-------------------+
| 1           | Step 1: Team Setup  | 10,000        | 8,500           | 85.0            | 15.0         | ✅ NORMAL         |
| 2           | Step 2: Invite      | 8,500         | 7,000           | 82.4            | 17.6         | ✅ NORMAL         |
| 3           | Step 3: Create Board| 7,000         | 4,480           | 64.0            | 36.0         | 🚨 HIGH DROP-OFF  |
| 4           | Step 4: Create Task | 4,480         | 3,494           | 78.0            | 22.0         | ⚠️ MODERATE       |
+-------------+---------------------+---------------+-----------------+-----------------+--------------+-------------------+

BUSINESS INSIGHT:
Step 3 has a 36% drop-off rate - 2x higher than other steps.
This step requires users to make a decision about board structure, which creates friction.

HYPOTHESIS:
Users get overwhelmed by the blank canvas problem: "What should my board look like?"

RECOMMENDED ACTION:
Provide pre-built board templates (e.g., "Marketing Campaign", "Sprint Planning", "Sales Pipeline")
to reduce cognitive load and decision paralysis.

This hypothesis was validated through A/B testing (see ab_test_assignments.csv).
*/
