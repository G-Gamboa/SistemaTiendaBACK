CREATE TABLE IF NOT EXISTS cash_inventory (
    denomination NUMERIC      NOT NULL PRIMARY KEY,
    quantity     INTEGER      NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions_log (
    id               SERIAL          PRIMARY KEY,
    transaction_type VARCHAR(50)     NOT NULL,
    sale_amount      NUMERIC(10, 2),
    received_amount  NUMERIC(10, 2),
    change_amount    NUMERIC(10, 2),
    money_in         JSONB           NOT NULL DEFAULT '{}',
    money_out        JSONB           NOT NULL DEFAULT '{}',
    notes            TEXT            NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
