cat > d11_review.md << 'EOF'
# D11 Docker 入门 · 复习手册（2026-10-09 实操版）

## 0. 一句话总结
镜像 = 类（只读模板），容器 = 实例（运行环境），卷 = 外接硬盘，网络 = 端口映射。
今天成果：sensor-api 容器化部署成功，curl /health、/smooth 验证通过。

## 1. 四概念卡（问题必答）
| 概念 | 定义 | 类比 | 关键命令 |
|---|---|---|---|
| 镜像 image | 只读模板：OS+依赖+代码打包 | 类 / 光盘 / 图纸 | docker build -t 名 . |
| 容器 container | 镜像的运行实例，可启停删 | 对象 / 便签纸 / 产品 | docker run / ps / rm |
| 卷 volume | 容器外的持久化存储 | 外接硬盘 / U 盘 | docker volume ls |
| 网络 | 容器对外通信 | 端口映射=门牌号 | -p 8000:8000 |

铁律：容器可写层随容器删除消失；要留的数据必须放卷。

## 2. 命令速查卡
构建 / 运行 / 管理 / 卷 / 清理 五大场景：
| 场景 | 命令 | 说明 |
|---|---|---|
| 构建 | docker build -t sensor-api . | 读当前目录 Dockerfile 出镜像 |
| 运行 | docker run -d --name x -p 8000:8000 镜像 | -d 后台 / --name 起名 / -p 映射 |
| 列表 | docker images / docker ps -a | 镜像 / 容器 |
| 日志 | docker logs 容器名 | journalctl 的容器版 |
| 进容器 | docker exec -it 容器 bash | 内部 shell，exit 退出 |
| 重启 | docker restart 容器名 | 重载代码/重新挂载 |
| 拷文件 | docker cp 容器:路径 本地路径 | 取出容器文件 |
| 卷挂载 | -v 卷名:容器路径 | named volume 持久化 |
| 卷挂载 | -v 宿主路径:容器路径 | bind mount 开发同步 |
| 清理 | docker system prune / system df | 磁盘不够时用 |

## 3. 今日实操全流程（可复现路径）
1. 安装：sudo apt install docker.io → sudo systemctl enable --now docker
2. 免 sudo：sudo usermod -aG docker $USER（重开终端生效）
3. 加速器：/etc/docker/daemon.json 写 registry-mirrors → restart docker
4. 验证：docker run hello-world
5. 写 Dockerfile（FROM/WORKDIR/COPY/RUN/EXPOSE/CMD 六段）
6. 构建：docker build -t sensor-api .（上下文 68KB）
7. 运行：docker run -d --name sensor-api -p 8000:8000 sensor-api
8. 验证：curl /health /smooth（与 D7 输出一致）
9. 卷实验：named volume 写数据 → 删容器 → 新容器读到（数据存活）

## 4. 坑清单（今天踩过的）
| 坑 | 现象 | 根因 | 解法 |
|---|---|---|---|
| 拉镜像超时 | i/o timeout | 连不上 Docker Hub | daemon.json 配镜像加速 |
| 端口占用 | address already in use | systemd 服务占 8000 | ss -tlnp 查 → 停旧服务 |
| 改代码不生效 | 容器还是旧行为 | ①bind mount 绑 inode ②Python 无热加载 | docker restart |
| sed -i 陷阱 | 宿主机新/容器旧 | sed -i 是 rename 换 inode | 重启容器重新挂载 |
| 续行吞命令 | 提示符变 > | 引号未闭合 | Ctrl+C 取消重输 |
| 全角分号 | 命令异常 | 中文标点不是分隔符 | 只用半角 ; |

## 5. 面试 Q&A（自测）
Q1 镜像和容器区别？
A: 镜像=只读模板（类），容器=运行实例（对象）；同镜像可跑多容器互不干扰。

Q2 为什么需要卷？
A: 容器可写层随删除消失，数据会丢；卷独立于容器生命周期，重建容器数据还在。

Q3 国内怎么拉镜像？
A: /etc/docker/daemon.json 配 registry-mirrors（多个源）→ restart docker。

Q4 改了代码为什么容器没变？
A: ①bind mount 绑 inode，sed -i 换文件后锚点失效 ②Python 模块启动时加载一次。
解法：docker restart（秒级），或开发配 --reload 工具。

Q5 端口冲突怎么排查？
A: ss -tlnp | grep 端口 → 找到占用进程 → 停掉/换端口 → 重跑。

Q6 Dockerfile 为什么依赖放前面 COPY？
A: 分层缓存——依赖层不变就复用，改代码只重建最后一层，构建秒级。

Q7 生产镜像为什么瘦身？
A: 只装运行依赖、.dockerignore 排除杂物 → 镜像小、构建快、攻击面小。

## 6. 动手自测
1. 默写 5 个核心命令（build/run/ps/exec/logs）
2. 解释 -v 两种写法（named volume vs bind mount）的适用场景
3. 现场跑一遍：build 一个镜像 → run → curl → rm
EOF
