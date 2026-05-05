CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS readings (
    ts    TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    topic TEXT             NOT NULL,
    value DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('readings', 'ts', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS readings_topic_ts_idx ON readings (topic, ts DESC);

CREATE OR REPLACE FUNCTION notify_new_reading()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('new_reading', row_to_json(NEW)::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS readings_notify ON readings;
CREATE TRIGGER readings_notify
AFTER INSERT ON readings
FOR EACH ROW EXECUTE FUNCTION notify_new_reading();
