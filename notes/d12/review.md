# D12 Docker Compose 编排 · 复习手册（2026-10-09 实操版）

## 0. 一句话
Compose = 一个 docker-compose.yml 描述全家桶（sensor-api + postgres + adminer），
docker compose up -d 一键启动，服务间用"服务名"互访。

## 1. 概念
| 概念 | 说明 |
|---|---|
| services | 服务清单（每个服务=一个容器） |
| 服务名即域名 | compose 内部网络按服务名解析（adminer 连 postgres 填服务名） |
| depends_on + healthcheck | 依赖编排：等 PG healthy 才起 api |
| environment | 容器环境变量（PG 初始用户/密码/库自动建） |
| volumes（底部声明） | 命名卷，Compose 自动加项目名前缀 |

## 2. 命令卡
| 命令 | 作用 |
|---|---|
| docker compose up -d | 一键启动 |
| docker compose ps | 状态（含 healthy） |
| docker compose logs 服务名 | 单服务日志 |
| docker compose exec 服务名 bash | 进容器 |
| docker compose down | 停止（卷保留） |
| docker compose down -v | 停止+删卷（慎用） |

## 3. 坑清单
| 坑 | 根因 | 解法 |
|---|---|---|
| docker compose: unknown command | compose 插件没装 | sudo apt install docker-compose-v2 |
| sensor-pg exited(1) | PG18 镜像改存储约定：拒绝挂 /data 子目录 | 挂载点改为 /var/lib/postgresql（父目录） |
| 端口冲突 | 宿主 PG 占 5432 | 容器映射 5433:5432 |

## 4. 问题 Q&A
Q1 Compose 解决什么问题？
A: 多容器编排——一个 yml 声明服务/网络/卷/依赖，一条命令起停；服务名互访免 IP 管理。

Q2 depends_on 有什么讲究？
A: 只保证"启动顺序"，不等"就绪"——所以要配合 healthcheck（condition: service_healthy）。

Q3 PG 数据怎么持久化？
A: 命名卷挂 /var/lib/postgresql（PG18 用父目录，版本子目录结构利于升级）。

Q4 生产 vs 开发部署差异？
A: 开发 bind mount 热更新；生产镜像内文件+命名卷持久化+healthcheck。

## 5. 自测
1. 默写 compose 六条命令
2. 手写一个两服务 yml（web + db）并说清卷/依赖/端口
3. 解释 down 和 down -v 的区别
