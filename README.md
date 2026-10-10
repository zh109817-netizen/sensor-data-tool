# sensor-data-tool · 传感器数据流水线与估计算法实战

> 求职demo · 算法与系统研发工程师方向
> 从零搭建的传感器数据**全链路**工程：采集 → 消息队列 → 流式清洗 → 时序入库 → 聚合分析 → 状态估计算法

---

## 项目亮点

| 模块 | 一句话 |
|---|---|
| **数据流水线** | 模拟设备上报 → Kafka 消息队列 → 流式清洗 → PostgreSQL 分区表 → 聚合查询 |
| **估计算法** | 手写 最小二乘 LS→加权最小二乘 WLS → 一维卡尔曼滤波 + 多传感器融合，全推导、可复现 |
| **工程素养** | Docker 容器化 / docker-compose 编排 / 数据卷与热更新 / 备份恢复 / 日志轮转 / git 版本管理 |

## 架构

```text
[模拟设备] ──► [Kafka (KRaft单节点, topic=sensor-events, 3分区)]
                   │
                   ▼
         [pipeline_consumer.py]  流式清洗（JSON解析、值域校验、死信队列）
                   │
                   ▼
      [PostgreSQL 18]  sensor_events_part（按 ts RANGE 分区，主键幂等去重）
                   │
                   ▼
          [聚合查询 / pandas 时序分析 / 状态估计]

