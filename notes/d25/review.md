# D25 · 工作流编排与调度（2026-10-10）

## 一、定时任务三件套
- cron: 系统级定时（表达式: 分 时 日 月 周）
- APScheduler: Python 进程内调度（CronTrigger/IntervalTrigger, misfire_grace_time 错过补偿, coalesce 积压合并）
- Celery beat: 分布式任务队列的定时器（配合 worker 执行）

## 二、工作流编排核心概念
- 状态机: 显式状态 + 转移条件（IDLE→RUNNING_A→(重试自环)→RUNNING_B→SUCCESS/FAILED）
- DAG: 有向无环图——任务为节点, 依赖为边, 无环保证不循环
- ★ 依赖语义: B 依赖 A = A 成功才允许 B 执行

## 三、Airflow 简介
- 核心: DAG 定义 + Scheduler 调度 + Executor 执行 + Web UI 监控
- 能力: 依赖/重试/回填/时区/告警

## 四、实测
- d25_scheduler.py: APScheduler cron 每小时跑流水线
  → 手动触发验证: 生产 7437 条/秒 + 消费 999/入库 962/死信 37
- d25_state_machine.py: A 前 2 次失败自动重试 → 第 3 次成功 → 触发 B → SUCCESS(重试 2 次)

## 五、轻量 vs Airflow 取舍（问题）
APScheduler+状态机: 单机/轻量/快落地/零运维
Airflow: DAG 声明式/分布式/Web UI/重试回填内置/重但全
判断标准: 任务复杂度是否值得引入调度平台运维成本

## 六、与智能体编排的关联
Agent 可以作为工作流中的一个步骤（节点）——
D24 的 LangGraph 本身就是"图编排"，与 Airflow DAG 同构:
LangGraph=LLM 节点编排, Airflow=数据任务编排
