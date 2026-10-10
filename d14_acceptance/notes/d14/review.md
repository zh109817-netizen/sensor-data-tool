# D14 周末验收 · 第2周总检验（2026-10-10）

## 1. 从零起栈（d14_acceptance/docker-compose.yml）
- 服务：postgres:18（d14-pg）+ sensor-api（d14-api）+ adminer（d14-adminer）
- 端口：5434/8001/8081（避开旧栈）；卷 d14-data:/var/lib/postgresql
- healthcheck pg_isready + depends_on condition: service_healthy
- 三服务 restart: unless-stopped
- 坑：YAML 缩进层级——api/adminer 曾写成 postgres 子字段（4 空格 vs 2 空格）

## 2. EXPLAIN 优化前后对比（sensor_readings 10 万行）
| 阶段 | 执行计划 | Execution Time |
|---|---|---|
| 优化前 | Seq Scan | 2.280 ms |
| 优化后 | Index Scan (idx_sensor_value) | 0.024 ms |
| 加速比 | ~95× | |

## 3. 持久化验证（待记录）
## 4. 健康检查验证（待记录）

## 3. 持久化验证 ✅
- 写入 100000 行 → docker compose down → up → COUNT 仍为 100000
- 结论：卷 d14-data 持久化生效（容器删了数据在）

## 4. 健康检查验证 ✅
- docker exec d14-pg kill -9 1（容器内杀 PID 1）→ 8 秒后自动复活 healthy
- healthcheck pg_isready + restart: unless-stopped 组合：异常退出自动拉起

## 5. 结论
D14 验收通过：一键起栈 ✅ / EXPLAIN 优化案例（95×）✅ / 持久化 ✅ / 健康检查 ✅
