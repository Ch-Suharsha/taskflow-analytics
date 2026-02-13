import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = pd.read_csv('../data/taskflow_ab_test.csv')

# Filter for the specific test
test_data = df[df['test_name'] == 'simplified_onboarding_q4_2025']

# Group by variant
results = test_data.groupby('variant').agg({
    'user_id': 'count',
    'converted': 'sum'
}).rename(columns={'user_id': 'total_users', 'converted': 'conversions'})

results['conversion_rate'] = results['conversions'] / results['total_users']

print("\n--- A/B Test Results ---")
print(results)

# Statistical Significance (Chi-Square)
# We need an array like [[conv_A, no_conv_A], [conv_B, no_conv_B]]
control = results.loc['control']
variant = results.loc['variant_a']

contingency = [
    [control['conversions'], control['total_users'] - control['conversions']],
    [variant['conversions'], variant['total_users'] - variant['conversions']]
]

chi2, p_value, _, _ = stats.chi2_contingency(contingency)

print(f"\nP-value: {p_value:.5f}")
is_sig = p_value < 0.05
print(f"Statistically Significant? {'YES' if is_sig else 'NO'} (at alpha=0.05)")

# Confidence Intervals (Simple approx)
# SE = sqrt( p(1-p) / n )
for v_name in ['control', 'variant_a']:
    r = results.loc[v_name]
    p = r['conversion_rate']
    n = r['total_users']
    se = np.sqrt(p * (1 - p) / n)
    ci = 1.96 * se
    print(f"\n{v_name} CI (95%): {p:.2%} ± {ci:.2%}")

# Lift
lift = (variant['conversion_rate'] - control['conversion_rate']) / control['conversion_rate']
print(f"\nRelative Lift: {lift:.2%}")
