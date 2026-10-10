# D15 · Kafka 核心概念（第3周 第1天）

## 一、心智模型（快递物流中心类比）
| 概念 | 大白话 | 类比 |
|---|---|---|
| Kafka | 分布式消息流平台 | 物流中心 |
| topic | 消息分类 | 分拣通道 |
| partition | topic 切成 N 段并行 | 并行传送带 |
| offset | 分区内消息编号 | 快递单号 |
| consumer group | 组内分摊分区 | 流水线分拣员 |
| rebalance | 组员变动重新分配 | 重新排班 |
| acks | 确认级别 0/1/all | 寄件回执 |
| KRaft | 自管元数据（无 ZK） | 自带调度台 |

## 二、消息旅程（完成标准答案）
生产者 → 写 topic 某分区（有 key 哈希 / 无 key 粘性轮询）
→ broker 存盘（acks 定确认深度）→ 消费者 poll 主动拉
→ 按分区内 offset 顺序读 → 提交 offset 记账 → 下次从书签继续

## 三、消费三铁律
1. 消费者主动拉（pull），broker 不推送
2. 分区内有序，跨分区不保证全局顺序
3. 读了不删 → 不同组可各自重读（广播基础）

## 四、consumer group 四作用
1. 组内分摊并行（每条恰好一人处理，加人到 ≤分区数扩容）
2. 组间独立广播（多用途各读各的）
3. 每组独立 offset 记账
4. rebalance 自动重排（加人减人不停机）

## 五、命令卡（apache/kafka 镜像 bin 不在 PATH，需完整路径）
| 操作 | 命令 |
|---|---|
| 创建 topic | /opt/kafka/bin/kafka-topics.sh --create --topic sensor-events --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 |
| 查看详情 | ... --describe --topic sensor-events ... |
| 生产 | /opt/kafka/bin/kafka-console-producer.sh --topic sensor-events --bootstrap-server localhost:9092 |
| 消费(从头) | /opt/kafka/bin/kafka-console-consumer.sh --topic sensor-events --from-beginning --group group-a --bootstrap-server localhost:9092 |
| 查 offset | /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server localhost:9092 --topic sensor-events |
| 查组进度 | /opt/kafka/bin/kafka-consumer-groups.sh --describe --group group-a --bootstrap-server localhost:9092 |

## 六、实操结果（2026-10-10）
- Kafka 3.9.0 KRaft 单节点，容器 kafka，9092
- topic sensor-events：3 分区（0/1/2），ReplicationFactor 1
- 生产 11 条（2 轮），offset 档案：分区0=6 / 分区1=5 / 分区2=0（粘性分区不均）
- group-a 从头消费：CURRENT=END(6/5/0)、LAG=0、no active members（组退出但 offset 记住=断点续传）

## 七、坑清单
1. 镜像 CLI 不在 PATH → 必须 /opt/kafka/bin/ 完整路径
2. 生产者退出用 Ctrl+D（EOF 优雅刷出），^C 可能丢尾部消息
3. 无 key 消息粘性分区 → 分区不均属正常
4. 分区数创建后只能增不能减

## 八、问题 Q&A
Q: Kafka 为什么快？ A: 顺序写磁盘 + 分区并行 + 零拷贝 + 消费者主动拉
Q: 消息会丢吗？ A: acks=all + 副本同步后返回；消费端处理完提交 offset
Q: 顺序怎么保证？ A: 同一分区内按 offset 有序；跨分区不保证 → 关键业务用单分区或 key 路由
