-- ============================================================
-- schema.sql
-- Reference SQL schema (SQLite dialect) matching database/models.py.
-- SQLAlchemy's create_all() generates this automatically at runtime;
-- keep this file in sync for manual inspection, migrations tooling,
-- or porting to Postgres/MySQL later.
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS careers (
    id              TEXT PRIMARY KEY,
    title           TEXT UNIQUE NOT NULL,
    description     TEXT,
    average_salary  REAL,
    growth_outlook  TEXT
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id                 TEXT PRIMARY KEY,
    email              TEXT UNIQUE NOT NULL,
    full_name          TEXT NOT NULL,
    hashed_password    TEXT NOT NULL,
    bio                TEXT,
    avatar_url         TEXT,
    experience_level   TEXT DEFAULT 'beginner',
    target_career_id   TEXT REFERENCES careers(id),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id           TEXT PRIMARY KEY,
    name         TEXT UNIQUE NOT NULL,
    category     TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS user_skills (
    id             TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    skill_id       TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency    REAL DEFAULT 0.0,
    verified       BOOLEAN DEFAULT 0,
    last_practiced TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS career_skills (
    id                     TEXT PRIMARY KEY,
    career_id              TEXT NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    skill_id               TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    required_proficiency   REAL DEFAULT 70.0,
    weight                 REAL DEFAULT 1.0,
    UNIQUE (career_id, skill_id)
);

CREATE TABLE IF NOT EXISTS career_missions (
    id           TEXT PRIMARY KEY,
    career_id    TEXT NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS roadmaps (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    career_id     TEXT NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    step_order    INTEGER NOT NULL,
    title         TEXT NOT NULL,
    description   TEXT,
    resource_type TEXT,
    resource_id   TEXT,
    status        TEXT DEFAULT 'locked',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_progress (
    id               TEXT PRIMARY KEY,
    user_id          TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    skill_id         TEXT REFERENCES skills(id),
    roadmap_step_id  TEXT REFERENCES roadmaps(id),
    progress_percent REAL DEFAULT 0.0,
    notes            TEXT,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenges (
    id                 TEXT PRIMARY KEY,
    title              TEXT NOT NULL,
    skill_id           TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    difficulty         TEXT DEFAULT 'practice' CHECK (difficulty IN ('prerequisite','practice','advanced')),
    prompt             TEXT NOT NULL,
    solution_criteria  TEXT,   -- JSON encoded
    max_score          REAL DEFAULT 100.0
);

CREATE TABLE IF NOT EXISTS challenge_attempts (
    id                          TEXT PRIMARY KEY,
    user_id                     TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    challenge_id                TEXT NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    submitted_answer            TEXT,
    score                       REAL DEFAULT 0.0,
    passed                      BOOLEAN DEFAULT 0,
    next_recommended_difficulty TEXT,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id               TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    career_id        TEXT REFERENCES careers(id),
    description      TEXT NOT NULL,
    required_skills  TEXT,  -- JSON encoded list of skill ids
    difficulty       TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS project_submissions (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    project_id  TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    repo_url    TEXT,
    file_path   TEXT,
    status      TEXT DEFAULT 'submitted',
    feedback    TEXT,
    score       REAL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS career_simulations (
    id             TEXT PRIMARY KEY,
    career_id      TEXT NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    scenario       TEXT NOT NULL,
    decision_tree  TEXT  -- JSON encoded
);

CREATE TABLE IF NOT EXISTS simulation_attempts (
    id             TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    simulation_id  TEXT NOT NULL REFERENCES career_simulations(id) ON DELETE CASCADE,
    choices_made   TEXT,  -- JSON encoded
    outcome_score  REAL DEFAULT 0.0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessments (
    id         TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    career_id  TEXT REFERENCES careers(id),
    questions  TEXT NOT NULL  -- JSON encoded
);

CREATE TABLE IF NOT EXISTS assessment_attempts (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    assessment_id   TEXT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    answers         TEXT,  -- JSON encoded
    score           REAL DEFAULT 0.0,
    result_summary  TEXT,  -- JSON encoded
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS achievements (
    id           TEXT PRIMARY KEY,
    title        TEXT UNIQUE NOT NULL,
    description  TEXT,
    icon         TEXT,
    criteria     TEXT  -- JSON encoded
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id             TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    achievement_id TEXT NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id                     TEXT PRIMARY KEY,
    user_id                TEXT UNIQUE NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    headline               TEXT,
    summary                TEXT,
    featured_projects      TEXT,  -- JSON encoded
    featured_achievements  TEXT,  -- JSON encoded
    public_slug            TEXT UNIQUE,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_missions (
    id             TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    date           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title          TEXT NOT NULL,
    description    TEXT,
    resource_type  TEXT,
    resource_id    TEXT,
    completed      BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS career_readiness (
    id                 TEXT PRIMARY KEY,
    user_id            TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    career_id          TEXT NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    readiness_percent  REAL DEFAULT 0.0,
    skill_gap_summary  TEXT,  -- JSON encoded
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helpful indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_user_skills_user      ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_career_skills_career   ON career_skills(career_id);
CREATE INDEX IF NOT EXISTS idx_roadmaps_user_career   ON roadmaps(user_id, career_id);
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_usr ON challenge_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_readiness_user_career  ON career_readiness(user_id, career_id);
