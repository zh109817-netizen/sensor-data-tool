
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

## 3. 持久化验证 ✅
- 写入 100000 行 → docker compose down → up → COUNT 仍为 100000
- 结论：卷 d14-data 持久化生效（容器删了数据在）

## 4. 健康检查验证 ✅（含修正）
- d14-pg healthy（pg_isready）；depends_on service_healthy 编排生效
- 修正：docker exec 杀主进程/kill = 外部强杀 → 不触发 restart（实测 api/pg RestartCount 恒 0）
- 正确验证：crash-test 容器（主进程 sleep 2; exit 1）→ RestartCount=1 自动拉起；stop 后停住

## 5. 补充知识（D14 实测收获）
- python:3.12-slim 无 kill 命令 → 用 python os.kill(1, SIGKILL)
- Docker 镜像 CMD = 启动命令（compose 不写 command 则继承）
- docker build -t 名字 . → 名字=镜像标签，Dockerfile 位置=上下文目录

## 6. 结论
D14 验收通过：一键起栈 ✅ / EXPLAIN 优化案例（95×）✅ / 持久化 ✅ / 健康检查 ✅ / restart 机制实测修正 ✅

