# D11 Docker 入门笔记

## 四概念（面试必答）
- 镜像 = 只读模板（类），容器 = 运行实例（对象），卷 = 外接硬盘，网络 = 端口映射
- 容器可写层随容器删除消失；卷独立于容器生命周期

## 核心命令
- docker build -t sensor-api .          # Dockerfile 构建镜像
- docker run -d --name x -p 8000:8000   # 运行 + 端口映射
- docker exec / logs / ps / restart / rm
- -v 卷名:容器路径 = named volume（持久化）
- -v 宿主路径:容器路径 = bind mount（开发同步）

## 实测数据与坑
- 国内拉镜像超时 → /etc/docker/daemon.json 配 registry-mirrors 解决
- 镜像瘦身：只装运行依赖（requirements-app.txt 仅 numpy），构建上下文 68KB
- 端口冲突：ss -tlnp 查占用 → 停 systemd 版服务 → 重跑
- ★ bind mount 绑 inode 不绑路径：sed -i 换文件（rename）后容器读旧内容，
  必须 docker restart 重新挂载；Python 也无热加载，改代码=重启容器

## 口述结论
镜像/容器/卷/网络四概念，国内镜像加速，镜像最小化，
把 sensor-api 容器化部署并用 curl /health、/smooth 验证。
