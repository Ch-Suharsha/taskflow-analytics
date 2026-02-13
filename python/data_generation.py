"""
=================================================================
TaskFlow Analytics - Realistic Synthetic Data Generator
=================================================================
This script generates 7 CSV files with realistic SaaS user behavior patterns.
Key realistic patterns included:
1. Churn varies by tier (15% free, 3% paid)
2. Power user distribution (80/20 rule)
3. Feature discovery friction (low adoption of hidden features)
4. Onboarding funnel with realistic drop-offs
5. A/B test with statistically significant results
=================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 70)
print("TASKFLOW ANALYTICS - DATA GENERATION")
print("=" * 70)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_USERS = 10000
NUM_WORKSPACES = 2500
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

TIERS = ['free', 'starter', 'professional', 'enterprise']
TIER_DISTRIBUTION = [0.60, 0.25, 0.12, 0.03]

# Churn rates by tier (monthly)
CHURN_RATES = {
    'free': 0.15,
    'starter': 0.08,
    'professional': 0.03,
    'enterprise': 0.01
}

print("📊 Configuration:")
print(f"   Users: {NUM_USERS:,}")
print(f"   Workspaces: {NUM_WORKSPACES:,}")
print(f"   Date Range: {START_DATE.date()} to {END_DATE.date()}")
print()

# ============================================================================
# TABLE 1: USERS
# ============================================================================

print("🔨 Generating users table...")

users_data = []
workspace_ids = [f"WS{str(i).zfill(6)}" for i in range(1, NUM_WORKSPACES + 1)]

for i in range(1, NUM_USERS + 1):
    user_id = f"U{str(i).zfill(6)}"
    workspace_id = random.choice(workspace_ids)

    # Signup date distribution:
    # 80% spread across entire range (growth curve)
    # 20% forced into Oct-Dec 2025 (A/B test window) to ensure sufficient sample
    days_range = (END_DATE - START_DATE).days
    if i <= NUM_USERS * 0.80:
        signup_date = START_DATE + timedelta(days=np.random.randint(0, days_range))
    else:
        # A/B test window: Oct 1 - Dec 31, 2025
        ab_start = datetime(2025, 10, 1)
        ab_days = (END_DATE - ab_start).days
        signup_date = ab_start + timedelta(days=np.random.randint(0, ab_days))

    # Account tier
    tier = np.random.choice(TIERS, p=TIER_DISTRIBUTION)

    # Determine if churned
    months_since_signup = (END_DATE - signup_date).days / 30
    churn_probability = 1 - (1 - CHURN_RATES[tier]) ** months_since_signup
    is_churned = np.random.random() < churn_probability

    if is_churned:
        churn_offset_days = np.random.randint(7, max(8, int((END_DATE - signup_date).days * 0.8)))
        last_login = signup_date + timedelta(days=churn_offset_days)
        is_active = False
    else:
        last_login = END_DATE - timedelta(days=np.random.randint(0, 7))
        is_active = True

    users_data.append({
        'user_id': user_id,
        'workspace_id': workspace_id,
        'email': fake.email(),
        'signup_date': signup_date,
        'account_tier': tier,
        'user_role': np.random.choice(['owner', 'admin', 'member', 'guest'], p=[0.10, 0.20, 0.60, 0.10]),
        'industry': np.random.choice(['tech', 'marketing', 'finance', 'healthcare', 'education', 'retail']),
        'team_size': np.random.choice([5, 10, 25, 50, 100, 250], p=[0.40, 0.30, 0.15, 0.10, 0.04, 0.01]),
        'signup_source': np.random.choice(['organic', 'paid_search', 'referral', 'sales'], p=[0.40, 0.30, 0.20, 0.10]),
        'country': np.random.choice(['US', 'UK', 'Canada', 'Germany', 'Australia']),
        'is_active': is_active,
        'last_login_date': last_login
    })

users_df = pd.DataFrame(users_data)
print(f"   ✅ Generated {len(users_df):,} users")

# ============================================================================
# TABLE 2: USER ACTIVITY SUMMARY (80/20 power user distribution)
# ============================================================================

print("🔨 Generating user_activity_summary table...")

activity_data = []

for idx, user in users_df.iterrows():
    days_since_signup = (END_DATE - user['signup_date']).days

    # 80/20 rule: 20% of users drive 80% of activity
    user_type = np.random.choice(['power_user', 'regular', 'casual'], p=[0.20, 0.50, 0.30])

    if user_type == 'power_user':
        total_sessions = np.random.randint(50, 200)
        total_events = np.random.randint(500, 2000)
        avg_session_duration = np.random.uniform(15, 45)
        tasks_created = np.random.randint(50, 300)
        tasks_completed = int(tasks_created * np.random.uniform(0.6, 0.9))
        boards_created = np.random.randint(5, 20)
        premium_features_used = np.random.randint(3, 6) if user['account_tier'] in ['professional', 'enterprise'] else np.random.randint(0, 2)
    elif user_type == 'regular':
        total_sessions = np.random.randint(10, 50)
        total_events = np.random.randint(50, 500)
        avg_session_duration = np.random.uniform(8, 20)
        tasks_created = np.random.randint(10, 50)
        tasks_completed = int(tasks_created * np.random.uniform(0.5, 0.8))
        boards_created = np.random.randint(1, 5)
        premium_features_used = np.random.randint(0, 3) if user['account_tier'] in ['professional', 'enterprise'] else 0
    else:
        total_sessions = np.random.randint(1, 10)
        total_events = np.random.randint(5, 50)
        avg_session_duration = np.random.uniform(3, 10)
        tasks_created = np.random.randint(0, 10)
        tasks_completed = int(tasks_created * np.random.uniform(0.3, 0.6))
        boards_created = np.random.randint(0, 2)
        premium_features_used = 0

    # Churned users have lower activity
    if not user['is_active']:
        total_sessions = int(total_sessions * 0.3)
        total_events = int(total_events * 0.3)

    is_at_risk = (END_DATE - user['last_login_date']).days > 14

    activity_data.append({
        'user_id': user['user_id'],
        'workspace_id': user['workspace_id'],
        'signup_date': user['signup_date'].date(),
        'days_since_signup': days_since_signup,
        'total_sessions': total_sessions,
        'total_events': total_events,
        'avg_session_duration_min': round(avg_session_duration, 1),
        'tasks_created': tasks_created,
        'tasks_completed': tasks_completed,
        'boards_created': boards_created,
        'premium_features_used': premium_features_used,
        'last_active_date': user['last_login_date'].date(),
        'is_power_user': user_type == 'power_user',
        'is_at_risk_churn': is_at_risk,
        'cohort_month': user['signup_date'].strftime('%Y-%m')
    })

activity_df = pd.DataFrame(activity_data)
print(f"   ✅ Generated {len(activity_df):,} activity summaries")

# ============================================================================
# TABLE 3: ONBOARDING FUNNEL (With realistic drop-offs)
# ============================================================================

print("🔨 Generating onboarding_funnel table...")

onboarding_data = []

STEP_COMPLETION_RATES = {
    1: 0.85,
    2: 0.82,
    3: 0.64,  # THE PROBLEM STEP - 36% drop-off
    4: 0.78
}

for idx, user in users_df.iterrows():
    # A/B test variant for users Oct-Dec 2025
    if user['signup_date'] >= datetime(2025, 10, 1) and user['signup_date'] <= datetime(2025, 12, 31):
        ab_variant = np.random.choice(['control', 'variant_a'])
    else:
        ab_variant = None

    step_1_completed = np.random.random() < STEP_COMPLETION_RATES[1]
    step_1_time = user['signup_date'] + timedelta(minutes=np.random.randint(5, 30)) if step_1_completed else None

    step_2_completed = step_1_completed and (np.random.random() < STEP_COMPLETION_RATES[2])
    step_2_time = step_1_time + timedelta(minutes=np.random.randint(10, 60)) if step_2_completed else None

    # Step 3: variant_a has better completion rate
    step_3_rate = 0.80 if ab_variant == 'variant_a' else STEP_COMPLETION_RATES[3]
    step_3_completed = step_2_completed and (np.random.random() < step_3_rate)
    step_3_time = step_2_time + timedelta(hours=np.random.randint(1, 48)) if step_3_completed else None

    step_4_completed = step_3_completed and (np.random.random() < STEP_COMPLETION_RATES[4])
    step_4_time = step_3_time + timedelta(minutes=np.random.randint(5, 30)) if step_4_completed else None

    if step_4_completed:
        time_to_complete_hours = (step_4_time - user['signup_date']).total_seconds() / 3600
        onboarding_completed = True
        completion_date = step_4_time
    else:
        time_to_complete_hours = None
        onboarding_completed = False
        completion_date = None

    onboarding_data.append({
        'user_id': user['user_id'],
        'step_1_completed': step_1_completed,
        'step_1_timestamp': step_1_time,
        'step_2_completed': step_2_completed,
        'step_2_timestamp': step_2_time,
        'step_3_completed': step_3_completed,
        'step_3_timestamp': step_3_time,
        'step_4_completed': step_4_completed,
        'step_4_timestamp': step_4_time,
        'onboarding_completed': onboarding_completed,
        'onboarding_completion_date': completion_date,
        'time_to_complete_hours': time_to_complete_hours,
        'ab_test_variant': ab_variant
    })

onboarding_df = pd.DataFrame(onboarding_data)
print(f"   ✅ Generated {len(onboarding_df):,} onboarding records")

# ============================================================================
# TABLE 4: FEATURE USAGE (With discovery friction)
# ============================================================================

print("🔨 Generating feature_usage table...")

FEATURES = {
    'kanban_boards': {'adoption_rate': 0.85, 'is_premium': False},
    'time_tracking': {'adoption_rate': 0.12, 'is_premium': True},    # LOW ADOPTION, HIGH VALUE
    'automation_rules': {'adoption_rate': 0.08, 'is_premium': True},
    'custom_fields': {'adoption_rate': 0.15, 'is_premium': True},
    'reporting_dashboard': {'adoption_rate': 0.65, 'is_premium': False},
    'integrations_slack': {'adoption_rate': 0.40, 'is_premium': False},
    'integrations_google_drive': {'adoption_rate': 0.30, 'is_premium': False}
}

feature_data = []

for idx, user in users_df.iterrows():
    for feature_name, feature_config in FEATURES.items():
        if feature_config['is_premium'] and user['account_tier'] == 'free':
            continue

        if np.random.random() < feature_config['adoption_rate']:
            days_until_discovery = int(np.random.gamma(shape=2, scale=20))
            first_used = user['signup_date'] + timedelta(days=days_until_discovery)
            total_usage = np.random.randint(1, 50) if user['is_active'] else np.random.randint(1, 10)
            last_used = user['last_login_date'] if user['is_active'] else first_used + timedelta(days=np.random.randint(1, 30))

            feature_data.append({
                'usage_id': f"FU{len(feature_data) + 1:08d}",
                'user_id': user['user_id'],
                'feature_name': feature_name,
                'first_used_date': first_used,
                'total_usage_count': total_usage,
                'last_used_date': last_used,
                'days_since_signup_at_first_use': days_until_discovery
            })

feature_df = pd.DataFrame(feature_data)
print(f"   ✅ Generated {len(feature_df):,} feature usage records")

# ============================================================================
# TABLE 5: SUBSCRIPTIONS
# ============================================================================

print("🔨 Generating subscriptions table...")

subscription_data = []

for workspace_id in users_df['workspace_id'].unique():
    workspace_users = users_df[users_df['workspace_id'] == workspace_id]
    owner = workspace_users[workspace_users['user_role'] == 'owner']
    plan_type = owner.iloc[0]['account_tier'] if len(owner) > 0 else workspace_users.iloc[0]['account_tier']

    user_count = len(workspace_users)
    mrr_map = {'free': 0, 'starter': 10, 'professional': 25, 'enterprise': 50}
    mrr = user_count * mrr_map[plan_type]

    start_date = workspace_users['signup_date'].min()
    is_any_active = workspace_users['is_active'].any()

    if not is_any_active:
        churn_date = workspace_users['last_login_date'].max()
        end_date = churn_date
        churn_reason = np.random.choice(['price', 'feature_gap', 'competitor', 'other'], p=[0.30, 0.25, 0.35, 0.10])
    else:
        churn_date = None
        end_date = None
        churn_reason = None

    subscription_data.append({
        'subscription_id': f"SUB{len(subscription_data) + 1:06d}",
        'workspace_id': workspace_id,
        'plan_type': plan_type,
        'mrr': mrr,
        'start_date': start_date,
        'end_date': end_date,
        'is_active': is_any_active,
        'churn_date': churn_date,
        'churn_reason': churn_reason
    })

subscriptions_df = pd.DataFrame(subscription_data)
print(f"   ✅ Generated {len(subscriptions_df):,} subscription records")

# ============================================================================
# TABLE 6: A/B TEST ASSIGNMENTS
# ============================================================================

print("🔨 Generating ab_test_assignments table...")

# Use the onboarding table's variant assignment as source of truth
ab_onboarding = onboarding_df[onboarding_df['ab_test_variant'].notna()].copy()

ab_test_data = []

for idx, ob_record in ab_onboarding.iterrows():
    user_id = ob_record['user_id']
    user_row = users_df[users_df['user_id'] == user_id].iloc[0]

    ab_test_data.append({
        'user_id': user_id,
        'test_name': 'simplified_onboarding_q4_2025',
        'variant': ob_record['ab_test_variant'],
        'assignment_date': user_row['signup_date'],
        'converted': ob_record['onboarding_completed'],
        'conversion_date': ob_record['onboarding_completion_date']
    })

ab_test_df = pd.DataFrame(ab_test_data)
print(f"   ✅ Generated {len(ab_test_df):,} A/B test assignments")

# ============================================================================
# TABLE 7: EVENTS (Behavioral event stream - sampled)
# ============================================================================

print("🔨 Generating events table (sampling 2,000 users)...")

EVENT_TYPES = [
    'signup_completed', 'onboarding_step_1', 'onboarding_step_2',
    'onboarding_step_3', 'onboarding_step_4', 'onboarding_completed',
    'task_created', 'task_completed', 'board_created',
    'automation_created', 'time_tracking_started', 'custom_field_added',
    'report_generated', 'integration_connected', 'upgrade_initiated', 'upgrade_completed'
]

EVENT_WEIGHTS = [
    0.01, 0.05, 0.05, 0.04, 0.03, 0.02,
    0.30, 0.25, 0.05,
    0.02, 0.02, 0.02,
    0.03, 0.05, 0.03, 0.03
]

events_data = []
event_id_counter = 1
sample_users = users_df.sample(n=min(2000, len(users_df)), random_state=42)

for idx, user in sample_users.iterrows():
    num_events = activity_df[activity_df['user_id'] == user['user_id']]['total_events'].values[0]
    active_days = max(1, (user['last_login_date'] - user['signup_date']).days)

    for _ in range(num_events):
        event_time = user['signup_date'] + timedelta(
            days=np.random.randint(0, max(1, active_days)),
            hours=np.random.randint(8, 22),
            minutes=np.random.randint(0, 60)
        )
        event_name = np.random.choice(EVENT_TYPES, p=EVENT_WEIGHTS)

        events_data.append({
            'event_id': f"E{event_id_counter:010d}",
            'user_id': user['user_id'],
            'event_name': event_name,
            'event_timestamp': event_time,
            'session_id': f"SESSION{np.random.randint(1, 100000):08d}",
            'properties': '{}'
        })
        event_id_counter += 1

events_df = pd.DataFrame(events_data)
print(f"   ✅ Generated {len(events_df):,} events")

# ============================================================================
# SAVE ALL FILES
# ============================================================================

print()
print("💾 Saving CSV files...")

users_df.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)
print("   ✅ users.csv")

activity_df.to_csv(os.path.join(DATA_DIR, 'user_activity_summary.csv'), index=False)
print("   ✅ user_activity_summary.csv")

onboarding_df.to_csv(os.path.join(DATA_DIR, 'onboarding_funnel.csv'), index=False)
print("   ✅ onboarding_funnel.csv")

feature_df.to_csv(os.path.join(DATA_DIR, 'feature_usage.csv'), index=False)
print("   ✅ feature_usage.csv")

subscriptions_df.to_csv(os.path.join(DATA_DIR, 'subscriptions.csv'), index=False)
print("   ✅ subscriptions.csv")

ab_test_df.to_csv(os.path.join(DATA_DIR, 'ab_test_assignments.csv'), index=False)
print("   ✅ ab_test_assignments.csv")

events_df.to_csv(os.path.join(DATA_DIR, 'events.csv'), index=False)
print("   ✅ events.csv")

print()
print("=" * 70)
print("✅ DATA GENERATION COMPLETE!")
print("=" * 70)
print()
print("📊 Summary:")
print(f"   - {len(users_df):,} users")
print(f"   - {len(subscriptions_df):,} workspaces")
print(f"   - {len(events_df):,} events")
print(f"   - {len(feature_df):,} feature usage records")
print(f"   - {len(ab_test_df):,} A/B test participants")
print()
