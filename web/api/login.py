#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录管理API路由

提供二维码登录相关的API接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime

from fnewscrawler.spiders.iwencai.login import IwencaiLogin
from fnewscrawler.spiders.eastmoney.login import EastMoneyLogin
from fnewscrawler.utils.logger import LOGGER

# 创建路由器
router = APIRouter()

# 全局登录实例管理
login_instances: Dict[str, Any] = {}
login_tasks: Dict[str, Dict[str, Any]] = {}


class QRLoginRequest(BaseModel):
    """二维码登录请求模型"""
    platform: str = "iwencai"
    qr_type: str = "微信"
    timeout: int = 120


class LoginStatusResponse(BaseModel):
    """登录状态响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/platforms")
async def get_supported_platforms():
    """获取支持的登录平台列表"""
    return {
        "success": True,
        "data": {
            "platforms": [
                {
                    "id": "iwencai",
                    "name": "问财",
                    "description": "同花顺问财平台",
                    "login_types": ["微信","QQ","同花顺"]
                },
                {
                    "id": "eastmoney",
                    "name": "东方财富",
                    "description": "东方财富平台",
                    "login_types": ["微信", "东方财富"]
                }
            ]
        }
    }


@router.get("/qr-types/{platform}")
async def get_supported_qr_types(platform: str):
    """获取指定平台支持的二维码登录方式"""
    try:
        if platform not in ["iwencai", "eastmoney"]:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 创建临时实例获取支持的登录方式
        if platform == "iwencai":
            login_instance = IwencaiLogin()
        elif platform == "eastmoney":
            login_instance = EastMoneyLogin()
        
        supported_types = login_instance.get_supported_qr_types()
        
        return {
            "success": True,
            "message": "获取支持的登录方式成功",
            "data": {
                "platform": platform,
                "qr_types": supported_types
            }
        }
        
    except Exception as e:
        LOGGER.error(f"获取支持的登录方式失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取支持的登录方式失败: {str(e)}")


@router.post("/qr/start")
async def start_qr_login(request: QRLoginRequest):
    """启动二维码登录"""
    try:
        platform = request.platform
        
        # 检查平台支持
        if platform not in ["iwencai", "eastmoney"]:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 创建登录实例
        if platform not in login_instances:
            if platform == "iwencai":
                login_instances[platform] = IwencaiLogin()
            elif platform == "eastmoney":
                login_instances[platform] = EastMoneyLogin()
            else:
                raise HTTPException(status_code=400, detail=f"无法创建登录实例: {platform}")
        
        login_instance = login_instances[platform]
        
        # 获取二维码
        success, qr_data = await login_instance.get_qr_code(request.qr_type)
        
        if not success:
            return LoginStatusResponse(
                success=False,
                message=f"获取二维码失败: {qr_data}"
            )
        
        if qr_data == "已经登录":
            return LoginStatusResponse(
                success=True,
                message="已经登录",
                data={"status": "logged_in"}
            )
        
        # 生成任务ID
        task_id = f"qr_login_{platform}_{int(time.time())}"
        
        # 保存任务信息
        login_tasks[task_id] = {
            "platform": platform,
            "qr_url": qr_data,
            "start_time": time.time(),
            "timeout": request.timeout,
            "status": "waiting"
        }
        
        return LoginStatusResponse(
            success=True,
            message="二维码生成成功",
            data={
                "task_id": task_id,
                "qr_url": qr_data,
                "timeout": request.timeout
            }
        )
        
    except Exception as e:
        LOGGER.error(f"启动二维码登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动二维码登录失败: {str(e)}")


@router.get("/qr/status/{task_id}")
async def check_qr_login_status(task_id: str):
    """检查二维码登录状态"""
    try:
        # 检查任务是否存在
        if task_id not in login_tasks:
            raise HTTPException(status_code=404, detail="登录任务不存在")
        
        task_info = login_tasks[task_id]
        platform = task_info["platform"]
        
        # 检查是否超时
        elapsed = time.time() - task_info["start_time"]
        if elapsed > task_info["timeout"]:
            # 清理任务
            del login_tasks[task_id]
            login_instance = login_instances.get(platform, None)
            if login_instance is not None:
                #尝试关闭资源
                await login_instance.close()
            return LoginStatusResponse(
                success=False,
                message="登录超时",
                data={"status": "timeout"}
            )
        
        # 检查登录状态
        if platform in login_instances:
            login_instance = login_instances[platform]
            # 使用不关闭浏览器的方法检查登录状态
            is_logged_in = await login_instance.verify_login_success()
            
            if is_logged_in:
                # 登录成功，保存状态
                await login_instance.save_context_state()
                
                await login_instance.close()
                # 清理任务
                del login_tasks[task_id]
                
                return LoginStatusResponse(
                    success=True,
                    message="登录成功",
                    data={"status": "success"}
                )
        
        # 计算剩余时间
        remaining = max(0, task_info["timeout"] - elapsed)
        
        return LoginStatusResponse(
            success=True,
            message="等待扫码",
            data={
                "status": "waiting",
                "remaining_time": int(remaining),
                "qr_url": task_info["qr_url"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"检查登录状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"检查登录状态失败: {str(e)}")


@router.delete("/qr/cancel/{task_id}")
async def cancel_qr_login(task_id: str):
    """取消二维码登录"""
    try:
        # 检查任务是否存在
        if task_id not in login_tasks:
            raise HTTPException(status_code=404, detail="登录任务不存在")
        
        task_info = login_tasks[task_id]
        platform = task_info["platform"]
        
        # 关闭登录实例
        if platform in login_instances:
            login_instance = login_instances[platform]

            await login_instance.close()
            # 移除实例
            del login_instances[platform]
        
        # 清理任务
        del login_tasks[task_id]
        
        return LoginStatusResponse(
            success=True,
            message="登录已取消"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"取消登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消登录失败: {str(e)}")


@router.get("/platform-status/{platform}")
async def get_login_status(platform: str):
    """获取平台登录状态"""
    try:
        if platform not in ["iwencai", "eastmoney"]:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 创建临时实例检查登录状态
        if platform == "iwencai":
            login_instance = IwencaiLogin()
        elif platform == "eastmoney":
            login_instance = EastMoneyLogin()
        
        is_logged_in = await login_instance.get_login_status()
        
        return LoginStatusResponse(
            success=True,
            message="获取登录状态成功",
            data={
                "platform": platform,
                "is_logged_in": is_logged_in,
                "check_time": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取登录状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取登录状态失败: {str(e)}")

@router.delete("/cache/{platform}")
async def clear_login_cache(platform: str):
    """清除登录缓存"""
    try:
        if platform not in ["iwencai", "eastmoney"]:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 创建临时实例清除缓存
        if platform == "iwencai":
            login_instance = IwencaiLogin()
        elif platform == "eastmoney":
            login_instance = EastMoneyLogin()
        
        success = await login_instance.clean_login_state()
        
        return LoginStatusResponse(
            success=success,
            message="清除登录缓存成功" if success else "清除登录缓存失败"
        )
        
    except Exception as e:
        LOGGER.error(f"清除登录缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除登录缓存失败: {str(e)}")


@router.get("/active-tasks")
async def get_active_tasks():
    """获取活跃的登录任务"""
    try:
        current_time = time.time()
        active_tasks = []
        
        for task_id, task_info in login_tasks.items():
            elapsed = current_time - task_info["start_time"]
            remaining = max(0, task_info["timeout"] - elapsed)
            
            if remaining > 0:
                active_tasks.append({
                    "task_id": task_id,
                    "platform": task_info["platform"],
                    "status": task_info["status"],
                    "remaining_time": int(remaining),
                    "elapsed_time": int(elapsed)
                })
        
        return {
            "success": True,
            "data": {
                "tasks": active_tasks,
                "total": len(active_tasks)
            }
        }
        
    except Exception as e:
        LOGGER.error(f"获取活跃任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取活跃任务失败: {str(e)}")