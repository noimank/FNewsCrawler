# FNewsCrawler

## 项目简介

FNewsCrawler 是一个专门用于**财经新闻爬取**的 Python 爬虫框架，基于 [Playwright](https://playwright.dev/python/) 构建。项目提供了**命令行工具**和**Web可视化界面**两种使用方式，支持多种新闻源的数据采集，具备完整的登录状态管理和Redis缓存功能。

## 主要特性

- 🚀 基于 Playwright 的异步爬虫框架
- 💰 专注财经新闻数据采集
- 🖥️ **Streamlit Web管理界面** - 可视化操作和管理
- 🔐 **智能登录管理** - 支持二维码、手机号、邮箱登录
- 🗄️ **Redis缓存系统** - 登录状态持久化和复用
- 🔧 **模块化设计** - 易于扩展新的新闻源
- 🌐 支持同花顺 iWencai 网站爬取 (东方财富开发中)
- 📊 内置浏览器管理和单例模式
- 📝 完整的日志记录系统

## 目录结构

```
FNewsCrawler/
├── README.md
├── requirements.txt         # 项目依赖
├── main.py                  # 主入口文件
├── fnewscrawler/           # 核心爬虫模块
│   ├── routes/             # 路由模块
│   ├── spiders/            # 爬虫实现
│   │   ├── __init__.py
│   │   ├── core/           # 核心组件
│   │   │   ├── __init__.py
│   │   │   └── browser.py  # 浏览器管理器
│   │   ├── iwencai/        # 同花顺iWencai爬虫
│   │   │   ├── __init__.py
│   │   │   ├── crawl.py    # 爬取逻辑(精简版)
│   │   │   └── login.py    # 登录处理
│   │   ├── example_spider.py
│   │   └── markdown_extract.py
│   ├── web/                # Web管理界面
│   │   ├── __init__.py
│   │   ├── app.py          # Streamlit主应用
│   │   ├── run.py          # 启动脚本
│   │   └── pages/          # 页面管理
│   │       ├── __init__.py
│   │       ├── base_manager.py      # 基础管理器
│   │       ├── iwencai_manager.py   # 同花顺管理器
│   │       └── dongfang_manager.py  # 东方财富管理器
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── config.py       # 配置管理
│       ├── logger.py       # 日志工具
│       └── path.py         # 路径工具
├── docs/                   # 文档目录
│   ├── login_state_sharing_explanation.md
│   └── web_application_guide.md
└── test/                   # 测试文件
    ├── env.py
    ├── iwencai_craw.py     # iWencai爬虫测试
    ├── login_sharing_demo.py
    ├── web_app_demo.py     # Web应用演示
    └── logger.py
```

## 安装依赖

```bash
# 建议使用虚拟环境
python -m venv venv

# Windows 激活虚拟环境
venv\Scripts\activate

# Linux/Mac 激活虚拟环境
# source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器驱动
python -m playwright install
```

## 快速开始

### 🖥️ Web管理界面 (推荐)

```bash
# 启动Web管理界面
python fnewscrawler/web/run.py

# 或使用演示脚本
python test/web_app_demo.py

# 浏览器访问: http://localhost:8501
```

**Web界面功能：**
- 📊 可视化登录状态管理
- 🔐 多种登录方式 (二维码/手机号/邮箱)
- 🚀 交互式爬取任务配置
- 📈 实时系统状态监控
- ⚙️ 配置管理和Redis连接测试

### 📟 命令行使用

```bash
# 运行主程序
python main.py

# 测试 iWencai 爬虫
python test/iwencai_craw.py
```

### 3. 代码示例

```python
import asyncio
from fnewscrawler.spiders.iwencai.crawl import IwencaiCrawler

async def main():
    crawler = IwencaiCrawler()
    result = await crawler.crawl("https://www.iwencai.com/unifiedwap/info/info")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 核心功能

### 🖥️ Web管理界面

基于 Streamlit 构建的现代化管理界面：

- **登录管理**: 可视化登录状态，支持二维码、手机号、邮箱登录
- **爬取任务**: 交互式配置爬取参数，实时查看结果
- **系统监控**: Redis连接状态、登录状态摘要、系统信息
- **配置管理**: Redis连接测试、爬虫参数配置
- **多源支持**: 模块化设计，易于扩展新的新闻源

### 🔐 智能登录管理

完整的登录状态管理系统：

- **Redis缓存**: 登录状态持久化存储和复用
- **多种登录方式**: 二维码扫码、手机号验证、邮箱登录
- **状态共享**: 跨页面登录状态共享机制
- **自动恢复**: 智能加载缓存的登录状态

### 🚀 浏览器管理

项目采用单例模式的浏览器管理器，确保资源的有效利用：

- 异步浏览器实例化
- 自动资源管理
- 支持无头模式和有头模式

### 💰 财经新闻爬取

专门针对财经资讯网站优化：

- **同花顺 iWencai**: 完整的新闻爬取支持
- **东方财富**: 开发中，敬请期待
- 支持关键词搜索和分页爬取
- 自动处理页面交互和数据提取
- 结构化数据输出和导出功能

## 项目依赖

### 核心依赖
- `playwright` - 浏览器自动化框架
- `streamlit` - Web应用框架
- `redis` - 缓存和状态管理
- `httpx` - HTTP 客户端
- `loguru` - 日志记录
- `crawl4ai` - 爬虫辅助工具

### 系统要求
- Python 3.8+
- Redis 服务器 (用于登录状态缓存)
- 支持的浏览器: Chrome/Chromium, Firefox, Safari

## 📚 详细文档

- [Web应用使用指南](docs/web_application_guide.md) - 完整的Web界面使用说明
- [登录状态共享机制](docs/login_state_sharing_explanation.md) - 技术实现原理
- [演示脚本说明](test/web_app_demo.py) - 快速体验Web应用

## 🚀 开发计划

### 已完成 ✅
- [x] Streamlit Web管理界面
- [x] Redis登录状态缓存
- [x] 同花顺iWencai爬虫
- [x] 多种登录方式支持
- [x] 模块化架构设计

### 开发中 🔄
- [ ] 东方财富新闻源
- [ ] 数据导出功能优化
- [ ] 性能监控面板

### 计划中 📋
- [ ] 更多财经网站支持
- [ ] 分布式爬取架构
- [ ] 数据分析和可视化
- [ ] API接口开发
- [ ] Docker容器化部署

## ⚠️ 注意事项

1. **合规使用**: 请遵守网站的 robots.txt 协议和使用条款
2. **频率控制**: 合理控制爬取频率，避免对目标网站造成压力
3. **用途限制**: 仅用于学习和研究目的，请勿用于商业用途
4. **环境准备**: 使用前请确保已安装 Playwright 浏览器驱动和Redis服务
5. **数据安全**: 登录凭据仅存储在本地Redis中，请妥善保管

## 许可证

本项目仅供学习交流使用。