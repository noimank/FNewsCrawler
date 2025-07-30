#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FNewsCrawler Web应用启动脚本

快速启动FastAPI Web应用
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).absolute()
sys.path.insert(0, str(project_root))

from fnewscrawler.utils.logger import LOGGER
import asyncio

# 检查当前平台是否为 Windows
if sys.platform == 'win32':
    # 设置事件循环策略为支持子进程的 WindowsSelectorEventLoopPolicy
    # 这是解决 NotImplementedError 的关键
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    LOGGER.info("window平台设置asyncio循环策略成功")


def main():
    """主函数"""
    try:
        LOGGER.info("正在启动FNewsCrawler Web应用...")

        host_addr = os.getenv("WEB_HOST", "localhost")
        port = int(os.getenv("WEB_PORT", 8480))
        # 启动配置
        config = {
            "app": "web.app:app",
            "host": host_addr,
            "port": port,
            # "reload": True,
            "log_level": "info",
            "access_log": True
        }

        LOGGER.info(f"Web应用将在 http://{host_addr}:{port} 启动")
        LOGGER.info(f"API文档地址: http://{host_addr}:{port}/docs")
        LOGGER.info("按 Ctrl+C 停止服务")

        # 启动服务
        uvicorn.run(**config)

    except KeyboardInterrupt:
        LOGGER.info("\n用户中断，正在关闭Web应用...")
    except Exception as e:
        LOGGER.error(f"启动Web应用失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()