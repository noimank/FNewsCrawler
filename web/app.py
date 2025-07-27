#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Web应用主文件

提供财经新闻爬虫和登录管理的Web API接口
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from .api import login_router, crawler_router
from fnewscrawler.utils.logger import LOGGER

# 创建FastAPI应用实例
app = FastAPI(
    title="FNewsCrawler Web API",
    description="财经新闻爬虫和登录管理Web应用",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# 注册API路由
app.include_router(login_router, prefix="/api/login", tags=["登录管理"])
app.include_router(crawler_router, prefix="/api/crawler", tags=["爬虫管理"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "FNewsCrawler - 财经新闻爬虫管理平台"}
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录管理页面"""
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "title": "登录管理"}
    )


@app.get("/crawler", response_class=HTMLResponse)
async def crawler_page(request: Request):
    """爬虫管理页面"""
    return templates.TemplateResponse(
        "crawler.html", 
        {"request": request, "title": "爬虫管理"}
    )



@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
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


