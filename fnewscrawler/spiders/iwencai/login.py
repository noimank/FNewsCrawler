# !/usr/bin/env python3
# -*- coding: utf-8 -*-  
"""  
问财登录管理器  

处理问财网站的登录逻辑，支持多种登录方式  
"""
import asyncio
from typing import Tuple, List

from fnewscrawler.core.qr_login_base import QRLoginBase
from fnewscrawler.utils.logger import LOGGER

class IwencaiLogin(QRLoginBase):
    """  
    问财登录管理器  
    """
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.iwencai.com/unifiedwap/home/index"
        # self.page_lock = asyncio.Lock()
        self.login_page = None
        self.popup_page = None  # 保存微信登录弹窗引用  

    async def init_env(self):
        context = await self.context_manager.get_context("iwencai")
        self.login_page = await context.new_page()
        #关闭可能残留的弹窗
        await self.close_popup()

    def _has_inited(self):
            if  self.login_page is None:
                return False
            return True

    def _has_popup(self):
        """检查是否有微信登录弹窗"""
        return self.popup_page is not None

    async def close_popup(self):
        """关闭微信登录弹窗"""
        try:
            if self._has_popup():
                await self.popup_page.close()
                self.popup_page = None
                return True
        except Exception as e:
            LOGGER.error(f"关闭微信登录弹窗失败: {e}")
        return False


    async def get_weixin_qr_code(self):
        try:
            if not self._has_inited():
                await self.init_env()

            await self.login_page.goto(self.base_url)
            await self.login_page.wait_for_load_state("domcontentloaded")

            if await self.verify_login_success():
                await self.close()
                return True, "已经登录"

            # 1. 点击"注册 / 登录"按钮以触发登录弹窗
            # print("正在点击 '注册 / 登录'...")
            await self.login_page.locator("text=注册 / 登录").hover()
            await self.login_page.locator("text=注册 / 登录").click()

            # print("等待登录弹窗容器可见...")
            await self.login_page.locator(".login-window-wrap").wait_for(state="visible", timeout=10000)
            # print("登录弹窗容器已可见。")

            # 3. 正确获取 iframe 元素并切换到 iframe 上下文
            # print("定位并切换到登录 iframe...")
            # 等待 iframe 加载完成
            await self.login_page.wait_for_selector("#login_iframe", state="visible", timeout=10000)

            # 获取 iframe 句柄
            frame = self.login_page.frame_locator("#login_iframe")

            # 使用多种选择器策略来定位微信登录按钮
            wechat_login_button = frame.locator(".btn_elem[l_type=weixin]")

            # 等待按钮可点击
            await wechat_login_button.wait_for(state="visible", timeout=10000)

            # 5. 设置弹窗监听并点击微信登录
            async with self.login_page.expect_popup() as popup_info:
                await wechat_login_button.click()
                # print("已点击微信登录按钮。")

            # 6. 处理微信登录弹窗
            # print("正在等待微信登录弹窗出现...")
            self.popup_page = await popup_info.value  # 保存弹窗引用
            # 等待弹窗页面完全加载
            await self.popup_page.wait_for_load_state("networkidle")
            # print("微信登录弹窗已加载。")

            # 7. 获取二维码图片URL
            qr_code_selector = ".js_qrcode_img.web_qrcode_img"
            await self.popup_page.wait_for_selector(qr_code_selector, state="visible")
            qr_code_url = await self.popup_page.locator(qr_code_selector).first.get_attribute("src")
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

    async def get_QQ_qr_code(self):
        try:
            if not self._has_inited():
                await self.init_env()

            await self.login_page.goto(self.base_url)
            await self.login_page.wait_for_load_state("domcontentloaded")

            if await self.verify_login_success():
                await self.close()
                return True, "已经登录"

                # 1. 点击"注册 / 登录"按钮以触发登录弹窗
            # print("正在点击 '注册 / 登录'...")
            await self.login_page.locator("text=注册 / 登录").hover()
            await self.login_page.locator("text=注册 / 登录").click()

            # 2. 等待包含 iframe 的容器变得可见
            # print("等待登录弹窗容器可见...")
            await self.login_page.locator(".login-window-wrap").wait_for(state="visible", timeout=10000)
            # print("登录弹窗容器已可见。")
            # 等待 iframe 加载完成
            await self.login_page.wait_for_selector("#login_iframe", state="visible", timeout=10000)

            # 获取 iframe 句柄
            frame = self.login_page.frame_locator("#login_iframe")

            # 使用多种选择器策略来定位QQ登录按钮
            qq_login_button = frame.locator(".btn_elem[l_type=qq]")

            # 等待按钮可点击
            await qq_login_button.wait_for(state="visible", timeout=10000)

            # 5. 设置弹窗监听并点击QQ登录
            async with self.login_page.expect_popup() as popup_info:
                await qq_login_button.click()
                # print("已点击QQ登录按钮。")
            # 6. 处理QQ登录弹窗
            # print("正在等待QQ登录弹窗出现...")
            self.popup_page = await popup_info.value  # 保存弹窗引用
            # 等待弹窗页面完全加载
            await self.popup_page.wait_for_load_state("networkidle")
            # print("QQ登录弹窗已加载。")

            #获取弹窗的内部iframe
            inner_frame = self.popup_page.frame_locator("#ptlogin_iframe")
            # 7. 获取二维码图片URL
            qr_code_selector = "#qrlogin_img.qrImg"
            await inner_frame.locator(qr_code_selector).wait_for(state="visible", timeout=5000)
            qr_code_url = await inner_frame.locator(qr_code_selector).first.get_attribute("src")
            # print(f"获取到二维码URL：{qr_code_url}")
            LOGGER.info(f"获取到QQ登录二维码URL：{qr_code_url}")

            return True, qr_code_url

        except TimeoutError as e:
            error_msg = f"等待QQ登录弹窗元素超时: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"获取QQ登录二维码过程中发生错误: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg


    async def get_THS_qr_code(self):
        """
        获取同花顺登录二维码
        """
        try:
            if not self._has_inited():
                await self.init_env()

            await self.login_page.goto(self.base_url)
            await self.login_page.wait_for_load_state("domcontentloaded")

            if await self.verify_login_success():
                await self.close()
                return True, "已经登录"

             # 1. 点击"注册 / 登录"按钮以触发登录弹窗
            # print("正在点击 '注册 / 登录'...")
            await self.login_page.locator("text=注册 / 登录").hover()
            await self.login_page.locator("text=注册 / 登录").click()

            # 2. 等待包含 iframe 的容器变得可见
            # print("等待登录弹窗容器可见...")
            await self.login_page.locator(".login-window-wrap").wait_for(state="visible", timeout=10000)
#             print("登录弹窗容器已可见。")

            # 3. 正确获取 iframe 元素并切换到 iframe 上下文
            # print("定位并切换到登录 iframe...")
            # 等待 iframe 加载完成
            await self.login_page.wait_for_selector("#login_iframe", state="visible", timeout=10000)

            # 获取 iframe 句柄
            frame = self.login_page.frame_locator("#login_iframe")

            # 使用多种选择器策略来定位微信登录按钮
            qr_login_button = frame.locator("#to_qrcode_login")

            # 等待按钮可点击
            await qr_login_button.wait_for(state="visible", timeout=10000)

            # 5. 设置弹窗监听并点击同花顺登录
            await qr_login_button.click()
            await asyncio.sleep(2)

            # 7. 获取二维码图片URL
            qr_code_selector = ".code-box img"
            await frame.locator(qr_code_selector).wait_for(state="visible", timeout=5000)
            qr_code_url = await frame.locator(qr_code_selector).first.get_attribute("src")
            if qr_code_url.startswith("/"):
                qr_code_url = "https://upass.iwencai.com" + qr_code_url
            # print(f"获取到二维码URL：{qr_code_url}")
            LOGGER.info(f"获取到同花顺登录二维码: {qr_code_url}")

            return True, qr_code_url

        except TimeoutError as e:
            error_msg = f"等待同花顺登录二维码页面元素超时: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"获取同花顺登录二维码过程中发生错误: {str(e)}"
            LOGGER.error(error_msg)
            return False, error_msg

    async def get_qr_code(self, qr_type: str = "微信") -> Tuple[bool, str]:
        """获取登录二维码  
        Args:            qr_type (str, optional): 二维码类型. Defaults to "微信".  
        Returns:            Tuple[bool, str]: (是否成功, 二维码URL或错误信息)  
        """
        if qr_type == "微信":
            return await self.get_weixin_qr_code()
        elif qr_type == "QQ":
            return await self.get_QQ_qr_code()
        elif qr_type == "同花顺":
            return await self.get_THS_qr_code()
        else:
            return False, "不支持的二维码登录方式"

    async def verify_login_success(self) -> bool:
        """  
        验证登录是否成功  
        """
        try:
            # 检查是否已初始化  
            if not self._has_inited():
                # print(" page：",  self.login_page)
                return False

                # 等待登录成功的标志元素出现
            await self.login_page.wait_for_selector(".login-box .user-photo", state="visible", timeout=3000)
            return True
        except Exception as e:
            return False

    async def get_login_status(self) -> bool:
        """获取登录状态（会自动关闭浏览器）"""
        # print("browser， context：", id(self.browser_manager._browser), id(self.context_manager._contexts.get("iwencai", "NNN")))
        temp_page = None
        try:
            context = await  self.context_manager.get_context("iwencai")
            temp_page = await context.new_page()
            await temp_page.goto(self.base_url)
            await temp_page.wait_for_load_state("domcontentloaded")
            await temp_page.wait_for_selector(".login-box .user-photo", state="visible", timeout=3000)
            return True
        except Exception as e:
            LOGGER.error(f"获取登录状态失败: {e}")
            return False
        finally:
            if temp_page:
                await temp_page.close()

    async def check_login_status_without_close(self) -> bool:
        """检查登录状态（不关闭浏览器，用于二维码登录过程中）"""
        try:
            # 检查是否已初始化  
            if not self._has_inited():
                print(" page：",  self.login_page)
                return False

                # 直接验证登录状态，不重新导航
            return await self.verify_login_success()

        except Exception as e:
            LOGGER.error(f"检查登录状态失败: {e}")
            return False

    async def save_context_state(self):
        """  
        保存浏览器状态到Redis  
        """
        try:
            flag = await self.context_manager.save_context_state("iwencai")
            return flag

        except Exception as e:
            LOGGER.error(f"保存浏览器状态失败: {e}")
            return False

    async def close(self) -> bool:
        if self._has_inited():
            if self._has_popup():
                await self.close_popup()
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
        flag = await self.context_manager.delete_context_state("iwencai")
        return flag == 1
    
    def get_supported_qr_types(self) -> List[str]:
        """
        获取支持的二维码类型
        Returns:
            List[str]: 支持的二维码类型列表
        """
        return ["微信", "同花顺"]

