# 🚀 TaskFlow Analytics Command Center

**A Product Analytics Portfolio Project Demonstrating Real-World Roadmap Influence**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://taskflow-analytics-suharsha.streamlit.app)
**[👉 View Live Dashboard](https://taskflow-analytics-suharsha.streamlit.app)**

---

## 📊 Quick Stats

- **10,000 users** analyzed across 2,500 workspaces
- **472K+ behavioral events** tracked over 24 months
- **3 major insights** discovered through proactive analysis
- **$1.21M ARR impact** from data-driven recommendations
- **1 A/B test** validated with 99.9% statistical confidence

---

## 🎯 The Business Problem

**Company**: TaskFlow (fictional Series D SaaS — B2B Project Management Platform)  
**Stage**: $50M ARR, 15,000 active workspaces, 8-person Product team  
**Challenge**: Growth is slowing. The Head of Product asked:

> *"Why are activation rates declining? What features should we prioritize to improve retention?"*

**My Role**: Product Analyst tasked with finding data-driven answers to influence Q1 2026 roadmap.

---

## 🔍 My Approach: 4-Part Analysis Framework

### Phase 1: Proactive Discovery
I didn't wait for stakeholders to ask questions. I analyzed usage data to find **hidden patterns**:
- Which features drive outsized retention despite low adoption?
- Where exactly do users abandon onboarding?

### Phase 2: Hypothesis Validation
I designed and simulated an A/B test to validate product changes:
- Simplified onboarding flow (4 steps → 3 steps with templates)

### Phase 3: Statistical Rigor
I ran proper statistical tests to ensure decisions weren't based on noise:
- Chi-Square test with confidence intervals
- P-value < 0.001 (99.9% confidence)

### Phase 4: Strategic Recommendation
I translated findings into a roadmap prioritization framework:
- Scored opportunities on User Demand, Revenue Impact, Effort, and Data Confidence

---

## 💡 Key Insight #1: The "Power Feature Paradox"

**The Discovery:**  
Only 12% of users discover the "Time Tracking" feature, BUT users who find it have **3.9x higher 30-day retention** than those who don't.

**SQL Query Used:**

```sql
-- Business Question: Which low-adoption features drive the highest retention?
-- Data Source: feature_usage + user_activity_summary tables

WITH feature_retention AS (
    SELECT 
        fu.feature_name,
        COUNT(DISTINCT fu.user_id) AS total_adopters,
        SUM(CASE 
            WHEN uas.days_since_signup >= 30 
            AND uas.last_active_date >= uas.signup_date + INTERVAL '30 days'
            THEN 1 ELSE 0 
        END) AS retained_30d,
        ROUND(
            100.0 * SUM(CASE 
                WHEN uas.days_since_signup >= 30 
                AND uas.last_active_date >= uas.signup_date + INTERVAL '30 days'
                THEN 1 ELSE 0 
            END) / COUNT(DISTINCT fu.user_id), 1
        ) AS retention_pct
    FROM feature_usage fu
    JOIN user_activity_summary uas ON fu.user_id = uas.user_id
    WHERE fu.feature_name IN ('time_tracking', 'automation_rules', 'custom_fields')
    GROUP BY fu.feature_name
),
baseline_retention AS (
    SELECT 
        ROUND(
            100.0 * SUM(CASE 
                WHEN days_since_signup >= 30 
                AND last_active_date >= signup_date + INTERVAL '30 days'
                THEN 1 ELSE 0 
            END) / COUNT(*), 1
        ) AS retention_pct
    FROM user_activity_summary
    WHERE user_id NOT IN (
        SELECT DISTINCT user_id FROM feature_usage WHERE feature_name = 'time_tracking'
    )
)
SELECT 
    fr.feature_name,
    fr.total_adopters,
    fr.retention_pct AS feature_retention_pct,
    br.retention_pct AS baseline_retention_pct,
    ROUND(fr.retention_pct / br.retention_pct, 2) AS retention_lift
FROM feature_retention fr
CROSS JOIN baseline_retention br
ORDER BY retention_lift DESC;
```

**Query Results:**

| Feature | Adopters | Retention % | Retention Lift |
|---------|----------|-------------|----------------|
| time_tracking | 1,200 | 82.3% | **3.9x** ✅ |
| custom_fields | 1,500 | 68.1% | 3.2x |
| automation_rules | 800 | 61.4% | 2.9x |

**Business Impact:**  
If we move Time Tracking to the main navigation (increasing adoption from 12% → 40%), we could retain **2,800 additional users** monthly = **+$450K ARR**.

**See full query:** [`sql/01_power_feature_paradox.sql`](sql/01_power_feature_paradox.sql)

---

## 💡 Key Insight #2: The "Onboarding Cliff"

**The Discovery:**  
Users drop off at **Step 3 (Create First Board)** at a 36% rate — significantly higher than other steps.

**SQL Query Used:**

```sql
-- Business Question: Where do users abandon onboarding?
WITH funnel_metrics AS (
    SELECT 1 AS step_number, 'Step 1: Team Setup' AS step_name,
        COUNT(*) AS users_reached,
        SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END) AS users_completed,
        ROUND(100.0 * SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_rate,
        ROUND(100.0 * (1 - SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END)::FLOAT / COUNT(*)), 1) AS drop_off_rate
    FROM onboarding_funnel
    UNION ALL
    SELECT 2, 'Step 2: Invite Members',
        SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_1_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
    UNION ALL
    SELECT 3, 'Step 3: Create Board',
        SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_2_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
    UNION ALL
    SELECT 4, 'Step 4: Create Task',
        SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END),
        SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END), 0), 1),
        ROUND(100.0 * (1 - SUM(CASE WHEN step_4_completed THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN step_3_completed THEN 1 ELSE 0 END), 0)), 1)
    FROM onboarding_funnel
)
SELECT step_number, step_name, users_reached, users_completed, completion_rate, drop_off_rate,
    CASE 
        WHEN drop_off_rate > 30 THEN '🚨 HIGH DROP-OFF'
        WHEN drop_off_rate > 20 THEN '⚠️ MODERATE'
        ELSE '✅ NORMAL'
    END AS alert_status
FROM funnel_metrics ORDER BY step_number;
```

**Query Results:**

| Step | Users Reached | Completed | Completion % | Drop-off % | Alert |
|------|---------------|-----------|--------------|------------|-------|
| Step 1: Team Setup | 10,000 | 8,500 | 85.0% | 15.0% | ✅ NORMAL |
| Step 2: Invite Members | 8,500 | 7,000 | 82.4% | 17.6% | ✅ NORMAL |
| Step 3: Create Board | 7,000 | 4,480 | 64.0% | **36.0%** | 🚨 HIGH |
| Step 4: Create Task | 4,480 | 3,494 | 78.0% | 22.0% | ⚠️ MODERATE |

**Hypothesis:** Step 3 requires too much upfront thinking ("What should my board structure be?"). Providing pre-built templates could fix this.

**See full query:** [`sql/02_onboarding_cliff.sql`](sql/02_onboarding_cliff.sql)

---

## 🧪 A/B Test: Simplified Onboarding

**Experiment Design:**
- **Control (A)**: Current 4-step onboarding
- **Variant (B)**: Simplified 3-step onboarding (merged Step 3 & 4 with templates)
- **Sample Size**: ~1,500 users per variant (3,045 total)
- **Duration**: Oct–Dec 2025
- **Primary Metric**: Onboarding completion rate

**Python Statistical Analysis:**

```python
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np

df = pd.read_csv('data/ab_test_assignments.csv')

control = df[df['variant'] == 'control']
variant = df[df['variant'] == 'variant_a']

control_rate = control['converted'].sum() / len(control)
variant_rate = variant['converted'].sum() / len(variant)

# Chi-Square Test
contingency = [
    [control['converted'].sum(), len(control) - control['converted'].sum()],
    [variant['converted'].sum(), len(variant) - variant['converted'].sum()]
]
chi2, p_value, dof, expected = chi2_contingency(contingency)

# 95% Confidence Intervals
z = 1.96
con_se = np.sqrt(control_rate * (1 - control_rate) / len(control))
var_se = np.sqrt(variant_rate * (1 - variant_rate) / len(variant))

print(f"Control:  {control_rate:.1%}  CI: [{control_rate - z*con_se:.1%}, {control_rate + z*con_se:.1%}]")
print(f"Variant:  {variant_rate:.1%}  CI: [{variant_rate - z*var_se:.1%}, {variant_rate + z*var_se:.1%}]")
print(f"Lift:     +{(variant_rate - control_rate):.1%}")
print(f"P-Value:  {p_value:.6f}")
print(f"Significant: {'YES ✅' if p_value < 0.05 else 'NO ❌'}")
```

**Results:**

```
Control:  33.4%  CI: [31.0%, 35.8%]
Variant:  42.7%  CI: [40.2%, 45.2%]
Lift:     +9.3%
P-Value:  0.000000
Significant: YES ✅
```

**Interpretation:**  
With a p-value < 0.001, we reject the null hypothesis with **99.9% confidence**. The simplified onboarding performs significantly better. No overlap in confidence intervals confirms the result.

**Business Impact:**  
Shipping Variant B would increase activation by 9.3 percentage points = **+$280K ARR** from improved user retention.

**See full analysis:** [`python/ab_test_analysis.py`](python/ab_test_analysis.py)

---

## 💡 Key Insight #3: Undermonetized Segments

**The Discovery:**  
230 workspaces on the **Free plan** have 10+ active users and exhibit "Professional tier" usage patterns.

**SQL Query Used:**

```sql
-- Business Question: Which Free tier users should we target for upgrades?
WITH free_workspace_behavior AS (
    SELECT 
        s.workspace_id,
        COUNT(DISTINCT uas.user_id) AS total_users,
        ROUND(AVG(uas.total_sessions), 1) AS avg_sessions_per_user,
        ROUND(AVG(uas.premium_features_used), 1) AS avg_premium_features
    FROM subscriptions s
    JOIN user_activity_summary uas ON s.workspace_id = uas.workspace_id
    WHERE s.plan_type = 'free' AND s.is_active = TRUE
    GROUP BY s.workspace_id
),
professional_baseline AS (
    SELECT AVG(uas.total_sessions) AS pro_avg_sessions
    FROM subscriptions s
    JOIN user_activity_summary uas ON s.workspace_id = uas.workspace_id
    WHERE s.plan_type = 'professional' AND s.is_active = TRUE
)
SELECT 
    COUNT(*) AS undermonetized_workspaces,
    SUM(total_users) AS total_users_in_segment,
    ROUND(AVG(avg_sessions_per_user), 1) AS avg_engagement,
    ROUND(AVG(avg_premium_features), 1) AS avg_premium_features
FROM free_workspace_behavior fwb
CROSS JOIN professional_baseline pb
WHERE fwb.total_users >= 10 AND fwb.avg_premium_features >= 2;
```

**Business Opportunity:**  
If we convert 50% of these workspaces to Professional ($25/user/month):  
- 115 workspaces × 14 avg users × $25 = **+$40K MRR** = **+$480K ARR**

**See full query:** [`sql/03_undermonetized_segments.sql`](sql/03_undermonetized_segments.sql)

---

## 🎯 My Roadmap Recommendation

Based on the data analysis, I built a prioritization framework scoring opportunities on:
1. **User Demand** (% of users affected)
2. **Revenue Impact** (ARR lift potential)
3. **Implementation Effort** (Engineering months)
4. **Data Confidence** (Validation strength)

### Q1 2026 Roadmap Priority Ranking:

| Rank | Initiative | User Demand | Revenue Impact | Effort | Priority Score | Status |
|------|-----------|-------------|----------------|--------|----------------|--------|
| 🥇 1 | **Improve Time Tracking Discoverability** | 88% | +$450K ARR | Low | **94/100** | ✅ RECOMMEND |
| 🥈 2 | **Ship Simplified Onboarding (A/B Tested)** | 67% | +$280K ARR | Medium | **86/100** | ✅ RECOMMEND |
| 🥉 3 | **Proactive Upgrade Campaign (Free→Pro)** | 23% | +$480K ARR | Low | **81/100** | ✅ RECOMMEND |
| 4 | Advanced Gantt Charts | 15% | +$890K ARR | High | 68/100 | ⏸️ DEFER |

**Total Estimated Impact: +$1.21M ARR in 2026**

### Recommended Monitoring Metrics:

| Initiative | Baseline | Target | Tracking |
|-----------|----------|--------|----------|
| Time Tracking Discoverability | 12% adoption | 40% adoption | Weekly cohort adoption curves |
| Simplified Onboarding | 33% completion | 43% completion | Daily activation funnel |
| Upgrade Campaign | 3% free-to-paid | 8% for targeted segment | Monthly conversion cohorts |

---

## 🛠️ Technical Implementation

### Tech Stack
- **Data Generation**: Python (Pandas, NumPy, Faker)
- **Data Analysis**: SQL (PostgreSQL dialect), Python (SciPy for stats)
- **Visualization**: Streamlit, Plotly
- **Version Control**: Git/GitHub
- **Deployment**: Streamlit Cloud

### Data Schema
The project simulates a realistic SaaS analytics database with 7 tables:
- `users` (10K rows) — User profiles and account info
- `events` (472K rows) — Behavioral event stream
- `onboarding_funnel` (10K rows) — Onboarding step completion
- `feature_usage` (23K rows) — Feature adoption tracking
- `subscriptions` (2.5K rows) — Revenue and plan data
- `ab_test_assignments` (3K rows) — Experiment data
- `user_activity_summary` (10K rows) — Pre-aggregated metrics

**See schema details:** [`sql/schema.sql`](sql/schema.sql)

### How the Data is Realistic

Unlike toy datasets, I engineered realistic patterns:

**Churn Patterns:**
```python
# Free tier users churn at 15% monthly, Paid at 3%
CHURN_RATES = {'free': 0.15, 'starter': 0.08, 'professional': 0.03, 'enterprise': 0.01}
churn_probability = 1 - (1 - CHURN_RATES[tier]) ** months_since_signup
```

**Power User Distribution:**
```python
# 80/20 rule: 20% of users drive 80% of activity
user_type = np.random.choice(['power_user', 'regular', 'casual'], p=[0.20, 0.50, 0.30])
```

**Feature Discovery Friction:**
```python
# Premium features have low discoverability — Time Tracking only found by 12%
days_until_discovery = int(np.random.gamma(shape=2, scale=20))
```

**See full data generation logic:** [`python/data_generation.py`](python/data_generation.py)

---

## 🚀 How to Run This Project Locally

### Prerequisites
- Python 3.9+
- Git

### Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/SuharshSuresh/taskflow-analytics.git
cd taskflow-analytics

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Generate the synthetic data (creates all CSV files)
python python/data_generation.py

# 4. Run A/B test analysis
python python/ab_test_analysis.py

# 5. Launch the Streamlit dashboard
streamlit run dashboard/streamlit_app.py
```

The dashboard will open at `http://localhost:8501`

---

## 📁 Project Structure

```
taskflow-analytics/
├── README.md                          # You are here
├── requirements.txt
│
├── data/                              # All synthetic datasets
│   ├── README.md                      # Schema documentation
│   ├── users.csv
│   ├── events.csv
│   ├── onboarding_funnel.csv
│   ├── feature_usage.csv
│   ├── subscriptions.csv
│   ├── ab_test_assignments.csv
│   └── user_activity_summary.csv
│
├── sql/                               # Production-quality SQL queries
│   ├── schema.sql                     # PostgreSQL table definitions
│   ├── 01_power_feature_paradox.sql
│   ├── 02_onboarding_cliff.sql
│   ├── 03_undermonetized_segments.sql
│   ├── 04_cohort_retention.sql
│   └── 05_ab_test_extraction.sql
│
├── python/                            # Data generation & analysis
│   ├── data_generation.py
│   └── ab_test_analysis.py
│
├── dashboard/                         # Interactive Streamlit app
│   ├── streamlit_app.py
│   └── README.md
│
└── docs/                              # Additional documentation
    ├── business_context.md
    ├── sql_showcase.md
    └── insights_summary.md
```

---

## 🎓 What This Project Demonstrates

✅ **Think Like a Product Manager**  
- Defined business metrics (activation, retention, MRR)
- Identified pain points proactively (not waiting for stakeholders)
- Framed analysis around business outcomes, not just data exploration

✅ **Execute Technical Analysis**  
- Wrote production-quality SQL with proper CTEs, window functions, and business logic
- Ran statistical tests with appropriate sample sizes and significance levels
- Generated realistic synthetic data with proper distributions and edge cases

✅ **Influence Product Decisions**  
- Built a prioritization framework based on data
- Translated insights into concrete recommendations with ROI estimates
- Created monitoring frameworks to track success metrics

✅ **Communicate Across Functions**  
- Executive-friendly dashboard with KPIs and alerts
- Technical documentation for data teams (schema, query explanations)
- Business documentation for product teams (insights, recommendations)

---

## 📧 Contact

**Suharsha Suresh**  
🐙 [GitHub](https://github.com/SuharshSuresh)

---

## 📝 License

This is a portfolio project created for demonstration purposes. Data is synthetic and does not represent any real company.

---

**Built with ❤️ to demonstrate real-world Product Analytics skills**
