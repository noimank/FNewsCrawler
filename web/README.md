# FNewsCrawler Web 应用

基于 FastAPI 的现代化 Web 界面，提供二维码登录管理和新闻爬取功能。

## 功能特性

### 🔐 登录管理
- 支持多平台二维码登录（问财等）
- 实时登录状态监控
- 登录会话管理
- 自动超时处理

### 🕷️ 爬虫管理
- 单个URL爬取
- 批量URL爬取
- 任务状态监控
- 结果查看和下载
- 并发控制

### 🎨 用户界面
- 响应式设计，支持移动端
- 现代化UI，基于Bootstrap 5
- 实时状态更新
- 友好的错误提示

## 项目结构

```
fnewscrawler/web/
├── app.py                 # FastAPI主应用
├── api/                   # API路由模块
│   ├── __init__.py
│   ├── login.py          # 登录管理API
│   └── crawler.py        # 爬虫管理API
├── templates/            # Jinja2模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 主页
│   ├── login.html        # 登录管理页面
│   └── crawler.html      # 爬虫管理页面
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 自定义样式
│   └── js/
│       └── common.js     # 公共JavaScript
└── README.md             # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

#### 方式一：使用启动脚本（推荐）

```bash
python main.py
```

#### 方式二：直接使用uvicorn

```bash
uvicorn fnewscrawler.web.app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问应用

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## API 接口

### 登录管理 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/login/platforms` | 获取支持的登录平台 |
| POST | `/api/login/start` | 启动二维码登录 |
| GET | `/api/login/status/{task_id}` | 检查登录状态 |
| POST | `/api/login/cancel/{task_id}` | 取消登录 |
| GET | `/api/login/platform-status/{platform}` | 获取平台登录状态 |
| POST | `/api/login/clear-cache/{platform}` | 清除登录缓存 |
| GET | `/api/login/active-tasks` | 获取活跃登录任务 |

### 爬虫管理 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/crawler/platforms` | 获取支持的爬虫平台 |
| POST | `/api/crawler/crawl-single` | 单个URL爬取 |
| POST | `/api/crawler/crawl-batch` | 批量URL爬取 |
| GET | `/api/crawler/task/{task_id}` | 获取任务状态 |
| GET | `/api/crawler/result/{task_id}` | 获取任务结果 |
| DELETE | `/api/crawler/task/{task_id}` | 删除任务 |
| GET | `/api/crawler/tasks` | 获取所有任务 |

## 使用指南

### 登录管理

1. **选择平台**: 在登录管理页面选择要登录的平台
2. **设置超时**: 配置二维码超时时间（默认300秒）
3. **扫码登录**: 使用对应平台的APP扫描二维码
4. **状态监控**: 实时查看登录状态和活跃任务
5. **缓存管理**: 可以清除特定平台的登录缓存

### 爬虫管理

#### 单个URL爬取
1. 输入要爬取的URL
2. 选择爬虫平台（如果URL匹配多个平台）
3. 点击"开始爬取"按钮
4. 查看爬取进度和结果

#### 批量URL爬取
1. 在文本框中输入多个URL（每行一个）
2. 设置并发数量（默认3）
3. 点击"批量爬取"按钮
4. 监控所有任务的进度

#### 任务管理
- **查看结果**: 点击任务卡片查看详细结果
- **下载数据**: 将爬取结果下载为JSON文件
- **删除任务**: 清理不需要的任务记录
- **状态筛选**: 按任务状态筛选显示

## 配置说明

### 环境变量

- `REDIS_URL`: Redis连接URL（默认: redis://localhost:6379/0）
- `LOG_LEVEL`: 日志级别（默认: INFO）
- `MAX_CONCURRENT_TASKS`: 最大并发任务数（默认: 10）

### 应用配置

在 `app.py` 中可以修改以下配置：

```python
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件配置
app.mount("/static", StaticFiles(directory="fnewscrawler/web/static"), name="static")
```

## 开发指南

### 添加新的登录平台

1. 在 `fnewscrawler/spiders/` 下创建新的平台目录
2. 实现继承自 `QRLoginBase` 的登录类
3. 在 `api/login.py` 中注册新平台

### 添加新的爬虫平台

1. 在对应的爬虫目录中实现爬虫逻辑
2. 在 `api/crawler.py` 中添加平台支持
3. 更新前端界面的平台选择器

### 自定义样式

- 修改 `static/css/style.css` 添加自定义样式
- 使用Bootstrap 5的工具类快速调整样式
- 支持响应式设计，确保移动端兼容性

### 扩展API

1. 在 `api/` 目录下创建新的路由文件
2. 在 `app.py` 中注册新的路由
3. 更新API文档和前端调用

## 部署指南

### 开发环境

```bash
# 启动开发服务器
python start_web.py
```

### 生产环境

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn fnewscrawler.web.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "fnewscrawler.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 故障排除

### 常见问题

1. **端口被占用**
   - 修改启动脚本中的端口号
   - 或者杀死占用端口的进程

2. **Redis连接失败**
   - 确保Redis服务正在运行
   - 检查Redis连接配置

3. **浏览器初始化失败**
   - 确保已安装Playwright浏览器
   - 运行 `playwright install` 安装浏览器

4. **静态文件404**
   - 检查静态文件路径配置
   - 确保文件存在于正确位置

### 日志查看

应用日志会输出到控制台，包含以下信息：
- API请求和响应
- 登录状态变化
- 爬虫任务进度
- 错误和异常信息

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。