# FNewsCrawler Docker部署指南

🐳 **专业的财经信息MCP服务Docker部署解决方案**

本目录包含FNewsCrawler项目的完整Docker部署方案，支持从开发测试到生产环境的全流程部署。

## 📁 文件说明

```
docker/
├── README.md           # 本文档 - 完整部署指南
├── Dockerfile          # 镜像构建文件
├── start.sh           # 容器启动脚本
```

## 🚀 快速部署

### 🎯 方式一：官方镜像部署（推荐）

**最简单的部署方式，开箱即用：**

```bash
# 一键启动服务
docker run --name fnewscrawler \
  -p 8480:8480 \
  -d noimankdocker/fnewscrawler:latest

# 查看启动日志
docker logs fnewscrawler -f

# 检查服务状态
docker ps | grep fnewscrawler
```

**服务访问地址：**
- 🌐 **Web界面**: http://localhost:8480
- 📊 **系统监控**: http://localhost:8480/monitor
- 🛠️ **MCP管理**: http://localhost:8480/mcp
- 📚 **API文档**: http://localhost:8480/docs

### 🔧 方式二：源码构建部署

**适合需要自定义配置的场景：**

```bash
# 1. 克隆项目
git clone https://github.com/noimank/FNewsCrawler.git
cd FNewsCrawler

# 2. 使用docker-compose部署
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```




## 🐳 Docker镜像说明

### 🏗️ 构建流程

**源码构建过程：**
1. 基于优化的基础镜像
2. 复制项目源码到 `/app` 目录
3. 安装Python依赖包
4. 配置Playwright浏览器环境
5. 设置启动脚本和健康检查
6. 优化镜像层和缓存策略

## ⚙️ 配置说明

### 🔧 环境变量配置

| 变量名 | 默认值 | 说明 | 重要性 |
|--------|--------|------|--------|
| `WEB_HOST` | `0.0.0.0` | Web服务监听地址 | 🔵 基础 |
| `WEB_PORT` | `8480` | Web服务端口 | 🔵 基础 |
| `MCP_SERVER_TYPE` | `http` | MCP服务类型（sse/http） | 🔵 基础 |
| `REDIS_HOST` | `localhost` | Redis服务地址 | 🟡 重要 |
| `REDIS_PORT` | `6379` | Redis服务端口 | 🟡 重要 |
| `PW_USE_HEADLESS` | `true` | 浏览器无头模式 | 🟢 性能 |
| `PW_CONTEXT_MAX_IDLE_TIME` | `3600` | 上下文最大空闲时间（秒） | 🟢 性能 |
| `PW_CONTEXT_HEALTH_CHECK_TIME` | `300` | 健康检查间隔（秒） | 🟢 性能 |

### 🌐 端口映射

| 容器端口 | 宿主机端口 | 服务类型 | 访问地址 |
|----------|------------|----------|----------|
| `8480` | `8480` | Web服务 | http://localhost:8480 |
| `6379` | - | Redis（内部） | 容器内部通信 |



## 🐛 故障排除

### 🚨 常见问题解决

#### **问题1：服务无法启动**

**症状：** 容器启动失败或无法访问Web界面

```bash
# 🔍 诊断步骤
# 1. 检查端口占用
netstat -tulpn | grep 8480
# Windows用户使用：netstat -an | findstr 8480

# 2. 查看容器状态
docker ps -a | grep fnewscrawler

# 3. 查看详细启动日志
docker logs fnewscrawler --tail=50

# 4. 检查Docker守护进程
docker info

# 🔧 解决方案
# 重新启动容器
docker restart fnewscrawler

# 或完全重建
docker rm -f fnewscrawler
docker run --name fnewscrawler -p 8480:8480 -d noimankdocker/fnewscrawler:latest
```

#### **问题2：Redis连接失败**

**症状：** 应用报Redis连接错误

```bash
# 🔍 诊断步骤
# 1. 测试Redis连接
docker exec fnewscrawler redis-cli ping

# 2. 检查Redis进程状态
docker exec fnewscrawler ps aux | grep redis

# 3. 查看Redis日志
docker exec fnewscrawler tail -f /var/log/redis/redis-server.log

# 🔧 解决方案
# 重启Redis服务
docker exec fnewscrawler redis-server --daemonize yes

# 或重启整个容器
docker restart fnewscrawler
```

#### **问题3：浏览器启动失败**

**症状：** 爬虫功能无法正常工作，浏览器相关错误

```bash
# 🔍 诊断步骤
# 1. 检查Playwright安装
docker exec fnewscrawler playwright --version

# 2. 测试浏览器启动
docker exec fnewscrawler python -c "from playwright.sync_api import sync_playwright; print('Browser OK')"

# 🔧 解决方案
# 重新安装浏览器
docker exec fnewscrawler playwright install chromium

# 安装系统依赖
docker exec fnewscrawler playwright install-deps chromium

# 如果仍有问题，重建容器
docker rm -f fnewscrawler
docker run --name fnewscrawler -p 8480:8480 -d ghcr.io/noimank/fnewscrawler:latest
```


### ⚡ 性能优化

#### **内存和CPU优化**

```bash
# 限制容器资源使用
docker run --name fnewscrawler \
  -p 8480:8480 \
  --memory=2g \
  --cpus=2.0 \
  -d ghcr.io/noimank/fnewscrawler:latest

# 实时监控资源使用
docker stats fnewscrawler

# 详细资源统计
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### **网络优化**

```bash
# 创建自定义网络（适用于多容器部署）
docker network create --driver bridge fnewscrawler-net

# 使用自定义网络启动
docker run --name fnewscrawler \
  --network fnewscrawler-net \
  -p 8480:8480 \
  -d ghcr.io/noimank/fnewscrawler:latest
```


## 📊 监控和日志

### 健康检查

容器内置健康检查，每30秒检查一次服务状态：

```bash
# 查看健康状态
docker-compose ps

# 手动执行健康检查
docker-compose exec fnewscrawler curl -f http://localhost:8480/api/monitor/overview
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 查看特定服务日志
docker-compose logs fnewscrawler

# 导出日志
docker-compose logs > fnewscrawler.log
```

### 性能监控

```bash
# 资源使用统计
docker stats fnewscrawler

# 容器进程
docker-compose exec fnewscrawler top

# 磁盘使用
docker-compose exec fnewscrawler df -h
```

## 🚀 生产环境部署建议

### 🏗️ 架构优化

#### **1. 外部Redis部署**
```bash
# 🎯 推荐：使用外部Redis避免数据丢失，可以实现部署多个节点并共享数据
# 启动独立Redis容器
docker run --name redis-server \
  -p 6379:6379 \
  -v redis-data:/data \
  -d redis:7-alpine redis-server --appendonly yes

# 连接外部Redis启动应用
docker run --name fnewscrawler \
  -p 8480:8480 \
  -e REDIS_HOST=your-redis-host \
  -e REDIS_PORT=6379 \
  -v $(pwd)/logs:/app/logs \
  -d ghcr.io/noimank/fnewscrawler:latest
```

#### **2. 负载均衡配置**
```nginx
# Nginx配置示例
upstream fnewscrawler {
    server 127.0.0.1:8480;
    server 127.0.0.1:8481;  # 多实例部署
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://fnewscrawler;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```



### 🔒 安全建议

- ✅ **定期更新镜像**：`docker pull noimankdocker/fnewscrawler:latest`
- ✅ **网络隔离**：使用自定义网络限制容器间通信
- ✅ **资源限制**：设置CPU和内存限制防止资源耗尽
- ✅ **SSL证书**：生产环境必须使用HTTPS
- ✅ **访问控制**：配置防火墙和访问白名单

## 📞 技术支持

### 🆘 获取帮助

**遇到问题时的处理流程：**

1. **📖 查阅文档**
   - 首先查看本文档的故障排除部分
   - 查看项目主README的常见问题

2. **🔍 搜索已知问题**
   - 访问 [GitHub Issues](https://github.com/noimank/FNewsCrawler/issues)
   - 搜索相关关键词和错误信息

3. **📝 提交新Issue**
   - 提供详细的错误日志和环境信息
   - 包含复现步骤和期望结果
   - 使用相关标签（docker, deployment等）

4. **💬 社区支持**
   - 参与项目讨论区
   - 联系项目维护者

### 📋 问题报告模板

```markdown
**环境信息：**
- 操作系统：
- Docker版本：
- 镜像版本：
- 部署方式：

**问题描述：**
[详细描述遇到的问题]

**错误日志：**
```
[粘贴相关错误日志]
```

**复现步骤：**
1. 
2. 
3. 

**期望结果：**
[描述期望的正常行为]
```

---

🐳 **Happy Dockerizing!** 

*让财经数据获取变得简单高效* ✨