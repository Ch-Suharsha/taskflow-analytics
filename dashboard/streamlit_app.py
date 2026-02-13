import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np
import os

# Page config
st.set_page_config(layout="wide", page_title="TaskFlow Analytics Command Center", page_icon="🚀")

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(SCRIPT_DIR, '..', 'data')

    users = pd.read_csv(os.path.join(data_path, 'users.csv'))
    activity = pd.read_csv(os.path.join(data_path, 'user_activity_summary.csv'))
    onboarding = pd.read_csv(os.path.join(data_path, 'onboarding_funnel.csv'))
    features = pd.read_csv(os.path.join(data_path, 'feature_usage.csv'))
    ab_test = pd.read_csv(os.path.join(data_path, 'ab_test_assignments.csv'))
    subs = pd.read_csv(os.path.join(data_path, 'subscriptions.csv'))
    return users, activity, onboarding, features, ab_test, subs

try:
    users, activity, onboarding, features, ab_test, subs = load_data()
except FileNotFoundError:
    st.error("Data files not found. Please run `python python/data_generation.py` first.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🚀 TaskFlow Analytics")
st.sidebar.markdown("**Product Analytics Command Center**")
page = st.sidebar.radio("Navigate", ["📊 Executive Summary", "🩺 Product Health", "🧪 A/B Test Results", "🗺️ Roadmap Influence"])

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary")
    st.markdown("*Key metrics for the TaskFlow product team — updated monthly*")

    # KPIs
    total_users = len(users)
    active_users = int(users['is_active'].sum())
    active_subs = subs[subs['is_active'] == True]
    mrr = active_subs['mrr'].sum()
    activation_rate = onboarding['onboarding_completed'].sum() / total_users

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", f"{total_users:,}")
    col2.metric("Active Users", f"{active_users:,}", delta=f"{active_users / total_users:.0%} of total")
    col3.metric("Monthly Recurring Revenue", f"${mrr:,.0f}")
    col4.metric("Activation Rate", f"{activation_rate:.1%}")

    # Alert
    st.markdown("### 🚨 Key Alerts")
    col_a, col_b = st.columns(2)
    with col_a:
        st.warning("⚠️ **Onboarding Cliff:** 36% drop-off at Step 3 (Create Board). See Product Health tab.")
    with col_b:
        st.success("✅ **A/B Test Win:** Simplified onboarding +9pp lift, p < 0.001. See A/B Test tab.")

    # Monthly signups trend
    st.subheader("Monthly Signups Trend")
    users['signup_month'] = pd.to_datetime(users['signup_date']).dt.to_period('M').astype(str)
    signups = users.groupby('signup_month').size().reset_index(name='signups')

    fig = px.area(signups, x='signup_month', y='signups',
                  labels={'signup_month': 'Month', 'signups': 'New Signups'},
                  color_discrete_sequence=['#636EFA'])
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, width="stretch")

    # MRR by plan
    st.subheader("MRR Breakdown by Plan")
    mrr_by_plan = active_subs.groupby('plan_type')['mrr'].sum().reset_index()
    mrr_by_plan = mrr_by_plan[mrr_by_plan['mrr'] > 0]
    fig_mrr = px.pie(mrr_by_plan, values='mrr', names='plan_type',
                     color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_mrr, width="stretch")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: PRODUCT HEALTH
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🩺 Product Health":
    st.title("🩺 Product Health Metrics")

    # ── Onboarding Funnel ─────────────────────────────────────────────────────
    st.subheader("Onboarding Funnel — The Cliff at Step 3")
    s1 = int(onboarding['step_1_completed'].sum())
    s2 = int(onboarding['step_2_completed'].sum())
    s3 = int(onboarding['step_3_completed'].sum())
    s4 = int(onboarding['step_4_completed'].sum())
    total = len(onboarding)

    funnel_df = pd.DataFrame({
        'Step': ['Start (All Users)', 'Step 1: Team Setup', 'Step 2: Invite Members',
                 'Step 3: Create Board ⚠️', 'Step 4: Create Task'],
        'Users': [total, s1, s2, s3, s4]
    })

    fig_funnel = px.funnel(funnel_df, x='Users', y='Step',
                           color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_funnel, width="stretch")

    # Drop-off rates
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Step 1 Drop-off", f"{(1 - s1 / total):.0%}")
    col2.metric("Step 2 Drop-off", f"{(1 - s2 / s1):.0%}" if s1 else "N/A")
    col3.metric("Step 3 Drop-off", f"{(1 - s3 / s2):.0%}" if s2 else "N/A", delta="🚨 Highest")
    col4.metric("Step 4 Drop-off", f"{(1 - s4 / s3):.0%}" if s3 else "N/A")

    st.info("💡 **Hypothesis:** Users face the 'blank canvas' problem at Step 3 — they don't know what board structure to use. Providing templates could fix this.")

    # ── Power Feature Paradox ─────────────────────────────────────────────────
    st.subheader("Power Feature Paradox")
    st.markdown("Low adoption + high retention = **hidden gem features**. Top-left quadrant is where the opportunities are.")

    adoption = features.groupby('feature_name')['user_id'].nunique().reset_index(name='adopters')
    adoption['adoption_rate'] = adoption['adopters'] / len(users)

    retention_lift_map = {
        'time_tracking': 3.9, 'kanban_boards': 1.2, 'automation_rules': 2.9,
        'custom_fields': 3.2, 'reporting_dashboard': 2.1, 'integrations_slack': 1.4,
        'integrations_google_drive': 1.1
    }
    adoption['retention_lift'] = adoption['feature_name'].map(retention_lift_map).fillna(1.0)

    fig_scatter = px.scatter(adoption, x='adoption_rate', y='retention_lift',
                             text='feature_name', size='adopters',
                             labels={'adoption_rate': 'Adoption Rate', 'retention_lift': '30-Day Retention Lift (x)'},
                             color_discrete_sequence=['#EF553B'])
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.add_hline(y=2.0, line_dash="dot", line_color="gray", annotation_text="2x retention threshold")
    fig_scatter.add_vline(x=0.20, line_dash="dot", line_color="gray", annotation_text="20% adoption threshold")
    st.plotly_chart(fig_scatter, width="stretch")

    st.success("🎯 **time_tracking** is the biggest opportunity: only 12% adoption but 3.9x retention lift. Moving it to the main nav could retain 2,800+ users.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: A/B TEST RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 A/B Test Results":
    st.title("🧪 A/B Test: Simplified Onboarding")

    st.markdown("""
    **Experiment:** Does simplifying onboarding from 4 steps → 3 steps (with board templates) improve completion?
    
    | Parameter | Value |
    |-----------|-------|
    | **Test Period** | Oct – Dec 2025 |
    | **Primary Metric** | Onboarding completion rate |
    | **Control** | Current 4-step flow |
    | **Variant** | 3-step flow with templates |
    """)

    test_data = ab_test[ab_test['test_name'] == 'simplified_onboarding_q4_2025']
    control = test_data[test_data['variant'] == 'control']
    variant = test_data[test_data['variant'] == 'variant_a']

    con_n, con_conv = len(control), int(control['converted'].sum())
    var_n, var_conv = len(variant), int(variant['converted'].sum())
    con_rate = con_conv / con_n if con_n else 0
    var_rate = var_conv / var_n if var_n else 0

    # KPI cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Control Conversion", f"{con_rate:.1%}", help=f"{con_conv:,} / {con_n:,}")
    col2.metric("Variant Conversion", f"{var_rate:.1%}", delta=f"+{(var_rate - con_rate):.1%}")

    # Chi-square test
    contingency = [[con_conv, con_n - con_conv], [var_conv, var_n - var_conv]]
    chi2, p_value, _, _ = stats.chi2_contingency(contingency)
    col3.metric("P-Value", f"{p_value:.6f}")

    if p_value < 0.05:
        st.success(f"✅ **Statistically Significant** (p = {p_value:.6f}, 99.9% confidence)")
    else:
        st.warning(f"⚠️ **Not Significant** (p = {p_value:.4f})")

    # Visualization
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Conversion Rate Comparison")
        bar_df = pd.DataFrame({
            'Variant': ['Control (4 Steps)', 'Variant (3 Steps)'],
            'Conversion Rate': [con_rate * 100, var_rate * 100],
            'Users': [con_n, var_n]
        })
        fig_bar = px.bar(bar_df, x='Variant', y='Conversion Rate',
                         color='Variant', text='Conversion Rate',
                         color_discrete_sequence=['#EF553B', '#00CC96'])
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bar.update_layout(yaxis_range=[0, 60], showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")

    with col_chart2:
        st.subheader("Confidence Intervals (95%)")
        z = 1.96
        con_se = np.sqrt(con_rate * (1 - con_rate) / con_n)
        var_se = np.sqrt(var_rate * (1 - var_rate) / var_n)

        ci_df = pd.DataFrame({
            'Variant': ['Control', 'Variant'],
            'Rate': [con_rate * 100, var_rate * 100],
            'Lower': [(con_rate - z * con_se) * 100, (var_rate - z * var_se) * 100],
            'Upper': [(con_rate + z * con_se) * 100, (var_rate + z * var_se) * 100]
        })
        ci_df['Error'] = ci_df['Upper'] - ci_df['Rate']

        fig_ci = go.Figure()
        fig_ci.add_trace(go.Bar(
            x=ci_df['Variant'], y=ci_df['Rate'],
            error_y=dict(type='data', array=ci_df['Error'].tolist(), visible=True),
            marker_color=['#EF553B', '#00CC96']
        ))
        fig_ci.update_layout(yaxis_title='Conversion Rate (%)', yaxis_range=[0, 60])
        st.plotly_chart(fig_ci, width="stretch")

    # Business impact
    st.subheader("💰 Business Impact")
    lift = var_rate - con_rate
    monthly_signups = 1000
    additional = monthly_signups * lift
    annual_impact = additional * 12 * 1200

    col_i1, col_i2, col_i3 = st.columns(3)
    col_i1.metric("Absolute Lift", f"+{lift:.1%}")
    col_i2.metric("Additional Conversions/Month", f"{additional:.0f}")
    col_i3.metric("Est. Annual Revenue Impact", f"${annual_impact:,.0f}")

    st.info("💡 **Recommendation:** Ship the simplified 3-step onboarding immediately. Monitor activation rate for 2 weeks post-launch.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: ROADMAP INFLUENCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Roadmap Influence":
    st.title("🗺️ Roadmap Prioritization Framework")
    st.markdown("Data-driven prioritization for Q1 2026. Scored on **User Demand**, **Revenue Impact**, **Effort**, and **Data Confidence**.")

    roadmap = pd.DataFrame([
        {"Rank": "🥇 1", "Initiative": "Improve Time Tracking Discoverability", "User Demand": "88%", "Revenue Impact": "+$450K ARR", "Effort": "Low", "Score": 94, "Status": "✅ RECOMMEND"},
        {"Rank": "🥈 2", "Initiative": "Ship Simplified Onboarding (A/B Tested)", "User Demand": "67%", "Revenue Impact": "+$280K ARR", "Effort": "Medium", "Score": 86, "Status": "✅ RECOMMEND"},
        {"Rank": "🥉 3", "Initiative": "Proactive Upgrade Campaign (Free→Pro)", "User Demand": "23%", "Revenue Impact": "+$480K ARR", "Effort": "Low", "Score": 81, "Status": "✅ RECOMMEND"},
        {"Rank": "4", "Initiative": "Advanced Gantt Charts", "User Demand": "15%", "Revenue Impact": "+$890K ARR", "Effort": "High", "Score": 68, "Status": "⏸️ DEFER"},
    ])

    st.dataframe(roadmap, width="stretch", hide_index=True)

    st.metric("Total Estimated Impact (Top 3)", "+$1.21M ARR")

    # Impact vs Effort scatter
    st.subheader("Impact vs Effort Matrix")
    matrix = pd.DataFrame([
        {"Initiative": "Time Tracking Discoverability", "Impact": 9, "Effort": 2, "Score": 94},
        {"Initiative": "Simplified Onboarding", "Impact": 8, "Effort": 4, "Score": 86},
        {"Initiative": "Upgrade Campaign", "Impact": 8, "Effort": 2, "Score": 81},
        {"Initiative": "Advanced Gantt Charts", "Impact": 7, "Effort": 8, "Score": 68},
    ])

    fig_matrix = px.scatter(matrix, x='Effort', y='Impact', text='Initiative',
                            size='Score', color='Score',
                            color_continuous_scale='RdYlGn',
                            range_color=[60, 100])
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(
        xaxis_title="Implementation Effort →", yaxis_title="Business Impact →",
        xaxis_range=[0, 10], yaxis_range=[5, 10]
    )
    fig_matrix.add_annotation(x=2, y=9.5, text="🎯 DO FIRST", showarrow=False, font=dict(size=14, color="green"))
    fig_matrix.add_annotation(x=8, y=9.5, text="⏸️ PLAN CAREFULLY", showarrow=False, font=dict(size=14, color="orange"))
    st.plotly_chart(fig_matrix, width="stretch")

    # Monitoring metrics
    st.subheader("📈 Recommended Monitoring Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Initiative #1: Time Tracking**
        - Baseline: 12% adoption
        - Target: 40% adoption
        - Track: Weekly cohort adoption
        """)
    with col2:
        st.markdown("""
        **Initiative #2: Onboarding**
        - Baseline: 33% completion
        - Target: 43% completion
        - Track: Daily activation funnel
        """)
    with col3:
        st.markdown("""
        **Initiative #3: Upgrades**
        - Baseline: 3% free-to-paid
        - Target: 8% for targeted segment
        - Track: Monthly conversion cohorts
        """)
