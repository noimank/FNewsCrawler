# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富登录管理器

处理东方财富网站的登录逻辑，支持多种登录方式
"""
import asyncio
from typing import Tuple, List

from fnewscrawler.core.qr_login_base import QRLoginBase

from fnewscrawler.utils.logger import LOGGER


class EastMoneyLogin(QRLoginBase):
    """
    东方财富登录管理器
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://passport2.eastmoney.com/pub/login"
        self.login_page = None

    async def init_env(self):
        context = await self.context_manager.get_context("eastmoney")
        self.login_page = await context.new_page()

    def _has_inited(self):
        if self.login_page is None:
            return False
        return True


    async def get_weixin_qr_code(self):
        try:
            if not self._has_inited():
                await self.init_env()

            await self.login_page.goto(self.base_url)
            await self.login_page.wait_for_load_state("domcontentloaded")

            if await self.verify_login_success():
                await self.close()
                return True, "已经登录"

            # 1. 点击已阅读并同意 
            await self.login_page.locator("#frame_login").content_frame.locator("#mobile_login_content img").first.click()

            await self.login_page.wait_for_timeout(300)
            # 2.点击微信登录
            await self.login_page.locator("#frame_login").content_frame.locator("#btn_wx").click()
            # print("登录弹窗容器已可见。")

            await self.login_page.wait_for_load_state("networkidle")

            qr_code_url = await self.login_page.locator(".web_qrcode_img_wrp img").first.get_attribute("src")
            # 3. 正确获取 iframe 元素并切换到 iframe 上下文
            # 等待 iframe 加载完成
            if qr_code_url.startswith("/"):
                qr_code_url = "https://open.weixin.qq.com" + qr_code_url
            # print(f"获取到二维码URL：{qr_code_url}")
            LOGGER.info(f"获取到微信登录二维码URL：{qr_code_url}")
            return True, qr_code_url

        except TimeoutError as e:
            error_msg = f"等待微信登录弹窗元素超时: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"获取微信二维码过程中发生错误: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

    async def get_eastmoney_qr_code(self):
        """
        获取东方财富登录二维码
        """
        try:
            if not self._has_inited():
                await self.init_env()

            await self.login_page.goto(self.base_url)
            await self.login_page.wait_for_load_state("domcontentloaded")

            if await self.verify_login_success():
                await self.close()
                return True, "已经登录"

            # 1. 点击已阅读并同意 
            await self.login_page.locator("#frame_login").content_frame.locator("#mobile_login_content img").first.click()

            # 7. 获取二维码图片URL
            qr_code_url = await self.login_page.locator("#frame_login").content_frame.locator("#qrcode").get_attribute("src")
            if qr_code_url.startswith("//"):
                qr_code_url = "https:" + qr_code_url
            # print(f"获取到二维码URL：{qr_code_url}")
            LOGGER.info(f"获取到东方财富登录二维码: {qr_code_url}")
            return True, qr_code_url

        except TimeoutError as e:
            error_msg = f"等待东方财富登录二维码页面元素超时: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"获取东方财富登录二维码过程中发生错误: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

    async def get_qr_code(self, qr_type: str = "微信") -> Tuple[bool, str]:
        """获取登录二维码
        Args:            qr_type (str, optional): 二维码类型. Defaults to "微信".
        Returns:            Tuple[bool, str]: (是否成功, 二维码URL或错误信息)
        """
        if qr_type == "微信":
            return await self.get_weixin_qr_code()
        elif qr_type == "东方财富":
            return await self.get_eastmoney_qr_code()
        else:
            return False, "不支持的二维码登录方式"

    async def verify_login_success(self) -> bool:
        """
        验证登录是否成功
        """
        try:
            # 检查是否已初始化
            if not self._has_inited():
                return False

            # 等待登录成功的标志元素出现
            await self.login_page.wait_for_selector(".pass_tabClass", state="visible", timeout=500)
            return True
        except Exception as e:
            return False

    async def get_login_status(self) -> bool:
        """获取登录状态（会自动关闭浏览器）"""
        temp_page = None
        try:
            context = await  self.context_manager.get_context("eastmoney")
            temp_page = await context.new_page()
            await temp_page.goto("https://passport2.eastmoney.com/pub/basicinfo")
            await temp_page.wait_for_load_state("domcontentloaded")
            await temp_page.wait_for_selector(".pass_tabClass", state="visible", timeout=600)
            return True
        except Exception as e:
            LOGGER.error(f"获取登录状态失败: {e}")
            return False
        finally:
            if temp_page:
                await temp_page.close()


    async def save_context_state(self):
        """
        保存浏览器状态到Redis
        """
        try:
            flag = await self.context_manager.save_context_state("eastmoney")
            return flag

        except Exception as e:
            LOGGER.error(f"保存浏览器状态失败: {e}")
            return False

    async def close(self) -> bool:
        if self._has_inited():
            await self.login_page.close()
            self.login_page = None
            LOGGER.info("调用close方法")
            return True
        return False

    async def clean_login_state(self) -> bool:
        """
        清理登录状态
        Returns:            bool: 清理是否成功
        """
        flag = await self.context_manager.delete_context_state("eastmoney")
        return flag == 1

    def get_supported_qr_types(self) -> List[str]:
        """
        获取支持的二维码类型
        Returns:
            List[str]: 支持的二维码类型列表
        """
        return ["微信", "东方财富"]

