# FNewsCrawler

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**专业的财经信息MCP服务** - 为大模型提供实时、准确的财经资讯数据

## 🚀 项目简介

FNewsCrawler 是一个专门为大模型设计的财经信息MCP（Model Context Protocol）服务，通过高效的爬虫技术从各大财经网站获取实时资讯，为AI模型提供准确、及时的财经数据支持。

### 🎯 核心特性

- **🤖 MCP协议兼容**：完全兼容Model Context Protocol，可无缝集成到各种AI应用中
- **📈 实时财经数据**：支持从同花顺问财等主流财经平台获取最新资讯
- **🏗️ 企业级架构**：采用单例模式的浏览器管理和上下文共享机制
- **🔐 智能登录系统**：支持二维码登录，自动维护登录状态
- **⚡ 高性能并发**：基于异步架构，支持高并发访问
- **🛡️ 生产级稳定性**：完善的错误处理、自动重试和健康检查机制
- **📊 可视化管理**：提供Web界面进行工具管理和系统监控

## 🏛️ 系统架构

```
FNewsCrawler
├── 🧠 MCP服务层          # 为大模型提供标准化接口
├── 🕷️ 爬虫引擎层         # 多站点财经数据采集
├── 🌐 浏览器管理层       # 单例浏览器实例管理
├── 🔄 上下文共享层       # 域名级别的会话状态管理
├── 🔐 登录认证层         # 二维码登录和状态维护
└── 💾 数据存储层         # Redis缓存和状态持久化
```

## 📦 快速开始

### 环境要求

- Python 3.8+
- Redis 服务器
- Chrome/Chromium 浏览器

### 安装部署

#### 🐳 Docker部署（推荐）

**方式一：从项目源码部署**
```bash
# 克隆项目
git clone https://github.com/noimank/FNewsCrawler.git
cd FNewsCrawler

# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

```

**方式二：快速部署启动**
```bash

#从dockerhub中拉取镜像并后台启动
docker run --name fnewscrawler -p 8480:8480 -d noimankdocker/fnewscrawler:latest

# 查看日志
docker logs fnewscrawler -f




```


> 📚 **详细文档**：查看 [Docker部署指南](docker/README.md) 了解完整的部署选项、配置说明和故障排除方法。

#### 📦 本地开发测试

1. **克隆项目**
```bash
git clone https://github.com/noimank/FNewsCrawler.git
cd FNewsCrawler
```

2. **安装依赖**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **配置环境**
```bash
# 创建 .env 文件，配置环境变量，建议关闭无头模式进行
cp .env.example .env

```

4. **启动Redis服务**
```bash
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows
# 下载并启动Redis服务
```

5. **启动服务**
```bash
# 启动Web服务
python main.py


```

### MCP客户端集成

MCP访问协议支持sse和http，通过环境变量MCP_SERVER_TYPE修改

mcp服务地址：http://localhost:8480/mcp/mcp-server

cherryStudio配置：
```
{
  "mcpServers": {
    "fnewscrawler": {
      "url": "http://localhost:8480/mcp/mcp-server",
      "type": "streamableHttp"
    }
  }
}
```

## 🛠️ 




## 🔧 开发指南

### 添加新的财经数据源

1. **创建爬虫模块**
```bash
mkdir fnewscrawler/spiders/新站点名
touch fnewscrawler/spiders/新站点名/__init__.py
touch fnewscrawler/spiders/新站点名/crawl.py
touch fnewscrawler/spiders/新站点名/login.py  # 如需登录
```

2. **实现登录类**（如需要）
```python
from fnewscrawler.core.qr_login_base import QRLoginBase

class NewSiteLogin(QRLoginBase):
    async def get_qr_code(self, qr_type: str) -> Tuple[bool, str]:
        # 实现二维码获取逻辑
        pass
    
    async def verify_login_success(self) -> bool:
        # 实现登录验证逻辑
        pass
```

3. **创建MCP工具**
```python
# fnewscrawler/mcp/新站点名/crawl.py
from fnewscrawler.mcp import mcp_server

@mcp_server.tool()
async def new_site_query(query: str):
    """新站点查询工具描述"""
    # 实现查询逻辑
    pass
```

4. **注册工具**
```python
# fnewscrawler/mcp/新站点名/__init__.py
import fnewscrawler.mcp.新站点名.crawl
```

### 核心设计原则

- **单例模式**：BrowserManager和ContextManager采用单例模式，确保资源高效利用
- **域名隔离**：每个域名维护独立的浏览器上下文，避免会话冲突
- **异步优先**：全面采用异步编程，提升并发性能
- **状态持久化**：登录状态和会话信息自动保存到Redis
- **健康检查**：定期检查浏览器和上下文健康状态，自动恢复异常

## 📊 系统监控

访问 `http://localhost:8480/monitor` 查看系统状态：

- 🌐 **浏览器状态**：实例健康度、版本信息、资源使用
- 🔄 **上下文管理**：活跃会话、空闲时间、使用统计
- 🛠️ **MCP工具**：工具状态、启用/禁用管理
- 📈 **系统日志**：实时日志查看和过滤

## 🔧 工具管理

访问 `http://localhost:8480/mcp` 进行工具管理：

- ✅ **启用/禁用工具**：动态控制工具可用性
- 📝 **工具详情查看**：查看工具描述和参数
- 🔄 **批量操作**：支持批量启用/禁用工具
- 📊 **使用统计**：工具调用次数和状态监控

## 🤝 贡献指南

我们欢迎社区贡献！请查看 [开发文档](docs/) 了解详细信息：

- [爬虫开发指南](docs/spider_development.md)
- [MCP工具开发指南](docs/mcp_tool_development.md)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP协议实现
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Redis](https://redis.io/) - 数据存储

---

**为大模型提供专业的财经数据支持** 🚀

如有问题或建议，请提交 [Issue](https://github.com/your-repo/FNewsCrawler/issues) 或 [Pull Request](https://github.com/your-repo/FNewsCrawler/pulls)。