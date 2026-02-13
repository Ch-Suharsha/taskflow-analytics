/*
=================================================================
TASKFLOW ANALYTICS - DATABASE SCHEMA
=================================================================
PostgreSQL table definitions for all 7 data tables.
These tables represent a realistic SaaS analytics database.
=================================================================
*/

-- Users: core user account data
CREATE TABLE users (
    user_id         VARCHAR(10) PRIMARY KEY,
    workspace_id    VARCHAR(10) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    signup_date     TIMESTAMP NOT NULL,
    account_tier    VARCHAR(20) NOT NULL CHECK (account_tier IN ('free', 'starter', 'professional', 'enterprise')),
    user_role       VARCHAR(20) NOT NULL CHECK (user_role IN ('owner', 'admin', 'member', 'guest')),
    industry        VARCHAR(50),
    team_size       INTEGER,
    signup_source   VARCHAR(20) CHECK (signup_source IN ('organic', 'paid_search', 'referral', 'sales')),
    country         VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,
    last_login_date TIMESTAMP
);

-- User Activity Summary: pre-aggregated engagement metrics per user
CREATE TABLE user_activity_summary (
    user_id                 VARCHAR(10) PRIMARY KEY REFERENCES users(user_id),
    workspace_id            VARCHAR(10) NOT NULL,
    signup_date             DATE NOT NULL,
    days_since_signup       INTEGER,
    total_sessions          INTEGER DEFAULT 0,
    total_events            INTEGER DEFAULT 0,
    avg_session_duration_min DECIMAL(5,1),
    tasks_created           INTEGER DEFAULT 0,
    tasks_completed         INTEGER DEFAULT 0,
    boards_created          INTEGER DEFAULT 0,
    premium_features_used   INTEGER DEFAULT 0,
    last_active_date        DATE,
    is_power_user           BOOLEAN DEFAULT FALSE,
    is_at_risk_churn        BOOLEAN DEFAULT FALSE,
    cohort_month            VARCHAR(7)
);

-- Onboarding Funnel: step-by-step onboarding tracking
CREATE TABLE onboarding_funnel (
    user_id                     VARCHAR(10) PRIMARY KEY REFERENCES users(user_id),
    step_1_completed            BOOLEAN DEFAULT FALSE,
    step_1_timestamp            TIMESTAMP,
    step_2_completed            BOOLEAN DEFAULT FALSE,
    step_2_timestamp            TIMESTAMP,
    step_3_completed            BOOLEAN DEFAULT FALSE,
    step_3_timestamp            TIMESTAMP,
    step_4_completed            BOOLEAN DEFAULT FALSE,
    step_4_timestamp            TIMESTAMP,
    onboarding_completed        BOOLEAN DEFAULT FALSE,
    onboarding_completion_date  TIMESTAMP,
    time_to_complete_hours      DECIMAL(8,2),
    ab_test_variant             VARCHAR(20)
);

-- Feature Usage: tracks when users discover and use features
CREATE TABLE feature_usage (
    usage_id                        VARCHAR(20) PRIMARY KEY,
    user_id                         VARCHAR(10) NOT NULL REFERENCES users(user_id),
    feature_name                    VARCHAR(50) NOT NULL,
    first_used_date                 TIMESTAMP,
    total_usage_count               INTEGER DEFAULT 0,
    last_used_date                  TIMESTAMP,
    days_since_signup_at_first_use  INTEGER
);

-- Subscriptions: workspace-level billing and churn data
CREATE TABLE subscriptions (
    subscription_id VARCHAR(12) PRIMARY KEY,
    workspace_id    VARCHAR(10) NOT NULL,
    plan_type       VARCHAR(20) NOT NULL CHECK (plan_type IN ('free', 'starter', 'professional', 'enterprise')),
    mrr             DECIMAL(10,2) DEFAULT 0,
    start_date      TIMESTAMP NOT NULL,
    end_date        TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    churn_date      TIMESTAMP,
    churn_reason    VARCHAR(50)
);

-- A/B Test Assignments: experiment tracking
CREATE TABLE ab_test_assignments (
    user_id         VARCHAR(10) PRIMARY KEY REFERENCES users(user_id),
    test_name       VARCHAR(100) NOT NULL,
    variant         VARCHAR(20) NOT NULL CHECK (variant IN ('control', 'variant_a')),
    assignment_date TIMESTAMP NOT NULL,
    converted       BOOLEAN DEFAULT FALSE,
    conversion_date TIMESTAMP
);

-- Events: behavioral event stream
CREATE TABLE events (
    event_id        VARCHAR(20) PRIMARY KEY,
    user_id         VARCHAR(10) NOT NULL REFERENCES users(user_id),
    event_name      VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    session_id      VARCHAR(20),
    properties      JSONB DEFAULT '{}'
);

-- Indexes for common query patterns
CREATE INDEX idx_users_workspace ON users(workspace_id);
CREATE INDEX idx_users_tier ON users(account_tier);
CREATE INDEX idx_users_signup ON users(signup_date);
CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_name ON events(event_name);
CREATE INDEX idx_events_timestamp ON events(event_timestamp);
CREATE INDEX idx_feature_usage_user ON feature_usage(user_id);
CREATE INDEX idx_feature_usage_name ON feature_usage(feature_name);
CREATE INDEX idx_subscriptions_workspace ON subscriptions(workspace_id);
CREATE INDEX idx_activity_workspace ON user_activity_summary(workspace_id);
