#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控API路由

提供browser和context服务的状态监控和管理接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from fnewscrawler.core.browser import BrowserManager
from fnewscrawler.core.context import context_manager
from fnewscrawler.utils.logger import LOGGER

# 创建路由器
router = APIRouter()

# 全局browser manager实例
browser_manager = BrowserManager()

class ServiceStatusResponse(BaseModel):
    """服务状态响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ServiceActionRequest(BaseModel):
    """服务操作请求模型"""
    action: str  # restart, cleanup, etc.
    target: Optional[str] = None  # 目标上下文名称（可选）

@router.get("/browser/status")
async def get_browser_status():
    """获取浏览器服务状态"""
    try:
        browser_info = await browser_manager.get_browser_info()
        
        return ServiceStatusResponse(
            success=True,
            message="获取浏览器状态成功",
            data={
                "service": "browser",
                "timestamp": datetime.now().isoformat(),
                **browser_info
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取浏览器状态失败: {e}")
        return ServiceStatusResponse(
            success=False,
            message=f"获取浏览器状态失败: {str(e)}",
            data={
                "service": "browser",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/context/status")
async def get_context_status():
    """获取上下文管理器状态"""
    try:
        context_stats = await context_manager.get_context_stats()
        
        return ServiceStatusResponse(
            success=True,
            message="获取上下文状态成功",
            data={
                "service": "context",
                "timestamp": datetime.now().isoformat(),
                **context_stats
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取上下文状态失败: {e}")
        return ServiceStatusResponse(
            success=False,
            message=f"获取上下文状态失败: {str(e)}",
            data={
                "service": "context",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/overview")
async def get_services_overview():
    """获取所有服务的概览状态"""
    try:
        # 并发获取两个服务的状态
        browser_task = asyncio.create_task(browser_manager.get_browser_info())
        context_task = asyncio.create_task(context_manager.get_context_stats())
        
        browser_info, context_stats = await asyncio.gather(
            browser_task, context_task, return_exceptions=True
        )
        
        # 处理browser结果
        if isinstance(browser_info, Exception):
            browser_status = {
                "status": "error",
                "error": str(browser_info)
            }
        else:
            browser_status = browser_info
        
        # 处理context结果
        if isinstance(context_stats, Exception):
            context_status = {
                "status": "error",
                "error": str(context_stats)
            }
        else:
            context_status = context_stats
        
        # 计算整体健康状态
        overall_healthy = (
            browser_status.get("status") == "healthy" and
            context_status.get("total_contexts", 0) >= 0
        )
        
        return ServiceStatusResponse(
            success=True,
            message="获取服务概览成功",
            data={
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy" if overall_healthy else "degraded",
                "services": {
                    "browser": browser_status,
                    "context": context_status
                }
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取服务概览失败: {e}")
        return ServiceStatusResponse(
            success=False,
            message=f"获取服务概览失败: {str(e)}",
            data={
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error"
            }
        )

@router.post("/browser/initialize")
async def browser_initialize():
    """初始化浏览器服务"""
    try:
        await browser_manager.initialize()
        browser_info = await browser_manager.get_browser_info()
        
        return ServiceStatusResponse(
            success=True,
            message="浏览器服务初始化成功",
            data={
                "action": "initialize",
                "timestamp": datetime.now().isoformat(),
                "browser_status": browser_info
            }
        )
        
    except Exception as e:
        LOGGER.error(f"初始化浏览器失败: {e}")
        raise HTTPException(status_code=500, detail=f"初始化浏览器失败: {str(e)}")

@router.post("/browser/action")
async def browser_action(request: ServiceActionRequest):
    """执行浏览器服务操作"""
    try:
        action = request.action.lower()
        
        if action == "restart":
            await browser_manager.force_restart()
            message = "浏览器服务重启成功"
        elif action == "initialize":
            await browser_manager.initialize()
            message = "浏览器服务初始化成功"
        elif action == "close":
            await browser_manager.close()
            message = "浏览器服务关闭成功"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作: {action}")
        
        # 获取操作后的状态
        browser_info = await browser_manager.get_browser_info()
        
        return ServiceStatusResponse(
            success=True,
            message=message,
            data={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "browser_status": browser_info
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"执行浏览器操作失败: {e}")
        raise HTTPException(status_code=500, detail=f"执行浏览器操作失败: {str(e)}")

@router.get("/context/stats")
async def get_context_stats():
    """获取上下文统计信息"""
    try:
        context_stats = await context_manager.get_context_stats()
        
        return ServiceStatusResponse(
            success=True,
            message="获取上下文统计成功",
            data={
                "service": "context",
                "timestamp": datetime.now().isoformat(),
                **context_stats
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取上下文统计失败: {e}")
        return ServiceStatusResponse(
            success=False,
            message=f"获取上下文统计失败: {str(e)}",
            data={
                "service": "context",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/context/cleanup")
async def context_cleanup():
    """清理过期上下文"""
    try:
        await context_manager._cleanup_expired_contexts()
        context_stats = await context_manager.get_context_stats()
        
        return ServiceStatusResponse(
            success=True,
            message="过期上下文清理成功",
            data={
                "action": "cleanup",
                "timestamp": datetime.now().isoformat(),
                "context_status": context_stats
            }
        )
        
    except Exception as e:
        LOGGER.error(f"清理上下文失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理上下文失败: {str(e)}")

@router.post("/context/action")
async def context_action(request: ServiceActionRequest):
    """执行上下文管理器操作"""
    try:
        action = request.action.lower()
        target = request.target
        
        if action == "refresh" and target:
            await context_manager.refresh_context(target)
            message = f"上下文 {target} 刷新成功"
        elif action == "close" and target:
            await context_manager.close_site_context(target)
            message = f"上下文 {target} 关闭成功"
        elif action == "close_all":
            await context_manager.close_all()
            message = "所有上下文关闭成功"
        elif action == "cleanup":
            await context_manager._cleanup_expired_contexts()
            message = "过期上下文清理成功"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作: {action} (target: {target})")
        
        # 获取操作后的状态
        context_stats = await context_manager.get_context_stats()
        
        return ServiceStatusResponse(
            success=True,
            message=message,
            data={
                "action": action,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "context_status": context_stats
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"执行上下文操作失败: {e}")
        raise HTTPException(status_code=500, detail=f"执行上下文操作失败: {str(e)}")

@router.get("/context/{site_name}/status")
async def get_site_context_status(site_name: str):
    """获取指定站点的上下文状态"""
    try:
        context_stats = await context_manager.get_context_stats()
        
        if site_name not in context_stats.get("contexts", {}):
            return ServiceStatusResponse(
                success=False,
                message=f"站点 {site_name} 的上下文不存在",
                data={
                    "site_name": site_name,
                    "exists": False,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        site_info = context_stats["contexts"][site_name]
        
        return ServiceStatusResponse(
            success=True,
            message=f"获取站点 {site_name} 状态成功",
            data={
                "site_name": site_name,
                "exists": True,
                "timestamp": datetime.now().isoformat(),
                **site_info
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取站点 {site_name} 状态失败: {e}")
        return ServiceStatusResponse(
            success=False,
            message=f"获取站点状态失败: {str(e)}",
            data={
                "site_name": site_name,
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 快速健康检查
        browser_healthy = True
        context_healthy = True
        
        try:
            browser_info = await browser_manager.get_browser_info()
            browser_healthy = browser_info.get("status") in ["healthy", "not_initialized"]
        except Exception:
            browser_healthy = False
        
        try:
            context_stats = await context_manager.get_context_stats()
            context_healthy = isinstance(context_stats.get("total_contexts"), int)
        except Exception:
            context_healthy = False
        
        overall_healthy = browser_healthy and context_healthy
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "browser": "healthy" if browser_healthy else "unhealthy",
                "context": "healthy" if context_healthy else "unhealthy"
            }
        }
        
    except Exception as e:
        LOGGER.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }