# D13 部署运维实战 · 复习手册（2026-10-10 实操版）

## 0. 一句话
容器化部署的四件运维事：日志、健康、备份、恢复 + 环境变量外置 + 版本管理。

## 1. 概念表
| 概念 | 要点 |
|---|---|
| restart 策略 | unless-stopped=异常退出自动拉起，手动 stop/kill 不拉起 |
| 模拟崩溃 | docker exec 容器 kill -9 1（杀容器内 PID 1，非 docker kill！） |
| .env | 敏感配置外置，yml 用 ${VAR} 引用，Compose 运行时注入 |
| pg_dump | PG 原生备份，SQL 文本可重放；> 重定向到宿主机文件 |
| 恢复 | docker exec -i 容器 psql < 备份文件（-i 保持 stdin） |
| 镜像 tag | latest=滚动标签不可回滚；v1.2.3=固定版本可回滚 |
| 日志驱动 | json-file 默认，日志存宿主机；轮转 max-size/max-file |

## 2. 命令卡
| 命令 | 作用 |
|---|---|
| docker exec 容器 kill -9 1 | 模拟容器内进程崩溃 |
| docker compose up -d --force-recreate | 用新配置强制重建 |
| docker exec sensor-pg pg_dump -U postgres 库 > 文件.sql | 备份 |
| docker exec -i sensor-pg psql -U postgres -d 库 < 文件.sql | 恢复 |
| docker tag 镜像 镜像:v1 | 打版本标签 |
| docker inspect 容器 --format '{{.HostConfig.RestartPolicy.Name}}' | 查重启策略 |
| (crontab -l; echo "任务") \| crontab - | 追加定时任务 |

## 3. 坑清单
| 坑 | 根因 | 解法 |
|---|---|---|
| docker kill 后不自动拉起 | kill=用户显式操作，restart 不管 | 用 docker exec 杀 PID 1 模拟崩溃 |
| sed 写 ${} 变空 | 双引号被 shell 展开 | 单引号让 ${VAR} 原样写入 |
| 8000 被占 | D7 systemd 服务 enable 自启 | sudo systemctl stop + disable |
| compose ps 端口列缺失 | 容器与 yml 状态不一致 | down + up 重建 |
| pg_dump 报错无文件 | 备份目录不存在 | 脚本先 mkdir -p |

## 4. 面试 Q&A
Q1 restart: unless-stopped 什么时候生效？
A: 容器内进程异常退出（杀 PID 1）自动拉起；docker stop/kill 不触发（尊重手动）。

Q2 密码为什么放 .env 不进 yml？
A: yml 要进 git；.env gitignore；敏感配置与代码分离。

Q3 pg_dump 备份怎么验证可靠？
A: 演练恢复——删表 → 重放备份 → 数据回来（备份可救命要真验证）。

Q4 latest 和 v1 的区别？
A: latest 滚动覆盖不可回滚；固定 tag 可回滚（老镜像还在）。

Q5 日志会撑爆磁盘吗？
A: 默认 json-file 无限增长；配 max-size/max-file 轮转。

## 5. 自测
1. 三句话讲清 restart 策略的生效边界
2. 默写备份/恢复两条命令
3. 解释为什么 sed 要用单引号
4. 说出 .env 的三个好处
