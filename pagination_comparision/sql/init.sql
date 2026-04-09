CREATE TABLE IF NOT EXISTS items (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_items_created_at_id_desc
ON items (created_at DESC, id DESC);
