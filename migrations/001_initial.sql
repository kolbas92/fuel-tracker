CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    username    TEXT,
    first_name  TEXT NOT NULL,
    report_count INT NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE stations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    osm_id      BIGINT UNIQUE,
    name        TEXT NOT NULL,
    brand       TEXT,
    address     TEXT,
    location    GEOGRAPHY(Point, 4326) NOT NULL,
    added_by    BIGINT REFERENCES users(telegram_id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stations_location ON stations USING GIST(location);

CREATE TABLE reports (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id  UUID NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    user_id     BIGINT NOT NULL REFERENCES users(telegram_id),
    has_fuel    BOOLEAN NOT NULL,
    fuel_type   TEXT NOT NULL CHECK (fuel_type IN ('92', '95', '98', 'dt', 'gas')),
    price       NUMERIC(6, 2),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_station_time ON reports(station_id, created_at DESC);

CREATE VIEW station_status AS
SELECT
    station_id,
    fuel_type,
    COUNT(*) FILTER (WHERE has_fuel = true)  AS votes_yes,
    COUNT(*) FILTER (WHERE has_fuel = false) AS votes_no,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
    MAX(created_at) AS last_report
FROM reports
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY station_id, fuel_type;
