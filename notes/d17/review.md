# D17 · 流式数据处理全链路（2026-10-10）

## 一、流水线架构（4 段）
模拟设备(20台×50条) → Kafka(sensor-events,3分区) → 清洗消费者(pipeline-group) → PostgreSQL(sensor_events_part 按月分区)

## 二、实测数据
- 生产：1000 条 / 0.151s / **6623 条/秒**
- 消费清洗：1033 条 → 入库 963 / 死信 70（5% 脏数据 + 历史非 JSON）
- 入库吞吐：**106 条/秒**（瓶颈！比生产慢 60×）
- PG 落库：959 行（963 尝试 - 4 重复被 ON CONFLICT 去重 = 幂等生效铁证）

## 三、每段可靠性（问题）
| 段 | 保障 | 防什么 |
|---|---|---|
| 生产 | acks=all + retries | 生产丢消息 |
| Kafka | 分区副本 + offset 持久化 | 宕机/断点丢失 |
| 清洗 | 手动提交(至少一次) + 死信 + 幂等 | 崩溃丢消息/脏数据 |
| 入库 | 批量 executemany + ON CONFLICT + 分区裁剪 | 写库慢/重复/查询慢 |

## 四、坑清单（本轮实测）
1. 消费者 join group 由 poll() 驱动——assignment() 不触发网络请求，等 rebalance 必须 poll
2. 新组第一次 poll 必空（协调期）→ 连续 3 次空 poll 才算消费完
3. PG round(double, int) 不存在 → 需 ::numeric 转型
4. psycopg 连接端口 = compose 映射的宿主机端口（5433→容器 5432）

## 五、脚本
- pipeline_producer.py（20 设备×50 条，5% 脏数据，key 哈希）
- pipeline_consumer.py（poll 驱动 + 清洗规则 + 批量 500 + 死信 + 幂等）
