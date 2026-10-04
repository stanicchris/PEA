CREATE TABLE IF NOT EXISTS tax_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country TEXT NOT NULL,
    year INT NOT NULL,
    prélèvements_sociaux DECIMAL NOT NULL,
    impot_revenu DECIMAL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (country, year)
);

INSERT INTO tax_rules (country, year, prélèvements_sociaux, impot_revenu, description)
VALUES 
    ('FR', 2024, 0.172, 0.128, 'PFU 30%'),
    ('FR', 2025, 0.172, 0.128, 'PFU 30%'),
    ('FR', 2026, 0.186, 0.128, 'Prélèvements Sociaux 18.6%');
