# 📊 SQL Showcase — Featured Queries with Explanations

This document highlights the SQL analysis queries used in this project, with explanations of the techniques and business reasoning behind each.

---

## Query 1: Power Feature Paradox (`01_power_feature_paradox.sql`)

**Technique:** Multi-CTE pattern with CROSS JOIN for baseline comparison

This query identifies features with low adoption but high retention impact. It uses two CTEs:
1. `feature_retention` — calculates 30-day retention for users who adopted each feature
2. `baseline_retention` — calculates baseline retention for non-adopters

The key insight is Time Tracking: only 12% adoption but 3.9x retention lift.

**SQL Skills Demonstrated:** CTEs, CASE expressions, aggregate functions, CROSS JOIN, conditional filtering

---

## Query 2: Onboarding Cliff (`02_onboarding_cliff.sql`)

**Technique:** UNION ALL for step-by-step funnel construction

This query reconstructs the onboarding funnel from boolean completion columns. Each UNION ALL block represents one funnel step, calculating:
- Users reached (from previous step)
- Users completed
- Completion rate
- Drop-off rate with alert status classification

**SQL Skills Demonstrated:** UNION ALL, NULLIF for division safety, CASE for categorical alerts

---

## Query 3: Undermonetized Segments (`03_undermonetized_segments.sql`)

**Technique:** Behavioral segmentation with cross-tier comparison

Identifies Free tier workspaces exhibiting Professional tier usage patterns. Uses a professional tier baseline CTE to dynamically set the comparison threshold (70% of Pro engagement).

**SQL Skills Demonstrated:** Multi-table JOINs, aggregate filtering with HAVING-like WHERE, CROSS JOIN for dynamic thresholds

---

## Query 4: Cohort Retention (`04_cohort_retention.sql`)

**Technique:** Multi-period cohort retention with eligibility windows

Calculates retention at Month 1, 3, 6, and 12 for each signup cohort. Handles the eligibility problem (newer cohorts can't have 12-month retention) by tracking eligible user counts per period.

**SQL Skills Demonstrated:** Window-based cohort analysis, INTERVAL arithmetic, conditional NULLs, multi-period retention curves

---

## Query 5: A/B Test Extraction (`05_ab_test_extraction.sql`)

**Technique:** Multi-table JOIN for experiment data enrichment

Joins 4 tables to create a comprehensive A/B test dataset with:
- Assignment data
- Onboarding step completion details
- User demographic context
- Post-onboarding engagement (guardrail metrics)

**SQL Skills Demonstrated:** 4-table JOIN, guardrail metric calculation, experiment data preparation
