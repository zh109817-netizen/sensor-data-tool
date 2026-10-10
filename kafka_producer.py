
"""D16: 模拟设备上报数据 -> Kafka（默认分区器：key 哈希路由）"""
import json
import random
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    acks="all",
    retries=3,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

for i in range(10):
    device = f"sensor-{i % 3:02d}"
    msg = {
        "device_id": device,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "value": round(random.uniform(20, 30), 2),
    }
    future = producer.send("sensor-events", key=device.encode(), value=msg)
    result = future.get(timeout=5)
    print(f"已发送: {msg} -> partition={result.partition} offset={result.offset}")
    time.sleep(0.2)
producer.flush()
print("完成")


