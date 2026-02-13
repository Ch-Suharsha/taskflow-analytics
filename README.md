# 🚀 TaskFlow Analytics Command Center
### *A Product Analytics Portfolio Project*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://taskflow-analytics-suharsha.streamlit.app)
**[👉 View Live Dashboard](https://taskflow-analytics-suharsha.streamlit.app)**

---

## 📖 The "Why" Behind This Project
**Recruiter/Hiring Manager:** If you're reading this, you probably want to know if I can actually *do the job*.

I built this project to simulate the **real-world day-to-day work** of a Product Data Analyst. Instead of just cleaning a clean dataset, I wanted to tackle a full-stack analytics problem: 
1.  **Thinking like a PM**: Defining business metrics and hypotheses.
2.  **Engineering the Data**: Generating realistic raw logs (churn patterns, feature usage, A/B tests).
3.  **Analyzing with SQL**: Writing complex queries to find "hidden" insights.
4.  **proving Value**: Running statistical tests to validate product changes.
5.  **Influencing Strategy**: Building a dashboard to tell a story to stakeholders.

This isn't just code—it's a **Product Health Check** for a Series D SaaS company.

---

## 💼 The Business Scenario
**Company**: "TaskFlow" (A fictional B2B Project Management SaaS, similar to Asana/Monday).
**Stage**: Series D | $50M ARR | 15k Workspaces.
**The Problem**: Growth is slowing. The Head of Product needs to know:
> *"Why are users dropping off during onboarding? And what feature should we build next to drive retention?"*

---

## 🕵️ My Approach & Solutions

### 1. The "Onboarding Cliff" Investigation
**The Hypothesis**: Users are overwhelmed by the 4-step setup process.
*   **Analysis**: I wrote a funnel analysis query (`sql/02_onboarding_cliff_analysis.sql`) and found a **36% drop-off** at Step 3 (Board Creation).
*   **Action**: Modeled a "Simplified Onboarding" experiment (A/B Test).

### 2. The A/B Test (Statistical Validation)
**The Experiment**: Reducing onboarding from 4 steps to 3.
*   **Result**: 
    *   **Control (Original)**: 35% Completion Rate.
    *   **Variant (New)**: 47% Completion Rate.
*   **Validation**: Performed Chi-Square test in Python (`python/ab_test_analysis.py`).
*   **Outcome**: **P-Value < 0.05**. The result is statistically significant.
*   **Business Impact**: Estimated **+$280k ARR** lift from improved activation.

### 3. The "Hidden Gem" Discovery
**The Insight**: 
*   Most users focus on "Kanban Boards".
*   *However*, my retention analysis (`sql/01_power_feature_paradox.sql`) revealed that users who find **"Time Tracking"** retention **3.9x longer**.
*   **The Problem**: Only 12% of users discover Time Tracking.
*   **Strategic Recommendation**: Move Time Tracking to the main navigation to drive discovery and retention.

---

## 🛠️ Technical Implementation

### The Stack
*   **Python**: For data generation & statistical analysis (Pandas, NumPy, SciPy).
*   **SQL (PostgreSQL dialect)**: For core business logic and data extraction.
*   **Streamlit**: For the interactive executive dashboard.
*   **Git/GitHub**: For version control and deployment.

### Key Files
*   `dashboard/streamlit_app.py`: The code powering the **[Live Dashboard](https://taskflow-analytics-suharsha.streamlit.app)**.
*   `sql/`: Contains 5 production-grade SQL queries answering specific business questions.
*   `python/data_generation.py`: The script I wrote to generate 2M+ rows of realistic synthetic data (simulating churn, power users, and funnel drop-offs).

---

## 🧪 How to Run Locally

If you want to poke around the code yourself:

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/Ch-Suharsha/taskflow-analytics.git
    cd taskflow-analytics
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Generate the Data** (Simulates the raw database):
    ```bash
    python python/data_generation.py
    ```

4.  **Run the Dashboard**:
    ```bash
    streamlit run dashboard/streamlit_app.py
    ```

---

## 🎤 Final Thought
Data analysis isn't just about writing code—it's about **making better decisions**. 

This project demonstrates my ability to take raw, messy goals ("fix retention"), translate them into technical requirements, and deliver actionable insights that drive revenue.

**I am ready to bring this same rigorous, product-focused mindset to your team.**
