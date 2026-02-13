-- Analysis 1.2: Onboarding Cliff Analysis
-- Analyze drop-off at each onboarding step

SELECT 
    'Step 1: Team Setup' as step_name,
    COUNT(CASE WHEN step_1_completed THEN 1 END) as users_completed,
    ROUND(100.0 * COUNT(CASE WHEN step_1_completed THEN 1 END) / COUNT(*), 2) as completion_rate,
    100.0 - ROUND(100.0 * COUNT(CASE WHEN step_1_completed THEN 1 END) / COUNT(*), 2) as drop_off_rate
FROM onboarding_funnel

UNION ALL

SELECT 
    'Step 2: Invite Members' as step_name,
    COUNT(CASE WHEN step_2_completed THEN 1 END) as users_completed,
    ROUND(100.0 * COUNT(CASE WHEN step_2_completed THEN 1 END) / COUNT(*), 2) as completion_rate,
    ROUND(100.0 * (COUNT(CASE WHEN step_1_completed THEN 1 END) - COUNT(CASE WHEN step_2_completed THEN 1 END)) / COUNT(CASE WHEN step_1_completed THEN 1 END), 2) as drop_off_rate
FROM onboarding_funnel

UNION ALL

SELECT 
    'Step 3: Create Board' as step_name,
    COUNT(CASE WHEN step_3_completed THEN 1 END) as users_completed,
    ROUND(100.0 * COUNT(CASE WHEN step_3_completed THEN 1 END) / COUNT(*), 2) as completion_rate,
    ROUND(100.0 * (COUNT(CASE WHEN step_2_completed THEN 1 END) - COUNT(CASE WHEN step_3_completed THEN 1 END)) / COUNT(CASE WHEN step_2_completed THEN 1 END), 2) as drop_off_result
FROM onboarding_funnel

UNION ALL

SELECT 
    'Step 4: Create Task' as step_name,
    COUNT(CASE WHEN step_4_completed THEN 1 END) as users_completed,
    ROUND(100.0 * COUNT(CASE WHEN step_4_completed THEN 1 END) / COUNT(*), 2) as completion_rate,
    ROUND(100.0 * (COUNT(CASE WHEN step_3_completed THEN 1 END) - COUNT(CASE WHEN step_4_completed THEN 1 END)) / COUNT(CASE WHEN step_3_completed THEN 1 END), 2) as drop_off_rate
FROM onboarding_funnel;
