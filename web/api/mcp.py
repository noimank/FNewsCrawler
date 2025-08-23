#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP管理API接口

提供MCP工具的管理功能，包括查看、启用、禁用等操作
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

from fnewscrawler.mcp.mcp_manager import MCPManager
from fnewscrawler.utils.logger import LOGGER

# 创建路由器
router = APIRouter()

# 创建MCP管理器实例
mcp_manager = MCPManager()


class MCPToolInfo(BaseModel):
    """MCP工具信息模型"""
    name: str
    title: str
    description: str
    enabled: bool


class MCPToolStatusRequest(BaseModel):
    """MCP工具状态请求模型"""
    tool_name: str
    enabled: bool


class APIResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get("/tools", response_model=APIResponse)
async def get_all_tools():
    """
    获取所有MCP工具信息
    
    Returns:
        包含所有工具信息的响应
    """
    try:
        tools_info = await mcp_manager.get_all_tools_info()
        
        return APIResponse(
            success=True,
            message=f"获取MCP工具信息成功，共 {len(tools_info)} 个工具",
            data={
                "tools": tools_info,
                "total_count": len(tools_info),
                "enabled_count": len([t for t in tools_info if t["enabled"]]),
                "disabled_count": len([t for t in tools_info if not t["enabled"]])
            }
        )
    except Exception as e:
        LOGGER.error(f"获取MCP工具信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取工具信息失败: {str(e)}")


@router.get("/tools/{tool_name}", response_model=APIResponse)
async def get_tool_info(tool_name: str):
    """
    获取指定MCP工具的详细信息
    
    Args:
        tool_name: 工具名称
        
    Returns:
        包含工具详细信息的响应
    """
    try:
        tool_info = await mcp_manager.get_tool_info(tool_name)
        
        return APIResponse(
            success=True,
            message=f"获取工具 {tool_name} 信息成功",
            data=tool_info
        )
    except Exception as e:
        LOGGER.error(f"获取工具 {tool_name} 信息失败: {e}")
        raise HTTPException(status_code=404, detail=f"工具 {tool_name} 不存在或获取失败")


@router.post("/tools/{tool_name}/enable", response_model=APIResponse)
async def enable_tool(tool_name: str):
    """
    启用指定的MCP工具
    
    Args:
        tool_name: 工具名称
        
    Returns:
        操作结果响应
    """
    try:
        success = await mcp_manager.enable_tool(tool_name)
        
        if success:
            LOGGER.info(f"MCP工具 {tool_name} 启用成功")
            return APIResponse(
                success=True,
                message=f"工具 {tool_name} 启用成功",
                data={"tool_name": tool_name, "enabled": True}
            )
        else:
            raise HTTPException(status_code=400, detail=f"启用工具 {tool_name} 失败")
            
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"启用工具 {tool_name} 失败: {e}")
        raise HTTPException(status_code=500, detail=f"启用工具失败: {str(e)}")


@router.post("/tools/{tool_name}/disable", response_model=APIResponse)
async def disable_tool(tool_name: str):
    """
    禁用指定的MCP工具
    
    Args:
        tool_name: 工具名称
        
    Returns:
        操作结果响应
    """
    try:
        success = await mcp_manager.disable_tool(tool_name)
        
        if success:
            LOGGER.info(f"MCP工具 {tool_name} 禁用成功")
            return APIResponse(
                success=True,
                message=f"工具 {tool_name} 禁用成功",
                data={"tool_name": tool_name, "enabled": False}
            )
        else:
            raise HTTPException(status_code=400, detail=f"禁用工具 {tool_name} 失败")
            
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"禁用工具 {tool_name} 失败: {e}")
        raise HTTPException(status_code=500, detail=f"禁用工具失败: {str(e)}")


@router.post("/tools/batch", response_model=APIResponse)
async def batch_update_tools(request: dict):
    """
    批量更新MCP工具状态
    
    Args:
        updates: 工具状态更新列表
        
    Returns:
        批量操作结果响应
    """
    try:
        tools_updates = request.get("tools", {})
        results = []
        success_count = 0
        
        for tool_name, enabled in tools_updates.items():
            try:
                if enabled:
                    success = await mcp_manager.enable_tool(tool_name)
                else:
                    success = await mcp_manager.disable_tool(tool_name)
                
                if success:
                    success_count += 1
                    results.append({
                        "tool_name": tool_name,
                        "success": True,
                        "message": f"工具 {tool_name} {'启用' if enabled else '禁用'}成功"
                    })
                else:
                    results.append({
                        "tool_name": tool_name,
                        "success": False,
                        "message": f"工具 {tool_name} {'启用' if enabled else '禁用'}失败"
                    })
                    
            except Exception as e:
                results.append({
                    "tool_name": tool_name,
                    "success": False,
                    "message": f"操作失败: {str(e)}"
                })
        
        total_updates = len(tools_updates)
        LOGGER.info(f"批量更新MCP工具状态完成，成功 {success_count}/{total_updates} 个")
        
        return APIResponse(
            success=True,
            message=f"批量更新完成，成功 {success_count}/{total_updates} 个工具",
            data={
                "results": results,
                "updated_count": success_count,
                "total_count": total_updates,
                "failed_count": total_updates - success_count
            }
        )
        
    except Exception as e:
        LOGGER.error(f"批量更新MCP工具状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")


@router.get("/status", response_model=APIResponse)
async def get_mcp_status():
    """
    获取MCP服务整体状态
    
    Returns:
        MCP服务状态信息
    """
    try:
        tools_info = await mcp_manager.get_all_tools_info()
        
        total_tools = len(tools_info)
        enabled_tools = len([t for t in tools_info if t["enabled"]])
        disabled_tools = total_tools - enabled_tools
        
        status = "healthy" if total_tools > 0 else "no_tools"
        if total_tools > 0 and enabled_tools == 0:
            status = "all_disabled"
        elif total_tools > 0 and disabled_tools == 0:
            status = "all_enabled"
        elif total_tools > 0:
            status = "partial_enabled"
        
        import time
        uptime_seconds = int(time.time() - getattr(get_mcp_status, '_start_time', time.time()))
        if not hasattr(get_mcp_status, '_start_time'):
            get_mcp_status._start_time = time.time()
        
        return APIResponse(
            success=True,
            message="获取MCP状态成功",
            data={
                "status": status,
                "total_tools": total_tools,
                "enabled_tools": enabled_tools,
                "disabled_tools": disabled_tools,
                "server_name": "FNewsCrawler",
                "server_running": True,
                "uptime": f"{uptime_seconds}秒"
            }
        )
        
    except Exception as e:
        LOGGER.error(f"获取MCP状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取MCP状态失败: {str(e)}")


@router.get("/call_tool/{tool_name}", response_model=APIResponse)
async def call_mcp_tool(tool_name: str, request: Request):
    """
    调用指定的MCP工具

    Args:
        tool_name: 工具名称
        request: 请求对象，包含查询参数

    Returns:
        工具执行结果
    """
    try:
        params = dict(request.query_params)
        result = await mcp_manager.call_tool(tool_name, **params)
        return APIResponse(
            success=True,
            message=f"调用工具 {tool_name} 成功",
            data=result
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"调用工具 {tool_name} 失败: {str(e)}",
        )
