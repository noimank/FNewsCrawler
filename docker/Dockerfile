FROM noimankdocker/fnewscrawler:dev

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# github action自带翻墙没必要设置
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
#RUN pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装项目依赖
RUN uv  pip  install --system --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium && \
    playwright install-deps chromium || true && \
    rm -rf /var/lib/apt/lists/* \

# 设置环境变量
ENV PYTHONPATH=/app
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=8480
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV PW_USE_HEADLESS=true
ENV LOG_FILE_PATH=/app/FNewsCrawler.log

EXPOSE 8480

# 启动脚本
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh
# 确保脚本使用Unix行结束符
RUN sed -i 's/\r$//' /app/start.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8480/api/monitor/overview || exit 1

# 启动命令
ENTRYPOINT ["/app/start.sh"]