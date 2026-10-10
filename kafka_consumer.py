
"""D16: 消费 sensor-events 落盘；手动提交 offset；支持模拟崩溃"""
import json
import os
import sys
from kafka import KafkaConsumer
from kafka.serializer import Deserializer

GROUP = sys.argv[2] if len(sys.argv) > 2 else "py-consumers"
TOPIC = "sensor-events"
OUT = "consumed.jsonl"
CRASH_AFTER = int(sys.argv[1]) if len(sys.argv) > 1 else 999

class JsonDeserializer(Deserializer):
    """容错反序列化：JSON 正常解析；非 JSON（历史消息）标记 raw，不炸进程"""
    def deserialize(self, topic, headers, data):
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return {"raw": data.decode("utf-8", "replace"), "unparsed": True}

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id=GROUP,
    enable_auto_commit=False,
    auto_offset_reset="earliest",
    value_deserializer=JsonDeserializer(),   # 类实现（消警告 + 容错）
)

print(f"开始消费（处理到第 {CRASH_AFTER} 条后崩溃）...")
with open(OUT, "a", encoding="utf-8") as f:
    count = 0
    for msg in consumer:
        data = msg.value
        print(f"[{msg.partition}:{msg.offset}] {data}")
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
        f.flush()
        count += 1
        if count == CRASH_AFTER:
            print(f"💥 模拟崩溃：处理完第 {count} 条，还没提交 offset")
            os._exit(1)
        consumer.commit()
