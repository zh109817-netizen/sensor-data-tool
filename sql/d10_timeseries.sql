
-- D10 时序数据建模：分区表 + 批量写入 + 时间桶聚合
-- 首次运行（已存在会报错）；在 sensor_db 库中执行

-- 1. 分区父表（主键必须含分区键 ts）
CREATE TABLE sensor_readings_part (
    device_id TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (device_id, ts)
) PARTITION BY RANGE (ts);

-- 2. 按月分区（边界左闭右开）
CREATE TABLE sensor_readings_part_p2026_07 PARTITION OF sensor_readings_part
FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE sensor_readings_part_p2026_08 PARTITION OF sensor_readings_part
FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE sensor_readings_part_p2026_09 PARTITION OF sensor_readings_part
FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE sensor_readings_part_p2026_10 PARTITION OF sensor_readings_part
FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE sensor_readings_part_p2026_11 PARTITION OF sensor_readings_part
FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

-- 3. 批量写入：INSERT...SELECT 10 万行（实测 152ms）
INSERT INTO sensor_readings_part (device_id, ts, value)
SELECT device_id, ts, value FROM sensor_readings;

-- 4. 批量写入：COPY 导出 / 导入（实测 14.9ms 导出 / 160ms 导入）
-- COPY sensor_readings TO '/tmp/sensor_dump.csv' WITH (FORMAT csv, HEADER);
-- COPY sensor_readings_part (device_id, ts, value)
--      FROM '/tmp/sensor_dump.csv' WITH (FORMAT csv, HEADER);

-- 5. 时间桶聚合：小时桶 / 15 分钟桶（date_trunc 手动实现 time_bucket）
SELECT date_trunc('hour', ts) AS bucket,
       COUNT(*) AS cnt, AVG(value) AS avg_v
FROM sensor_readings GROUP BY bucket ORDER BY bucket;

SELECT date_trunc('hour', ts) + (EXTRACT(MINUTE FROM ts)::int / 15) * INTERVAL '15 min' AS bucket,
       COUNT(*) AS cnt, AVG(value) AS avg_v
FROM sensor_readings GROUP BY bucket ORDER BY bucket;

