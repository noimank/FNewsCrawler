from abc import ABC, abstractmethod
from typing import Tuple, List

from fnewscrawler.core.browser import browser_manager
from fnewscrawler.core.context import context_manager


class QRLoginBase(ABC):
    _instance = None
    """通用二维码登录基类"""
    def __init__(self) -> None:
        """初始化二维码登录基类"""
        self.browser_manager = browser_manager
        self.context_manager = context_manager

    def __new__(cls, *args, **kwargs):
        """
        单例模式，确保只有一个实例，减少实例化开销
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    @abstractmethod
    async def get_qr_code(self, qr_type: str = "微信") -> Tuple[bool, str]:
        """
        获取登录二维码
        Args:
            qr_type (str, optional): 二维码类型. Defaults to "微信".
        Returns:
            Tuple[bool, str]: (是否成功, 二维码URL或错误信息)
        """
        raise NotImplementedError


    @abstractmethod
    async def verify_login_success(self) -> bool:
        """
        该函数是get_qr_code公用一个page，在用户扫码后验证登录是否成功，编写时不要抛出错误，必须能正确返回
        Returns:
            bool: 登录是否成功
        """
        raise NotImplementedError

    @abstractmethod
    async def save_context_state(self):
        """
        保存浏览器状态到Redis
        """
        raise NotImplementedError

          
    @abstractmethod
    async def get_login_status(self) -> bool:
        """
        该函数是新开一个页面获取登录状态，编写时不要抛出错误，必须能正确返回
        Returns:
            bool: 是否已经登录
        """
        raise NotImplementedError

    @abstractmethod
    async def clean_login_state(self) -> bool:
        """
        清理登录状态，编写时不要抛出错误，必须能正确返回
        Returns:
            bool: 清理是否成功
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> bool:
        """
        关闭浏览器页面，释放资源，编写时不要抛出错误，必须能正确返回
        Returns:
            bool: 关闭是否成功
        """
        raise NotImplementedError

    @abstractmethod
    def get_supported_qr_types(self) -> List[str]:
        """
        获取支持的二维码类型
        Returns:
            List[str]: 支持的二维码类型列表
        """
        raise NotImplementedError

