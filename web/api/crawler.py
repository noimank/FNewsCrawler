#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理API路由

提供新闻爬取相关的API接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
import asyncio
import time
from datetime import datetime
import uuid

from fnewscrawler.core.markdown_crawler import MarkdownCrawler
from fnewscrawler.utils.logger import LOGGER

# 创建路由器
router = APIRouter()

# 全局爬虫任务管理
crawler_tasks: Dict[str, Dict[str, Any]] = {}
crawler_results: Dict[str, Dict[str, Any]] = {}


class CrawlRequest(BaseModel):
    """爬取请求模型"""
    url: HttpUrl
    platform: str = "iwencai"
    extract_content: bool = True
    save_to_file: bool = False
    output_format: str = "markdown"  # markdown, json, html


class BatchCrawlRequest(BaseModel):
    """批量爬取请求模型"""
    urls: List[HttpUrl]
    platform: str = "iwencai"
    extract_content: bool = True
    save_to_file: bool = False
    output_format: str = "markdown"
    max_concurrent: int = 3


class CrawlResponse(BaseModel):
    """爬取响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/platforms")
async def get_supported_platforms():
    """获取支持的爬虫平台列表"""
    return {
        "success": True,
        "data": {
            "platforms": [
                {
                    "id": "iwencai",
                    "name": "问财",
                    "description": "同花顺问财平台新闻爬取",
                    "supported_formats": ["markdown", "json", "html"]
                }
            ]
        }
    }


@router.post("/crawl")
async def crawl_single_url(request: CrawlRequest, background_tasks: BackgroundTasks):
    """爬取单个URL"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 记录任务开始
        crawler_tasks[task_id] = {
            "url": str(request.url),
            "platform": request.platform,
            "status": "running",
            "start_time": time.time(),
            "output_format": request.output_format
        }
        
        # 启动后台爬取任务
        background_tasks.add_task(
            _crawl_single_task,
            task_id,
            request
        )
        
        return CrawlResponse(
            success=True,
            message="爬取任务已启动",
            data={
                "task_id": task_id,
                "url": str(request.url),
                "platform": request.platform
            }
        )
        
    except Exception as e:
        LOGGER.error(f"启动爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动爬取任务失败: {str(e)}")


@router.post("/crawl/batch")
async def crawl_batch_urls(request: BatchCrawlRequest, background_tasks: BackgroundTasks):
    """批量爬取URL"""
    try:
        # 生成批次ID
        batch_id = str(uuid.uuid4())
        
        # 记录批次任务
        crawler_tasks[batch_id] = {
            "type": "batch",
            "urls": [str(url) for url in request.urls],
            "platform": request.platform,
            "status": "running",
            "start_time": time.time(),
            "total_urls": len(request.urls),
            "completed_urls": 0,
            "output_format": request.output_format
        }
        
        # 启动后台批量爬取任务
        background_tasks.add_task(
            _crawl_batch_task,
            batch_id,
            request
        )
        
        return CrawlResponse(
            success=True,
            message="批量爬取任务已启动",
            data={
                "batch_id": batch_id,
                "total_urls": len(request.urls),
                "platform": request.platform
            }
        )
        
    except Exception as e:
        LOGGER.error(f"启动批量爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动批量爬取任务失败: {str(e)}")


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """获取爬取任务状态"""
    try:
        if task_id not in crawler_tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task_info = crawler_tasks[task_id]
        
        # 计算运行时间
        elapsed_time = time.time() - task_info["start_time"]
        
        response_data = {
            "task_id": task_id,
            "status": task_info["status"],
            "elapsed_time": int(elapsed_time)
        }
        
        # 添加任务特定信息
        if task_info.get("type") == "batch":
            response_data.update({
                "type": "batch",
                "total_urls": task_info["total_urls"],
                "completed_urls": task_info["completed_urls"],
                "progress": task_info["completed_urls"] / task_info["total_urls"] * 100
            })
        else:
            response_data.update({
                "type": "single",
                "url": task_info["url"]
            })
        
        # 如果任务完成，添加结果
        if task_info["status"] == "completed" and task_id in crawler_results:
            response_data["result"] = crawler_results[task_id]
        elif task_info["status"] == "failed":
            response_data["error"] = task_info.get("error", "未知错误")
        
        return CrawlResponse(
            success=True,
            message="获取任务状态成功",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """获取爬取任务结果"""
    try:
        if task_id not in crawler_results:
            if task_id not in crawler_tasks:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            task_status = crawler_tasks[task_id]["status"]
            if task_status == "running":
                raise HTTPException(status_code=202, detail="任务正在运行中")
            elif task_status == "failed":
                raise HTTPException(status_code=400, detail="任务执行失败")
            else:
                raise HTTPException(status_code=404, detail="任务结果不存在")
        
        result = crawler_results[task_id]
        
        return CrawlResponse(
            success=True,
            message="获取任务结果成功",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"获取任务结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除爬取任务"""
    try:
        # 删除任务记录
        if task_id in crawler_tasks:
            del crawler_tasks[task_id]
        
        # 删除结果记录
        if task_id in crawler_results:
            del crawler_results[task_id]
        
        return CrawlResponse(
            success=True,
            message="任务已删除"
        )
        
    except Exception as e:
        LOGGER.error(f"删除任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/tasks")
async def get_all_tasks():
    """获取所有爬取任务"""
    try:
        current_time = time.time()
        tasks_list = []
        
        for task_id, task_info in crawler_tasks.items():
            elapsed_time = current_time - task_info["start_time"]
            
            task_data = {
                "task_id": task_id,
                "status": task_info["status"],
                "elapsed_time": int(elapsed_time),
                "platform": task_info["platform"]
            }
            
            if task_info.get("type") == "batch":
                task_data.update({
                    "type": "batch",
                    "total_urls": task_info["total_urls"],
                    "completed_urls": task_info["completed_urls"]
                })
            else:
                task_data.update({
                    "type": "single",
                    "url": task_info["url"]
                })
            
            tasks_list.append(task_data)
        
        return {
            "success": True,
            "data": {
                "tasks": tasks_list,
                "total": len(tasks_list)
            }
        }
        
    except Exception as e:
        LOGGER.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


async def _crawl_single_task(task_id: str, request: CrawlRequest):
    """执行单个爬取任务"""
    try:
        LOGGER.info(f"开始执行爬取任务: {task_id}, URL: {request.url}")
        
        # 创建爬虫实例
        crawler = MarkdownCrawler()
        
        # 执行爬取
        result = await crawler.crawl_url(
            url=str(request.url),
            platform=request.platform,
            extract_content=request.extract_content
        )
        
        # 保存结果
        crawler_results[task_id] = {
            "url": str(request.url),
            "platform": request.platform,
            "content": result.get("content", ""),
            "title": result.get("title", ""),
            "metadata": result.get("metadata", {}),
            "crawl_time": datetime.now().isoformat(),
            "format": request.output_format
        }
        
        # 更新任务状态
        crawler_tasks[task_id]["status"] = "completed"
        crawler_tasks[task_id]["end_time"] = time.time()
        
        LOGGER.info(f"爬取任务完成: {task_id}")
        
    except Exception as e:
        LOGGER.error(f"爬取任务失败: {task_id}, 错误: {e}")
        crawler_tasks[task_id]["status"] = "failed"
        crawler_tasks[task_id]["error"] = str(e)
        crawler_tasks[task_id]["end_time"] = time.time()


async def _crawl_batch_task(batch_id: str, request: BatchCrawlRequest):
    """执行批量爬取任务"""
    try:
        LOGGER.info(f"开始执行批量爬取任务: {batch_id}, URLs数量: {len(request.urls)}")
        
        # 创建爬虫实例
        crawler = MarkdownCrawler()
        
        # 批量结果
        batch_results = []
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def crawl_single_url(url: str):
            async with semaphore:
                try:
                    result = await crawler.crawl_url(
                        url=url,
                        platform=request.platform,
                        extract_content=request.extract_content
                    )
                    
                    return {
                        "url": url,
                        "success": True,
                        "content": result.get("content", ""),
                        "title": result.get("title", ""),
                        "metadata": result.get("metadata", {})
                    }
                except Exception as e:
                    LOGGER.error(f"爬取URL失败: {url}, 错误: {e}")
                    return {
                        "url": url,
                        "success": False,
                        "error": str(e)
                    }
                finally:
                    # 更新完成数量
                    crawler_tasks[batch_id]["completed_urls"] += 1
        
        # 并发执行所有URL爬取
        tasks = [crawl_single_url(str(url)) for url in request.urls]
        batch_results = await asyncio.gather(*tasks)
        
        # 保存批量结果
        crawler_results[batch_id] = {
            "type": "batch",
            "total_urls": len(request.urls),
            "results": batch_results,
            "crawl_time": datetime.now().isoformat(),
            "format": request.output_format,
            "success_count": sum(1 for r in batch_results if r["success"]),
            "failed_count": sum(1 for r in batch_results if not r["success"])
        }
        
        # 更新任务状态
        crawler_tasks[batch_id]["status"] = "completed"
        crawler_tasks[batch_id]["end_time"] = time.time()
        
        LOGGER.info(f"批量爬取任务完成: {batch_id}")
        
    except Exception as e:
        LOGGER.error(f"批量爬取任务失败: {batch_id}, 错误: {e}")
        crawler_tasks[batch_id]["status"] = "failed"
        crawler_tasks[batch_id]["error"] = str(e)
        crawler_tasks[batch_id]["end_time"] = time.time()