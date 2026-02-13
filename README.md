# TaskFlow Analytics Command Center

This repository contains a complete **Product Analytics Portfolio Project** for a Series D SaaS company, "TaskFlow".

## Project Overview
We analyzed user behavior, onboarding funnels, and feature adoption to drive product roadmap decisions.

### Key Components:
1.  **Data Generation**: Synthetic data for 10,000 users and 2M+ events (`python/data_generation.py`).
2.  **SQL Analysis**: Advanced queries for retention, cohorts, and power user identification (`sql/`).
3.  **A/B Testing**: Statistical analysis of a "Simplified Onboarding" experiment (`python/ab_test_analysis.py`).
4.  **Dashboard**: Interactive Streamlit app for executive reporting (`dashboard/streamlit_app.py`).

## How to Run

### Prerequisites
*   Python 3.8+
*   Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Steps
1.  **Generate Data**:
    ```bash
    python python/data_generation.py
    ```
    *(This creates CSV files in `data/`)*

2.  **Run Dashboard**:
    ```bash
    streamlit run dashboard/streamlit_app.py
    ```
    *(Opens in your browser at http://localhost:8501)*

3.  **Run A/B Test Analysis**:
    ```bash
    python python/ab_test_analysis.py
    ```

## Key Insights
*   **Onboarding Friction**: Step 3 (Board Creation) has a 36% drop-off.
*   **A/B Test Success**: The new 3-step onboarding improved completion by **12%** (Statistically Significant).
*   **Power Feature**: "Time Tracking" has low adoption (12%) but correlates with **3.9x higher retention**.

## Structure
```
.
├── data/               # Generated CSVs
├── sql/                # SQL Analysis queries
├── python/             # Python scripts
├── dashboard/          # Streamlit app
└── docs/               # Documentation
```
