#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FNews Crawler - 财经新闻爬虫主入口


"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

# 确保数据目录存在
os.makedirs(project_root / "data", exist_ok=True)

def start_web_app():
    """
    启动Streamlit Web应用
    """
    try:
        import streamlit.web.cli as stcli
        import streamlit as st
        
        # 从环境变量获取配置
        host = os.getenv('STREAMLIT_HOST', 'localhost')
        port = int(os.getenv('STREAMLIT_PORT', '8501'))
        debug = os.getenv('STREAMLIT_DEBUG', 'false').lower() == 'true'
        
        print(f"🚀 启动FNews Crawler Web应用...")
        print(f"📍 访问地址: http://{host}:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print(f"🔐 支持二维码登录管理")
        print(f"📰 支持多平台新闻爬取")
        print(f"按 Ctrl+C 停止应用\n")
        
        # 设置Streamlit应用路径
        app_path = str(project_root / "fnewscrawler" / "web" / "app.py")
        
        # 检查应用文件是否存在
        if not os.path.exists(app_path):
            print(f"❌ 应用文件不存在: {app_path}")
            sys.exit(1)
        
        # 构建启动参数
        sys.argv = [
            "streamlit",
            "run",
            app_path,
            "--server.address", host,
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true" if not debug else "false",
            "--theme.base", "light"
        ]
        
        # 启动Streamlit应用
        stcli.main()
        
    except ImportError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动Web应用失败: {e}")
        sys.exit(1)

def main():
    """
    主入口函数
    """
    parser = argparse.ArgumentParser(
        description="FNews Crawler - 财经新闻爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py              # 启动Web界面 (推荐)
  python main.py --cli        # 命令行模式
  python main.py --test       # 测试模式
  python main.py --web        # 显式启动Web界面
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true', 
        help='启动Web界面模式 (默认)'
    )

    
    args = parser.parse_args()
    
    # 显示欢迎信息
    print("\n" + "="*60)
    print("🎯 FNews Crawler - 财经新闻爬虫系统")
    print("📊 支持同花顺问财、东方财富等多个新闻源")
    print("🔧 基于 Playwright + Streamlit + Redis")
    print("="*60 + "\n")
    
    try:
        # 默认启动Web界面
        start_web_app()
            
    except KeyboardInterrupt:
        print("\n👋 感谢使用 FNews Crawler!")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()