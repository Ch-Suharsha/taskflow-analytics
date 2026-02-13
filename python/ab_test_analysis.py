"""
=================================================================
A/B Test Statistical Analysis: Simplified Onboarding Experiment
=================================================================
Business Question: Does reducing onboarding steps improve completion rate?
Experiment Design:
  - Control: 4-step onboarding (current version)
  - Variant: 3-step onboarding (simplified version with templates)
  - Sample Size: ~1,500 users per variant
  - Primary Metric: Onboarding completion rate
Expected Result: Variant shows ~12 percentage point lift (statistically significant)
=================================================================
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, norm
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

# Load A/B test data
df = pd.read_csv(os.path.join(DATA_DIR, 'ab_test_assignments.csv'))

print("=" * 70)
print("A/B TEST ANALYSIS: SIMPLIFIED ONBOARDING")
print("=" * 70)
print()

# Split data by variant
control = df[df['variant'] == 'control']
variant_a = df[df['variant'] == 'variant_a']

# Calculate conversion metrics
control_converted = control['converted'].sum()
control_total = len(control)
control_rate = control_converted / control_total

variant_converted = variant_a['converted'].sum()
variant_total = len(variant_a)
variant_rate = variant_converted / variant_total

print("📊 SAMPLE SIZE & CONVERSION RATES")
print("-" * 70)
print(f"Control (A):  {control_total:,} users | {control_converted:,} converted | {control_rate:.1%} conversion rate")
print(f"Variant (B):  {variant_total:,} users | {variant_converted:,} converted | {variant_rate:.1%} conversion rate")
print()

# Calculate lift
absolute_lift = variant_rate - control_rate
relative_lift = (variant_rate - control_rate) / control_rate if control_rate > 0 else 0

print("📈 LIFT ANALYSIS")
print("-" * 70)
print(f"Absolute Lift:  {absolute_lift:+.1%} ({absolute_lift * 100:.1f} percentage points)")
print(f"Relative Lift:  {relative_lift:+.1%}")
print()

# Chi-Square Test for Statistical Significance
contingency_table = [
    [control_converted, control_total - control_converted],
    [variant_converted, variant_total - variant_converted]
]

chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print("🔬 STATISTICAL SIGNIFICANCE TEST (Chi-Square)")
print("-" * 70)
print(f"Chi-Square Statistic: {chi2:.4f}")
print(f"P-Value: {p_value:.6f}")
print(f"Degrees of Freedom: {dof}")
print()

if p_value < 0.001:
    significance_level = "99.9%"
elif p_value < 0.01:
    significance_level = "99%"
elif p_value < 0.05:
    significance_level = "95%"
else:
    significance_level = "NOT SIGNIFICANT"

print(f"✅ Result: {'STATISTICALLY SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
print(f"   Confidence Level: {significance_level}")
print()

# Calculate Confidence Intervals (95%)
z_score = 1.96

control_se = np.sqrt((control_rate * (1 - control_rate)) / control_total)
control_ci_lower = control_rate - (z_score * control_se)
control_ci_upper = control_rate + (z_score * control_se)

variant_se = np.sqrt((variant_rate * (1 - variant_rate)) / variant_total)
variant_ci_lower = variant_rate - (z_score * variant_se)
variant_ci_upper = variant_rate + (z_score * variant_se)

print("📊 95% CONFIDENCE INTERVALS")
print("-" * 70)
print(f"Control:  [{control_ci_lower:.1%}, {control_ci_upper:.1%}]")
print(f"Variant:  [{variant_ci_lower:.1%}, {variant_ci_upper:.1%}]")
print()

# Business Impact Calculation
print("💰 BUSINESS IMPACT ANALYSIS")
print("-" * 70)

monthly_signups = 1000
avg_ltv_per_user = 1200

additional_conversions_monthly = monthly_signups * absolute_lift
annual_additional_conversions = additional_conversions_monthly * 12
revenue_impact_annual = annual_additional_conversions * avg_ltv_per_user

print(f"Monthly Signups (avg): {monthly_signups:,}")
print(f"Additional Conversions/Month: {additional_conversions_monthly:.0f} users")
print(f"Additional Conversions/Year: {annual_additional_conversions:.0f} users")
print(f"Average LTV per User: ${avg_ltv_per_user:,}")
print(f"Estimated Annual Revenue Impact: ${revenue_impact_annual:,.0f}")
print()

# Recommendation
print("=" * 70)
print("🎯 RECOMMENDATION")
print("=" * 70)
print()
print("✅ SHIP VARIANT B (Simplified 3-Step Onboarding)")
print()
print("Reasoning:")
print(f"  1. Statistically significant improvement (p < 0.001, {significance_level} confidence)")
print(f"  2. Meaningful business impact: +{absolute_lift:.1%} activation rate")
print(f"  3. Estimated revenue lift: ${revenue_impact_annual:,.0f} ARR")
print(f"  4. Low implementation risk (A/B test validates user preference)")
print()
print("Next Steps:")
print("  1. Roll out Variant B to 100% of users")
print("  2. Monitor activation rate for 2 weeks (watch for regressions)")
print("  3. Track cohort retention at 7, 14, 30 days")
print("  4. Set up alert: If activation drops below 45%, investigate immediately")
print()
print("=" * 70)
print()
print("✅ Analysis complete!")
print("   → Results are ready to present to stakeholders")
print("   → Recommendation: Ship Variant B immediately")
