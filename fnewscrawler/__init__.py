from dotenv import load_dotenv
import os
#获取上一级目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#尝试加载项目目录下的.env文件
if os.path.exists(os.path.join(BASE_DIR, ".env")):
    load_dotenv(os.path.join(BASE_DIR, ".env"))
else:
    print(f"[FNewsCrawler]-> {BASE_DIR}目录下的 .env 不存在，必要的环境变量有可能无法设置")

from .utils.path import get_project_root
from .utils.logger import LOGGER


#涉及到环境变量的库应该在导入环境变量后导入
from .core.browser import browser_manager
from .core.context import context_manager