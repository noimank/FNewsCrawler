#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Web应用主文件

提供财经新闻登录管理的Web API接口
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fnewscrawler.utils.logger import LOGGER
from .api import login_router, monitor_router, mcp_router, tools_router
from fnewscrawler.mcp import mcp_server
from fnewscrawler.mcp.mcp_manager import MCPManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的操作
    try:
        LOGGER.info("FNewsCrawler Web应用正在启动")
        # 初始化MCP工具状态
        mcp_manager = MCPManager()
        await mcp_manager.init_tools_status()
        LOGGER.info("MCP工具状态初始化完成")
        
    except Exception as e:
        LOGGER.error(f"应用启动时发生错误: {e}")
    
    yield

    # 关闭时的操作
    try:
        LOGGER.info("FNewsCrawler Web应用正在关闭")

        # 清理浏览器资源
        from fnewscrawler.core.browser import browser_manager
        await browser_manager.close()

        # 清理登录实例
        from web.api.login import login_instances
        for platform, instance in login_instances.items():
            try:
                await instance.close()
                LOGGER.info(f"已关闭 {platform} 登录实例")
            except Exception as e:
                LOGGER.warning(f"关闭 {platform} 登录实例时发生错误: {e}")

        login_instances.clear()
        LOGGER.info("FNewsCrawler Web应用关闭完成")
    except Exception as e:
        LOGGER.error(f"应用关闭时发生错误: {e}")

mcp_app = None

# 创建MCP服务器的ASGI应用
if os.getenv("MCP_SERVER_TYPE","sse") == "sse":
    mcp_app = mcp_server.sse_app(path='/mcp-server')
    LOGGER.info("MCP服务器已配置为SSE模式")
else:
    mcp_app = mcp_server.http_app(path='/mcp-server')
    LOGGER.info("MCP服务器已配置为HTTP模式")

# 创建FastAPI应用实例，集成MCP生命周期
@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    """组合应用和MCP的生命周期管理"""
    async with lifespan(app):
        async with mcp_app.lifespan(app):
            yield

app = FastAPI(
    title="FNewsCrawler Web API",
    description="财经新闻登录管理Web应用",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=combined_lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件目录
current_dir = Path(__file__).parent

# 配置静态文件服务
static_dir = current_dir / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 配置模板引擎
templates_dir = current_dir / "templates"
if not templates_dir.exists():
    templates_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

# 挂载MCP服务器
app.mount("/mcp", mcp_app)

# 注册API路由
app.include_router(login_router, prefix="/api/login", tags=["登录管理"])
app.include_router(monitor_router, prefix="/api/monitor", tags=["系统监控"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP管理"])
app.include_router(tools_router, prefix="/api/call_tools", tags=["get方法调用各类工具"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页"""
    return templates.TemplateResponse(
        request,
        "index.html", 
        {"title": "FNewsCrawler - 财经新闻爬虫管理平台"}
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录管理页面"""
    return templates.TemplateResponse(
        request,
        "login.html", 
        {"title": "登录管理"}
    )




@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    """系统监控页面"""
    return templates.TemplateResponse(
        request,
        "monitor.html", 
        {"title": "系统监控"}
    )


@app.get("/mcp", response_class=HTMLResponse)
async def mcp_page(request: Request):
    """MCP管理页面"""
    return templates.TemplateResponse(
        request,
        "mcp.html", 
        {"title": "MCP管理"}
    )



