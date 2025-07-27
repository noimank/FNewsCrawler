import asyncio
import time
from typing import Optional

from playwright.async_api import async_playwright, Browser, Playwright

from fnewscrawler.utils.logger import LOGGER


class BrowserManager:
    """
    生产级单例浏览器管理器，支持高并发访问和自动恢复
    """
    _instance: Optional['BrowserManager'] = None
    _init_lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_init_done'):
            return

        self._browser: Optional[Browser] = None
        self._playwright: Optional[Playwright] = None
        self._browser_lock = asyncio.Lock()
        self._is_initializing = False
        self._last_health_check = 0
        self._health_check_interval = 30  # 30秒健康检查间隔
        self._max_retry_attempts = 3
        self._retry_delay = 2  # 重试延迟
        self._init_done = True

        LOGGER.info("BrowserManager 实例已创建")

    async def _is_browser_healthy(self) -> bool:
        """检查浏览器是否健康可用"""
        try:
            if not self._browser:
                return False

            # 检查连接状态
            if not self._browser.is_connected():
                return False

            # 尝试获取浏览器版本作为健康检查
            version =  self._browser
            return bool(version)
        except Exception as e:
            LOGGER.warning(f"浏览器健康检查失败: {e}")
            return False

    async def _cleanup_browser_resources(self) -> None:
        """清理浏览器资源"""
        if self._browser:
            try:
                if self._browser.is_connected():
                    await self._browser.close()
                    LOGGER.info("浏览器实例已关闭")
            except Exception as e:
                LOGGER.warning(f"关闭浏览器时发生错误: {e}")
            finally:
                self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
                LOGGER.info("Playwright 实例已停止")
            except Exception as e:
                LOGGER.warning(f"停止 Playwright 时发生错误: {e}")
            finally:
                self._playwright = None

    async def _initialize_browser(self) -> None:
        """内部浏览器初始化方法"""
        if self._is_initializing:
            # 如果正在初始化，等待完成
            while self._is_initializing:
                await asyncio.sleep(0.1)
            return

        self._is_initializing = True
        try:
            LOGGER.info("正在启动 Playwright 浏览器...")

            # 清理旧资源
            await self._cleanup_browser_resources()

            # 启动新的浏览器实例
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # 可选：禁用图片加载以提高性能
                ]
            )

            # 验证浏览器是否正常工作
            if not await self._is_browser_healthy():
                raise RuntimeError("浏览器启动后健康检查失败")

            self._last_health_check = time.time()
            LOGGER.info("Playwright 浏览器启动成功")

        except Exception as e:
            LOGGER.error(f"初始化浏览器失败: {e}")
            await self._cleanup_browser_resources()
            raise
        finally:
            self._is_initializing = False

    async def initialize(self) -> None:
        """公共初始化方法"""
        async with self._init_lock:
            if await self._is_browser_healthy():
                return
            await self._initialize_browser()

    async def get_browser(self) -> Browser:
        """获取浏览器实例，支持自动重连和错误恢复"""
        async with self._browser_lock:
            current_time = time.time()

            # 定期健康检查
            if (current_time - self._last_health_check) > self._health_check_interval:
                if not await self._is_browser_healthy():
                    LOGGER.warning("定期健康检查失败，重新初始化浏览器")
                    await self._initialize_browser()
                else:
                    self._last_health_check = current_time

            # 如果浏览器不健康，尝试重新初始化
            if not await self._is_browser_healthy():
                for attempt in range(self._max_retry_attempts):
                    try:
                        LOGGER.info(f"浏览器不可用，尝试重新初始化 (第 {attempt + 1}/{self._max_retry_attempts} 次)")
                        await self._initialize_browser()
                        break
                    except Exception as e:
                        LOGGER.error(f"第 {attempt + 1} 次初始化失败: {e}")
                        if attempt < self._max_retry_attempts - 1:
                            await asyncio.sleep(self._retry_delay * (attempt + 1))  # 指数退避
                        else:
                            raise RuntimeError(f"经过 {self._max_retry_attempts} 次尝试后仍无法初始化浏览器")

            if not self._browser or not await self._is_browser_healthy():
                raise RuntimeError("无法获取健康的浏览器实例")

            return self._browser

    async def create_context(self, **kwargs):
        """创建新的浏览器上下文，推荐的高并发使用方式"""
        browser = await self.get_browser()
        return await browser.new_context(**kwargs)

    async def get_browser_info(self) -> dict:
        """获取浏览器信息用于监控"""
        try:
            if not self._browser:
                return {"status": "not_initialized"}

            if not self._browser.is_connected():
                return {"status": "disconnected"}

            version =  self._browser.version
            contexts = self._browser.contexts

            return {
                "status": "healthy",
                "version": version,
                "context_count": len(contexts),
                "last_health_check": self._last_health_check,
                "is_connected": self._browser.is_connected()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def force_restart(self) -> None:
        """强制重启浏览器（用于故障恢复）"""
        async with self._browser_lock:
            LOGGER.info("强制重启浏览器...")
            await self._cleanup_browser_resources()
            await self._initialize_browser()
            LOGGER.info("浏览器强制重启完成")

    async def close(self) -> None:
        """优雅关闭浏览器管理器"""
        async with self._browser_lock:
            LOGGER.info("正在关闭 BrowserManager...")
            self._is_initializing = False
            await self._cleanup_browser_resources()
            LOGGER.info("BrowserManager 已关闭")

    async def __aenter__(self):
        """异步上下文管理器支持"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器支持"""
        await self.close()


# 单例实例
browser_manager = BrowserManager()

