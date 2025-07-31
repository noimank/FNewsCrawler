#!/bin/bash

# FNewsCrawler Docker启动脚本

set -e

echo "🚀 启动 FNewsCrawler 服务..."


# 启动Redis服务（如果未运行）
if ! pgrep redis-server > /dev/null; then
    echo "🔧 启动Redis服务..."
    redis-server --daemonize yes --bind 0.0.0.0 --port 6379
    sleep 2
fi

# 等待Redis服务启动
echo "⏳ 等待Redis服务启动..."
while ! redis-cli ping > /dev/null 2>&1; do
    echo "等待Redis连接..."
    sleep 2
done
echo "✅ Redis服务已就绪"


# 检查Python环境
echo "🐍 检查Python环境..."
python --version
pip list | grep -E "(fastapi|playwright|redis|fastmcp)"

# 启动主应用
exec python main.py