import json
import asyncio
import json
import os
import time
from typing import Dict, Any, Optional, Set

from playwright.async_api import BrowserContext, Error

from fnewscrawler.core.browser import browser_manager
from fnewscrawler.core.redis_manager import get_redis
from fnewscrawler.utils import get_random_user_agent
from fnewscrawler.utils.logger import LOGGER


class ContextManager:
    """
    生产级浏览器上下文管理器，支持高并发访问、自动清理和状态恢复
    """

    def __init__(self):
        self._contexts: Dict[str, BrowserContext] = {}
        self._context_locks: Dict[str, asyncio.Lock] = {}  # 每个站点独立的锁
        self._global_lock = asyncio.Lock()  # 全局锁
        self._context_creation_time: Dict[str, float] = {}
        self._context_last_used: Dict[str, float] = {}
        self._context_usage_count: Dict[str, int] = {}
        self._creating_contexts: Set[str] = set()  # 正在创建的上下文

        # 配置参数
        self._max_idle_time = int(os.environ.get("PW_CONTEXT_MAX_IDLE_TIME", 3600))  # 最大空闲时间（秒）
        self._health_check_interval = int(os.environ.get("PW_CONTEXT_HEALTH_CHECK_TIME", 300))  # 健康检查间隔（秒）

        # 清理任务相关
        self._cleanup_task = None
        self._cleanup_task_started = False

        LOGGER.info("生产级 ContextManager 实例已创建")

    def _start_cleanup_task(self):
        """启动后台清理任务 - 延迟到首次使用时启动"""
        if self._cleanup_task_started:
            return

        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()

            async def cleanup_worker():
                while True:
                    try:
                        await asyncio.sleep(self._health_check_interval)
                        await self._cleanup_expired_contexts()
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        LOGGER.error(f"清理任务异常: {e}")

            self._cleanup_task = asyncio.create_task(cleanup_worker())
            self._cleanup_task_started = True
            LOGGER.info("后台清理任务已启动")

        except RuntimeError:
            # 没有运行的事件循环，延迟到首次调用时启动
            LOGGER.warning("没有运行的事件循环，清理任务将在首次使用时启动")

    async def _ensure_cleanup_task_started(self):
        """确保清理任务已启动"""
        if not self._cleanup_task_started:
            self._start_cleanup_task()

    async def _cleanup_expired_contexts(self):
        """清理过期的上下文"""
        current_time = time.time()
        expired_sites = []

        async with self._global_lock:
            for site_name in list(self._contexts.keys()):
                # creation_time = self._context_creation_time.get(site_name, 0)
                last_used = self._context_last_used.get(site_name, 0)

                # 检查是否过期
                # age = current_time - creation_time
                idle_time = current_time - last_used
                if self._max_idle_time <=0:
                    continue

                if  idle_time > self._max_idle_time:
                    expired_sites.append(site_name)

        # 清理过期上下文
        for site_name in expired_sites:
            try:
                await self._force_close_context(site_name, reason="expired")
            except Exception as e:
                LOGGER.error(f"清理过期上下文 {site_name} 失败: {e}")

    async def _get_site_lock(self, site_name: str) -> asyncio.Lock:
        """获取站点专用锁"""
        if site_name not in self._context_locks:
            async with self._global_lock:
                if site_name not in self._context_locks:
                    self._context_locks[site_name] = asyncio.Lock()
        return self._context_locks[site_name]

    async def _get_storage_state(self, site_name: str) -> Optional[Dict[str, Any]]:
        """从Redis加载指定网站的登录状态，支持连接池和超时"""
        try:
            r = get_redis()
            state_json = r.get(f'playwright:auth:{site_name}')
            if state_json:
                LOGGER.info(f"从Redis加载 {site_name} 的登录状态")
                return json.loads(state_json)
            return None

        except json.JSONDecodeError as e:
            LOGGER.error(f"解析 {site_name} 登录状态JSON失败: {e}")
        except Exception as e:
            LOGGER.warning(f"从Redis加载 {site_name} 登录状态失败: {e}")
        return None

    async def _is_context_healthy(self, context: BrowserContext) -> bool:
        """检查上下文是否健康"""
        try:
            if not context:
                return False

            # 检查浏览器连接状态
            browser = context.browser
            if not browser or not browser.is_connected():
                return False

            # 轻量级健康检查
            pages = context.pages
            return pages is not None

        except Exception as e:
            LOGGER.debug(f"上下文健康检查失败: {e}")
            return False

    async def _create_new_context(self, site_name: str) -> BrowserContext:
        """创建新的浏览器上下文"""
        browser = await browser_manager.get_browser()
        storage_state = await self._get_storage_state(site_name)

        # 反爬虫脚本
        anti_detection_script = """
            // 隐藏webdriver标识
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 隐藏自动化相关属性
            delete navigator.__proto__.webdriver;

            // 伪造chrome属性
            Object.defineProperty(window, 'chrome', {
                writable: true,
                enumerable: true,
                configurable: false,
                value: {
                    runtime: {},
                    csi: function() {},
                    loadTimes: function() {}
                }
            });

            // 伪造插件
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 隐藏自动化检测
            const originalQuery = window.document.querySelector;
            window.document.querySelector = function(selector) {
                if (selector === 'img[src*="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="]') {
                    return null;
                }
                return originalQuery.apply(this, arguments);
            };
        """

        try:
            context = await browser.new_context(
                user_agent=get_random_user_agent(),
                java_script_enabled=True,
                accept_downloads=True,
                storage_state=storage_state,
                # viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True,
                bypass_csp=True,
                # 添加额外的反检测选项
                # extra_http_headers={
                #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                #     'Accept-Encoding': 'gzip, deflate, br',
                #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                #     'Sec-Fetch-Site': 'none',
                #     'Sec-Fetch-Mode': 'navigate',
                #     'Sec-Fetch-User': '?1',
                #     'Sec-Fetch-Dest': 'document',
                #     'Upgrade-Insecure-Requests': '1',
                # }
            )

            # 注入反爬虫脚本
            await context.add_init_script(anti_detection_script)

            # 设置默认超时
            context.set_default_timeout(30000)
            context.set_default_navigation_timeout(30000)

            LOGGER.info(f"为 {site_name} 创建新的浏览器上下文成功")
            return context

        except Error as e:
            LOGGER.error(f"创建 {site_name} 上下文时发生 Playwright 错误: {e}")
            raise
        except Exception as e:
            LOGGER.error(f"创建 {site_name} 上下文时发生未知错误: {e}")
            raise

    async def get_context(self, site_name: str, force_new: bool = False) -> BrowserContext:
        """
        获取指定网站的浏览器上下文，支持高并发和自动恢复

        Args:
            site_name: 网站名称
            force_new: 是否强制创建新上下文
        """
        # 确保清理任务已启动
        await self._ensure_cleanup_task_started()

        current_time = time.time()

        # 如果不强制创建新上下文，先检查现有上下文
        if not force_new and site_name in self._contexts:
            context = self._contexts[site_name]
            if await self._is_context_healthy(context):
                # 更新使用时间和计数
                self._context_last_used[site_name] = current_time
                self._context_usage_count[site_name] = self._context_usage_count.get(site_name, 0) + 1
                return context
            else:
                # 上下文不健康，标记为需要重建
                LOGGER.warning(f"{site_name} 的上下文不健康，将重新创建")
                await self._force_close_context(site_name, reason="unhealthy")

        # 获取站点专用锁
        site_lock = await self._get_site_lock(site_name)

        async with site_lock:
            # 双重检查，防止并发创建
            if not force_new and site_name in self._contexts:
                context = self._contexts[site_name]
                if await self._is_context_healthy(context):
                    self._context_last_used[site_name] = current_time
                    self._context_usage_count[site_name] = self._context_usage_count.get(site_name, 0) + 1
                    return context

            # 检查是否正在创建中
            if site_name in self._creating_contexts:
                # 等待创建完成
                retry_count = 0
                while site_name in self._creating_contexts and retry_count < 50:  # 最多等待5秒
                    await asyncio.sleep(0.1)
                    retry_count += 1

                # 如果创建完成，返回结果
                if site_name in self._contexts:
                    context = self._contexts[site_name]
                    if await self._is_context_healthy(context):
                        self._context_last_used[site_name] = current_time
                        self._context_usage_count[site_name] = self._context_usage_count.get(site_name, 0) + 1
                        return context

            # 标记正在创建
            self._creating_contexts.add(site_name)

            try:
                LOGGER.info(f"正在为 {site_name} 创建新的浏览器上下文...")

                # 创建新上下文
                context = await self._create_new_context(site_name)

                # 保存上下文和元数据
                self._contexts[site_name] = context
                self._context_creation_time[site_name] = current_time
                self._context_last_used[site_name] = current_time
                self._context_usage_count[site_name] = 1

                LOGGER.info(f"{site_name} 上下文创建成功，当前管理 {len(self._contexts)} 个上下文")
                return context

            finally:
                # 移除创建标记
                self._creating_contexts.discard(site_name)

    async def _force_close_context(self, site_name: str, reason: str = "manual"):
        """强制关闭指定站点的上下文"""
        try:
            if site_name in self._contexts:
                context = self._contexts[site_name]
                try:
                    await context.close()
                    LOGGER.info(f"上下文 {site_name} 已关闭 (原因: {reason})")
                except Exception as e:
                    LOGGER.warning(f"关闭上下文 {site_name} 时发生错误: {e}")

                # 清理元数据
                self._contexts.pop(site_name, None)
                self._context_creation_time.pop(site_name, None)
                self._context_last_used.pop(site_name, None)
                self._context_usage_count.pop(site_name, None)

        except Exception as e:
            LOGGER.error(f"强制关闭上下文 {site_name} 失败: {e}")

    async def save_context_state(self, site_name: str) -> bool:
        """保存指定网站的登录状态到Redis"""
        if site_name not in self._contexts:
            LOGGER.warning(f"无法保存上下文状态，网站 {site_name} 的上下文不存在")
            return False

        context = self._contexts[site_name]
        try:
            # 检查上下文健康状态
            if not await self._is_context_healthy(context):
                LOGGER.warning(f"上下文 {site_name} 不健康，跳过状态保存")
                return False

            # 获取存储状态
            state_dict = await context.storage_state()
            state_json = json.dumps(state_dict, ensure_ascii=False)

            # 异步保存到Redis
            r = get_redis()
            r.set(f'playwright:auth:{site_name}', state_json)  # 24小时过期

            LOGGER.info(f"上下文状态已保存到Redis: {site_name}")
            return True

        except Exception as e:
            LOGGER.error(f"保存 {site_name} 上下文状态时发生错误: {e}")

        return False

    async def delete_context_state(self, site_name: str) -> int:
        """删除指定网站的登录状态"""
        try:
            r = get_redis()
            flag =  r.delete(f'playwright:auth:{site_name}')

            LOGGER.info(f"已从Redis删除键 playwright:auth:{site_name}")
            return flag

        except asyncio.TimeoutError:
            LOGGER.error(f"删除 {site_name} 登录状态超时")
        except Exception as e:
            LOGGER.error(f"从Redis删除 {site_name} 登录状态失败: {e}")
        return 0

    async def refresh_context(self, site_name: str) -> BrowserContext:
        """刷新指定站点的上下文"""
        LOGGER.info(f"刷新 {site_name} 的上下文")
        await self._force_close_context(site_name, reason="refresh")
        return await self.get_context(site_name, force_new=True)

    async def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文管理器统计信息"""
        current_time = time.time()
        stats = {
            "total_contexts": len(self._contexts),
            "creating_contexts": len(self._creating_contexts),
            "contexts": {}
        }

        for site_name in self._contexts:
            creation_time = self._context_creation_time.get(site_name, 0)
            last_used = self._context_last_used.get(site_name, 0)
            usage_count = self._context_usage_count.get(site_name, 0)

            stats["contexts"][site_name] = {
                "age_seconds": int(current_time - creation_time),
                "idle_seconds": int(current_time - last_used),
                "usage_count": usage_count,
                "is_healthy": await self._is_context_healthy(self._contexts[site_name])
            }

        return stats

    async def close_site_context(self, site_name: str):
        """关闭指定站点的上下文"""
        site_lock = await self._get_site_lock(site_name)
        async with site_lock:
            await self._force_close_context(site_name, reason="manual_close")

    async def close_all(self):
        """关闭所有管理的浏览器上下文实例"""
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._global_lock:
            LOGGER.info("正在关闭所有浏览器上下文...")

            # 并发关闭所有上下文
            close_tasks = []
            for site_name in list(self._contexts.keys()):
                task = asyncio.create_task(
                    self._force_close_context(site_name, reason="shutdown")
                )
                close_tasks.append(task)

            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)

            # 清理所有数据结构
            self._contexts.clear()
            self._context_locks.clear()
            self._context_creation_time.clear()
            self._context_last_used.clear()
            self._context_usage_count.clear()
            self._creating_contexts.clear()

            LOGGER.info("所有上下文已清理完毕")

    async def __aenter__(self):
        """异步上下文管理器支持"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器支持"""
        await self.close_all()


# 在模块级别创建 ContextManager 实例，方便全局访问
context_manager = ContextManager()

