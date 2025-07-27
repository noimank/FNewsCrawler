from .utils.logger import LOGGER
from .utils.path import get_project_root

from dotenv import load_dotenv
import os

#尝试加载项目目录下的.env文件
if os.path.exists(os.path.join(get_project_root(), ".env")):
    load_dotenv(os.path.join(get_project_root(), ".env"))
else:
    LOGGER.warning(f"{get_project_root()}目录下的 .env 不存在，必要的环境变量有可能无法设置")


#涉及到环境变量的库应该在导入环境变量后导入
from .core.browser import browser_manager
from .core.context import context_manager