-- ============================================================
-- CLOTHING BRAND ERP — FIXED SCHEMA (STABLE + DJANGO COMPATIBLE)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. BRANCHES & USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS branches (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name       TEXT NOT NULL,
    location   TEXT,
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id     UUID REFERENCES branches(id) ON DELETE SET NULL,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT CHECK (role IN ('admin','manager','cashier')), -- ✅ FIXED
    is_active     BOOLEAN DEFAULT TRUE,
    last_login    TIMESTAMP,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- ============================================================
-- AUTH TABLES (REQUIRED FOR DJANGO LOGIN)
-- ============================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. PARTIES
-- ============================================================

CREATE TABLE IF NOT EXISTS parties (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_name TEXT NOT NULL,
    party_type TEXT CHECK (party_type IN ('CUSTOMER', 'SUPPLIER')),
    phone      TEXT,
    email      TEXT,
    address    TEXT,
    gst_number TEXT,
    state_code CHAR(2),
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. ACTIVITY LOGS (🔥 FIXED)
-- ============================================================

CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    branch_id UUID,
    action TEXT,
    entity_type TEXT,
    entity_id UUID,
    details JSONB,  -- ✅ IMPORTANT FIX
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_branch_id ON activity_logs(branch_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- ============================================================
-- 4. PRODUCTS
-- ============================================================

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    sku TEXT UNIQUE,
    branch_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_branch_id ON products(branch_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- ============================================================
-- 5. STOCK
-- ============================================================

CREATE TABLE IF NOT EXISTS stock (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID,
    branch_id UUID,
    quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_product_id ON stock(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_branch_id ON stock(branch_id);

-- ============================================================
-- 6. INVOICES
-- ============================================================

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invoices_branch_id ON invoices(branch_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- ============================================================
-- 7. TRANSACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID,
    invoice_id UUID,
    amount NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_branch_id ON transactions(branch_id);
CREATE INDEX IF NOT EXISTS idx_transactions_invoice_id ON transactions(invoice_id);

-- ============================================================
-- 8. NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    branch_id UUID,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. ADMIN SEED (FIXED)
-- ============================================================

INSERT INTO users (id, name, email, password_hash, role)
VALUES (
    uuid_generate_v4(),
    'Admin',
    'admin@neurostock.local',
    crypt('Admin@123', gen_salt('bf')),
    'admin'
)
ON CONFLICT (email) DO NOTHING;