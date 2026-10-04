CREATE TYPE account_type AS ENUM ('PEA', 'PEA_PME', 'PEA_JEUNE', 'CTO');
CREATE TYPE transaction_type AS ENUM ('DEPOSIT', 'WITHDRAWAL', 'BUY', 'SELL', 'DIVIDEND', 'FEE', 'TAX');

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type account_type NOT NULL,
    broker VARCHAR,
    opened_at DATE,
    label VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own accounts" ON accounts FOR ALL USING (auth.uid() = user_id);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    type transaction_type NOT NULL,
    isin VARCHAR,
    quantity NUMERIC,
    price NUMERIC,
    amount NUMERIC,
    fees NUMERIC,
    currency VARCHAR DEFAULT 'EUR',
    note TEXT,
    source VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own transactions" ON transactions FOR ALL USING (auth.uid() = user_id);

CREATE TABLE instruments (
    isin VARCHAR PRIMARY KEY,
    ticker VARCHAR,
    name VARCHAR,
    sector VARCHAR,
    country VARCHAR,
    currency VARCHAR DEFAULT 'EUR',
    asset_type VARCHAR,
    is_distributing BOOLEAN,
    ter NUMERIC,
    pea_eligible BOOLEAN,
    replication VARCHAR,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read instruments" ON instruments FOR SELECT USING (true);

CREATE TABLE prices_daily (
    isin VARCHAR REFERENCES instruments(isin) ON DELETE CASCADE,
    date DATE NOT NULL,
    close NUMERIC NOT NULL,
    PRIMARY KEY (isin, date)
);
ALTER TABLE prices_daily ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read prices_daily" ON prices_daily FOR SELECT USING (true);
