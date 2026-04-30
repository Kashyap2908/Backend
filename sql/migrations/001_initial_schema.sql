-- ============================================================
-- Migration 001 — Initial schema for auth infrastructure
-- Run once against your PostgreSQL database.
-- Requires: pgcrypto extension (CREATE EXTENSION IF NOT EXISTS pgcrypto)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Password-reset tokens ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       TEXT        NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used        BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_prt_user UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS idx_prt_token ON password_reset_tokens (token);

-- ── Refresh tokens ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       TEXT        NOT NULL UNIQUE,
    branch_id   UUID,
    expires_at  TIMESTAMPTZ NOT NULL,
    is_revoked  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rt_token     ON refresh_tokens (token);
CREATE INDEX IF NOT EXISTS idx_rt_user_id   ON refresh_tokens (user_id);

-- ── Activity / Audit log ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_logs (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        REFERENCES users(id) ON DELETE SET NULL,
    branch_id   UUID,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id   UUID,
    details     JSONB,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partition-friendly indexes for dashboard / audit queries
CREATE INDEX IF NOT EXISTS idx_al_branch_id  ON activity_logs (branch_id);
CREATE INDEX IF NOT EXISTS idx_al_user_id    ON activity_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_al_action     ON activity_logs (action);
CREATE INDEX IF NOT EXISTS idx_al_created_at ON activity_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_al_entity     ON activity_logs (entity_type, entity_id);

-- ── Recommended indexes on the users table ───────────────────────────────────
-- (Run only if these don't already exist in your schema)
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email     ON users (email);
-- CREATE        INDEX IF NOT EXISTS idx_users_branch_id ON users (branch_id);
