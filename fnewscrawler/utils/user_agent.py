import random
from fake_useragent import UserAgent, FakeUserAgentError
from fnewscrawler.utils import LOGGER

# 预定义一些常用的 Chrome User-Agent 作为备用
CHROME_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_random_user_agent():
    """
    获取一个随机的 Chrome 浏览器 User-Agent。
    尝试使用 fake-useragent 库，如果失败则从预定义的列表中随机选择一个。

    Returns:
        str: 一个随机的 Chrome User-Agent 字符串。
    """
    try:
        # 尝试从在线数据库获取
        ua = UserAgent(browsers=['Chrome'],os='Windows', platforms='desktop')
        random_ua = ua.chrome
        return random_ua
    except FakeUserAgentError as e:
        # 如果 fake-useragent 特定错误发生
        LOGGER.warning(f"FakeUserAgentError: {e}. Falling back to predefined list.")
    except Exception as e:
        # 其他异常
        LOGGER.error(f"Unexpected error fetching User-Agent: {e}. Falling back to predefined list.")

    # 从预定义列表中随机选择一个
    return random.choice(CHROME_USER_AGENTS)

