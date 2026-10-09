cat > d10_notes.md << 'EOF'
# D10 时序数据建模笔记

## 实测数据（10 万行，WSL2 本机）
| 写入方式 | 耗时 | 场景 |
|---|---|---|
| 逐行 INSERT | 几十秒（估） | 少量/交互 |
| INSERT...SELECT | 152 ms | 库内迁移 |
| COPY 导入 | 160 ms | 文件批量入库 |

## 关键结论
- 批量写入比逐行快 2 个数量级：攒批再写，绝不逐行 INSERT
- 分区裁剪：查询 10 月数据只扫 p2026_10 分区（EXPLAIN 验证）
- 分区表主键必须含分区键（ts）
- 超出分区范围的数据被拒收（no partition found）
- date_trunc 时间桶 ≈ TimescaleDB time_bucket；avg=24.95 与生成逻辑自洽

## 口述能力
时序表按月 RANGE 分区 + COPY 批量入库 + date_trunc 时间桶聚合，
为「多源数据采集与处理平台」的量级设计。

