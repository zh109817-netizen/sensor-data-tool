"""D17: 模拟 20 台设备批量上报 1000 条到 Kafka（含 5% 脏数据供清洗演示）"""
import json
import random
import time
from kafka import KafkaProducer

N_DEVICES = 20
N_PER_DEVICE = 50

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    acks="all",
    retries=3,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

t0 = time.perf_counter()
total = 0
base = time.time()
for dev in range(N_DEVICES):
    device = f"sensor-{dev:02d}"
    for j in range(N_PER_DEVICE):
        ts = time.strftime("%Y-%m-%d %H:%M:%S",
                           time.localtime(base + dev * 100 + j))  # 每设备时间错开（主键唯一）
        if random.random() < 0.05:          # 5% 脏数据：越界/负值（供清洗）
            value = random.uniform(-5, 500)
        else:
            value = round(random.uniform(20, 30), 2)
        producer.send("sensor-events", key=device.encode(),
                      value={"device_id": device, "ts": ts, "value": value})
        total += 1
producer.flush()
dt = time.perf_counter() - t0
print(f"生产 {total} 条，耗时 {dt:.3f}s，吞吐 {total/dt:.0f} 条/秒")
