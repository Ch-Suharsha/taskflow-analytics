import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Constants
NUM_USERS = 10000
NUM_WORKSPACES = 2500
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Data directory is sibling to python/ directory (i.e., ../data)
DATA_DIR = os.path.join(SCRIPT_DIR, '../data')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

print("Starting data generation...")

# --- 1. Users & Workspaces ---
print("Generating Users & Workspaces...")
users = []
workspaces = [f"ws_{i}" for i in range(NUM_WORKSPACES)]
workspace_map = {} # ws_id -> {industry, team_size, country}

industries = ['tech', 'marketing', 'finance', 'healthcare', 'education', 'retail']
countries = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia']

# Generate Workspace attributes
for ws in workspaces:
    workspace_map[ws] = {
        'industry': np.random.choice(industries, p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05]),
        'team_size': np.random.randint(1, 50),
        'country': np.random.choice(countries, p=[0.5, 0.1, 0.1, 0.1, 0.1, 0.1])
    }

account_tiers = ['free', 'starter', 'professional', 'enterprise']
tier_probs = [0.60, 0.25, 0.12, 0.03]

roles = ['owner', 'admin', 'member', 'guest']
signup_sources = ['organic', 'paid_search', 'referral', 'sales']

for i in range(NUM_USERS):
    user_id = f"u_{i}"
    workspace_id = np.random.choice(workspaces)
    ws_info = workspace_map[workspace_id]
    
    signup_date = START_DATE + timedelta(days=np.random.randint(0, (END_DATE - START_DATE).days))
    
    # Logic: Higher tiers for larger teams
    if ws_info['team_size'] > 20:
        tier = np.random.choice(account_tiers, p=[0.1, 0.2, 0.4, 0.3])
    else:
        tier = np.random.choice(account_tiers, p=tier_probs)

    # Churn logic
    months_since_signup = (END_DATE - signup_date).days / 30
    if tier == 'free':
        churn_prob = 0.15 * months_since_signup
    else:
        churn_prob = 0.03 * months_since_signup
    
    is_active = np.random.rand() > min(churn_prob, 0.9) # Cap churn at 90%
    last_login = END_DATE if is_active else signup_date + timedelta(days=np.random.randint(1, 90))

    users.append({
        'user_id': user_id,
        'workspace_id': workspace_id,
        'email': fake.email(),
        'signup_date': signup_date,
        'account_tier': tier,
        'user_role': np.random.choice(roles),
        'industry': ws_info['industry'],
        'team_size': ws_info['team_size'],
        'signup_source': np.random.choice(signup_sources),
        'country': ws_info['country'],
        'is_active': is_active,
        'last_login_date': last_login
    })

df_users = pd.DataFrame(users)
df_users.to_csv(f'{DATA_DIR}/taskflow_users.csv', index=False)
print(f"Saved {len(df_users)} users.")

# --- 2. Onboarding Funnel & A/B Test ---
print("Generating Onboarding Funnel & A/B Test...")
onboarding = []
ab_assignments = []

# A/B Test Config
TEST_NAME = "simplified_onboarding_q4_2025"
TEST_START = datetime(2025, 10, 1)

for _, user in df_users.iterrows():
    # A/B Test Assignment
    if user['signup_date'] >= TEST_START:
        variant = np.random.choice(['control', 'variant_a'])
        ab_assignments.append({
            'user_id': user['user_id'],
            'test_name': TEST_NAME,
            'variant': variant,
            'assignment_date': user['signup_date'],
            'converted': False, # Update later
            'conversion_date': None
        })
    else:
        variant = 'control' # Historical baseline

    # Funnel Completion Rates
    # Base rates
    s1_rate = 0.85
    s2_rate = 0.82
    s3_rate = 0.64
    s4_rate = 0.78 # Of those who complete s3
    
    # Variant A lift
    if variant == 'variant_a':
        # Simulate lift: better completion at step 3 (simulating 3-step flow via better UX)
        s3_rate = 0.80 
    
    # Execution
    step_1 = np.random.rand() < s1_rate
    step_2 = step_1 and (np.random.rand() < s2_rate)
    step_3 = step_2 and (np.random.rand() < s3_rate)
    step_4 = step_3 and (np.random.rand() < s4_rate)
    
    complete = step_4
    
    # Update A/B conversion
    if user['signup_date'] >= TEST_START:
        ab_assignments[-1]['converted'] = complete
        if complete:
            ab_assignments[-1]['conversion_date'] = user['signup_date'] + timedelta(minutes=np.random.randint(10, 120))

    base_time = user['signup_date']
    
    onboarding.append({
        'user_id': user['user_id'],
        'step_1_completed': step_1,
        'step_1_timestamp': base_time + timedelta(minutes=2) if step_1 else None,
        'step_2_completed': step_2,
        'step_2_timestamp': base_time + timedelta(minutes=5) if step_2 else None,
        'step_3_completed': step_3,
        'step_3_timestamp': base_time + timedelta(minutes=15) if step_3 else None,
        'step_4_completed': step_4,
        'step_4_timestamp': base_time + timedelta(minutes=30) if step_4 else None,
        'onboarding_completed': complete,
        'onboarding_completion_date': base_time + timedelta(minutes=30) if complete else None,
        'time_to_complete_hours': np.random.uniform(0.5, 48) if complete else None,
        'ab_test_variant': variant if user['signup_date'] >= TEST_START else None
    })

df_onboarding = pd.DataFrame(onboarding)
df_onboarding.to_csv(f'{DATA_DIR}/taskflow_onboarding_funnel.csv', index=False)

df_ab = pd.DataFrame(ab_assignments)
df_ab.to_csv(f'{DATA_DIR}/taskflow_ab_test.csv', index=False)
print(f"Saved onboarding data and {len(df_ab)} A/B test assignments.")

# --- 3. Feature Usage ---
print("Generating Feature Usage...")
features = ['kanban_boards', 'time_tracking', 'automation_rules', 'custom_fields', 
            'reporting_dashboard', 'integrations_slack', 'integrations_google_drive']

# Adoption rates (Base probabilities)
feature_probs = {
    'kanban_boards': 0.90,
    'time_tracking': 0.12, # Low adoption
    'automation_rules': 0.08,
    'custom_fields': 0.15,
    'reporting_dashboard': 0.65, # High adoption for Enterprise
    'integrations_slack': 0.40,
    'integrations_google_drive': 0.50
}

usage_records = []
feature_id_counter = 0

for _, user in df_users.iterrows():
    if not user['is_active']: continue
    
    # Adjust probs based on tier
    tier_mult = 1.0
    if user['account_tier'] == 'enterprise': tier_mult = 2.0
    if user['account_tier'] == 'free': tier_mult = 0.5
    
    for feat in features:
        prob = feature_probs[feat] * tier_mult
        
        # Enterprise features shouldn't be used by free users (mostly)
        if feat == 'reporting_dashboard' and user['account_tier'] == 'free':
            prob = 0.01
            
        if np.random.rand() < prob:
            # User adopted this feature
            first_used = user['signup_date'] + timedelta(days=np.random.randint(0, 30))
            if first_used > END_DATE: continue
            
            # High usage count for 'time_tracking' adopters (retention correlation)
            if feat == 'time_tracking':
                usage_count = np.random.randint(50, 500)
            else:
                usage_count = np.random.randint(5, 100)
                
            usage_records.append({
                'usage_id': f"fu_{feature_id_counter}",
                'user_id': user['user_id'],
                'feature_name': feat,
                'first_used_date': first_used,
                'total_usage_count': usage_count,
                'last_used_date': END_DATE - timedelta(days=np.random.randint(0, 7)),
                'days_since_signup_at_first_use': (first_used - user['signup_date']).days
            })
            feature_id_counter += 1

df_features = pd.DataFrame(usage_records)
df_features.to_csv(f'{DATA_DIR}/taskflow_feature_usage.csv', index=False)
print(f"Saved {len(df_features)} feature usage records.")

# --- 4. Subscriptions ---
print("Generating Subscriptions...")
subscriptions = []
sub_id_counter = 0

# Group users by workspace to determine subscription
ws_users = df_users.groupby('workspace_id')

for ws_id, group in ws_users:
    # Assume workspace tier matches the majority of users (simplification)
    tier = group['account_tier'].mode()[0]
    
    mrr_map = {'free': 0, 'starter': 10, 'professional': 25, 'enterprise': 50} # Enterprise avg
    mrr = mrr_map[tier] * len(group)
    
    start_date = group['signup_date'].min()
    is_active = group['is_active'].any()
    
    churn_date = None
    churn_reason = None
    if not is_active:
        churn_date = group['last_login_date'].max()
        churn_reason = np.random.choice(['price', 'feature_gap', 'competitor', 'other'], 
                                      p=[0.3, 0.2, 0.2, 0.3])
    
    subscriptions.append({
        'subscription_id': f"sub_{sub_id_counter}",
        'workspace_id': ws_id,
        'plan_type': tier,
        'mrr': mrr,
        'start_date': start_date,
        'end_date': None if is_active else churn_date,
        'is_active': is_active,
        'churn_date': churn_date,
        'churn_reason': churn_reason
    })
    sub_id_counter += 1

df_subs = pd.DataFrame(subscriptions)
df_subs.to_csv(f'{DATA_DIR}/taskflow_subscriptions.csv', index=False)
print(f"Saved {len(df_subs)} subscriptions.")

print("Data generation complete!")
