# D16 · Python 生产消费实战（2026-10-10）

## 一、Producer 要点
- KafkaProducer(bootstrap_servers, acks="all", retries=3, value_serializer)
- send() 异步返回 future → future.get(timeout) 同步等确认
- flush() 清空发送队列（退出前必调）
- key 哈希路由：同 key 同分区（顺序保证）；kafka-python 3.x 公式 = murmur2(key) & 0x7fffffff % 分区数
- ⚠️ 实测：sensor-00/01/02 三个 key 恰好都映射分区 0 = 哈希碰撞 → 数据倾斜真实存在
- ⚠️ kafka-python 3.x 分区器接口变了：对象 .partition() 方法，不是 2.x 函数
- ⚠️ kafka-python 3.x serializer 需实现 Deserializer 类（lambda 有 DeprecationWarning）

## 二、Consumer 要点
- KafkaConsumer(topic, group_id, enable_auto_commit=False, auto_offset_reset="earliest")
- enable_auto_commit=False → 手动 commit()：处理一条提交一条 = 至少一次
- 崩溃演示：处理完没提交就挂 → 重启重复消费那一条（铁证）
- 容错：消息格式不统一（历史文本）→ json 解析失败标记 unparsed，不炸进程

## 三、三种语义 + 幂等（面试）
| 语义 | 策略 | 结果 | 场景 |
|---|---|---|---|
| 至多一次 | 先提交后处理 | 可能丢 | 日志统计 |
| 至少一次 | 先处理再提交 | 不丢可能重复 | Kafka 默认 |
| 精确一次 | 事务+幂等 | 不丢不重 | 金融扣款 |
- 幂等：重复处理结果相同（upsert 按主键）

## 四、实操数据
- topic sensor-events（3 分区）；producer 发 10 条 JSON（全落分区0=碰撞）
- crash-group：从头读，第 3 条崩溃未提交 → 重启 [0:2] 重复消费 → 至少一次验证 ✅

## 五、命令/脚本
- kafka_producer.py（模拟 3 设备上报 10 条，key=设备号）
- kafka_consumer.py [崩溃点] [组名]（手动提交 + 崩溃模拟 + 容错反序列化）
