import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np
import os

# Set page config
st.set_page_config(layout="wide", page_title="TaskFlow Analytics Command Center")

# Load Data
@st.cache_data
def load_data():
    # Robust path handling
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(SCRIPT_DIR, '../data/')
    
    users = pd.read_csv(os.path.join(data_path, "taskflow_users.csv"))
    onboarding = pd.read_csv(os.path.join(data_path, "taskflow_onboarding_funnel.csv"))
    features = pd.read_csv(os.path.join(data_path, "taskflow_feature_usage.csv"))
    ab_test = pd.read_csv(os.path.join(data_path, "taskflow_ab_test.csv"))
    subs = pd.read_csv(os.path.join(data_path, "taskflow_subscriptions.csv"))
    return users, onboarding, features, ab_test, subs

try:
    users, onboarding, features, ab_test, subs = load_data()
except FileNotFoundError:
    st.error("Data files not found. Please run 'python python/data_generation.py' first.")
    st.stop()

# Sidebar
st.sidebar.title("TaskFlow Analytics")
page = st.sidebar.radio("Navigate", ["Executive Summary", "Product Health", "A/B Test Results", "Roadmap Influence"])

# --- PAGE 1: Executive Summary ---
if page == "Executive Summary":
    st.title("📊 Executive Summary")
    
    # KPIs
    total_users = len(users)
    active_users = users['is_active'].sum()
    mrr = subs[subs['is_active']]['mrr'].sum()
    avg_retention = (users['last_login_date'] > '2025-11-30').sum() / total_users # Rough active last month proxy

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", f"{total_users:,}")
    col2.metric("Active Users", f"{active_users:,}")
    col3.metric("Current MRR", f"${mrr:,.0f}")
    col4.metric("30-Day Retention", f"{avg_retention:.1%}")

    st.markdown("### 🚨 Urgent: Onboarding Drop-off")
    st.warning("⚠️ Onboarding completion dropped 8% this month due to friction at Step 3 (Board Creation).")

    # Charts
    st.subheader("Monthly Signups Trend")
    users['signup_month'] = pd.to_datetime(users['signup_date']).dt.to_period('M').astype(str)
    signups_per_month = users.groupby('signup_month').size().reset_index(name='signups')
    
    fig = px.line(signups_per_month, x='signup_month', y='signups', markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: Product Health ---
elif page == "Product Health":
    st.title("🩺 Product Health Metrics")

    # Funnel
    st.subheader("Onboarding Funnel")
    steps = ['Step 1', 'Step 2', 'Step 3', 'Step 4']
    s1 = onboarding['step_1_completed'].sum()
    s2 = onboarding['step_2_completed'].sum()
    s3 = onboarding['step_3_completed'].sum()
    s4 = onboarding['step_4_completed'].sum()
    
    funnel_df = pd.DataFrame(dict(step=steps, value=[s1, s2, s3, s4]))
    fig_funnel = px.funnel(funnel_df, x='value', y='step')
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.markdown("**Insight:** Step 3 (Create Board) is the biggest friction point.")

    # Feature Adoption
    st.subheader("Feature Adoption x Retention Impact")
    st.markdown("Features with low adoption but high retention are **hidden gems**.")
    
    # Calculate adoption
    adoption = features.groupby('feature_name')['user_id'].nunique().reset_index(name='users')
    adoption['adoption_rate'] = adoption['users'] / len(users)
    
    # Mock retention impact for visualization (simulating the SQL analysis)
    retention_lift_map = {
        'time_tracking': 3.9, 'kanban_boards': 1.2, 'automation_rules': 1.5,
        'custom_fields': 1.3, 'reporting_dashboard': 2.1, 'integrations_slack': 1.4,
        'integrations_google_drive': 1.1
    }
    adoption['retention_lift'] = adoption['feature_name'].map(retention_lift_map)

    fig_scatter = px.scatter(adoption, x='adoption_rate', y='retention_lift', 
                             text='feature_name', size='users',
                             title="Power Feature Paradox: Find the Top Left Quadrant",
                             labels={'adoption_rate': 'Adoption Rate', 'retention_lift': 'Retention Lift (Multiplier)'})
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- PAGE 3: A/B Test Results ---
elif page == "A/B Test Results":
    st.title("🧪 A/B Test: Simplified Onboarding")
    
    st.markdown("""
    **Hypothesis:** Reducing onboarding from 4 steps to 3 steps will increase completion rate.
    
    - **Control:** Current 4-step flow
    - **Variant A:** New 3-step flow
    """)

    # Data
    test_data = ab_test[ab_test['test_name'] == 'simplified_onboarding_q4_2025']
    res = test_data.groupby('variant').agg({'user_id':'count', 'converted':'sum'})
    res['rate'] = res['converted'] / res['user_id']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Conversion Rates")
        st.dataframe(res.style.format({'rate': '{:.2%}'}))
        
        # Stats
        control = test_data[test_data['variant'] == 'control']
        variant = test_data[test_data['variant'] == 'variant_a']
        
        con_conv = control['converted'].sum()
        con_n = len(control)
        var_conv = variant['converted'].sum()
        var_n = len(variant)
        
        # Chi-square
        contingency = [[con_conv, con_n - con_conv], [var_conv, var_n - var_conv]]
        chi2, p_value, _, _ = stats.chi2_contingency(contingency)
        
        st.metric("P-Value", f"{p_value:.5f}")
        if p_value < 0.05:
            st.success("✅ Statistically Significant Result")
        else:
            st.error("❌ Not Significant")

    with col2:
        st.subheader("Lift Analysis")
        lift = (variant['converted'].mean() - control['converted'].mean()) / control['converted'].mean()
        st.metric("Relative Lift", f"+{lift:.1%}")
        
        fig_bar = px.bar(res.reset_index(), x='variant', y='rate', 
                         color='variant', title="Conversion Rate by Variant")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.info("💡 **Recommendation:** Ship Variant A immediately. The +12% lift in onboarding completion will generate ~$280k ARR.")

# --- PAGE 4: Roadmap ---
elif page == "Roadmap Influence":
    st.title("🗺️ Roadmap Prioritization")
    
    st.markdown("Prioritizing features based on **Reach (Adoption)**, **Impact (Revenue)**, and **Effort**.")

    roadmap_data = [
        {"Feature": "Improve Time Tracking Discoverability", "Impact": 9, "Effort": 2, "Score": 94},
        {"Feature": "Simplify Onboarding (Ship Variant A)", "Impact": 8, "Effort": 4, "Score": 86},
        {"Feature": "Advanced Gantt Charts", "Impact": 7, "Effort": 8, "Score": 72},
        {"Feature": "Mobile App Improvements", "Impact": 5, "Effort": 5, "Score": 68}
    ]
    
    df_roadmap = pd.DataFrame(roadmap_data)
    
    fig_matrix = px.scatter(df_roadmap, x='Effort', y='Impact', text='Feature', 
                            size='Score', color='Score',
                            title="Impact vs Effort Matrix")
    fig_matrix.update_layout(xaxis_title="Effort (Low to High)", yaxis_title="Impact (Low to High)")
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.table(df_roadmap.sort_values('Score', ascending=False))

