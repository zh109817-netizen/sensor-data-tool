
"""D17: 消费 -> 清洗 -> 批量写 PostgreSQL 分区表（等 rebalance + 连续空 poll 退出）"""
import json
import os
import time
from kafka import KafkaConsumer
from kafka.serializer import Deserializer
import psycopg

GROUP = "pipeline-group"
TOPIC = "sensor-events"
BATCH = 500
DLQ_FILE = "dlq/dead_letter.jsonl"
os.makedirs("dlq", exist_ok=True)

class JsonDeserializer(Deserializer):
    def deserialize(self, topic, headers, data):
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return {"unparsed": True, "raw": data.decode("utf-8", "replace")}

consumer = KafkaConsumer(
    TOPIC, bootstrap_servers="localhost:9092", group_id=GROUP,
    enable_auto_commit=False, auto_offset_reset="earliest",
    value_deserializer=JsonDeserializer(),
)

print("触发 rebalance（poll 驱动组加入）...")
while True:
    consumer.poll(timeout_ms=1000, max_records=1)   # ① poll 才发 JoinGroup 请求
    if consumer.assignment():                       # ② 分配完成
        break
    time.sleep(0.2)
print("已分配分区:", sorted(tp.partition for tp in consumer.assignment()))

def clean(msg):
    if msg.get("unparsed"):
        return False, "非 JSON"
    device = msg.get("device_id")
    ts = msg.get("ts")
    value = msg.get("value")
    if device is None:
        return False, "缺 device_id"
    if value is None:
        return False, "缺 value"
    if ts is None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, f"value 非数值: {value}"
    if not (0 <= value <= 100):
        return False, f"value 越界: {value}"
    return True, (device, ts, value)

conn = psycopg.connect("host=localhost port=5433 dbname=sensor_db user=postgres password=postgres")
t0 = time.perf_counter()
buffer, dlq_n, ok_n, seen = [], 0, 0, 0

def flush_batch():
    global buffer, ok_n
    if not buffer:
        return
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO sensor_events_part (device_id, ts, value) "
            "VALUES (%s, %s, %s) ON CONFLICT (device_id, ts) DO NOTHING",
            buffer,
        )
    conn.commit()
    ok_n += len(buffer)
    buffer = []

print("开始消费（连续 3 次空 poll 自动结束）...")
empty_polls = 0
with open(DLQ_FILE, "a", encoding="utf-8") as dlq:
    while True:
        records = consumer.poll(timeout_ms=3000, max_records=1000)
        if not records:
            empty_polls += 1
            if empty_polls >= 3:          # ② 连续 3 次空才算消费完
                break
            continue
        empty_polls = 0
        for tp, msgs in records.items():
            for msg in msgs:
                seen += 1
                ok, row = clean(msg.value)
                if not ok:
                    dlq.write(json.dumps({"reason": row, "msg": msg.value}, ensure_ascii=False) + "\n")
                    dlq_n += 1
                else:
                    buffer.append(row)
                if len(buffer) >= BATCH:
                    flush_batch()
        consumer.commit()

flush_batch()
dt = time.perf_counter() - t0
print(f"消费 {seen} 条 | 入库 {ok_n} | 死信 {dlq_n} | 耗时 {dt:.2f}s | 入库吞吐 {ok_n/dt:.0f} 条/秒")
conn.close()
