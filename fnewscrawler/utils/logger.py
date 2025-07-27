import os

from loguru import logger


class Logger:
    def __init__(self):
        # 只允许INFO、WARNING、ERROR三种日志等级
        allowed_levels = {"INFO", "WARNING", "ERROR"}
        env_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
        self.level = env_level if env_level in allowed_levels else "INFO"
        self.logger = logger
        # self.logger.remove()  # 移除默认的控制台输出
        logger_path = os.environ.get("LOG_FILE_PATH", os.path.expanduser("~/FNewsCrawler.log"))
        os.makedirs(os.path.dirname(logger_path), exist_ok=True)
        self.logger.add(
            logger_path,
            rotation="1 MB",
            encoding="utf-8",
            level=self.level
        )

    def info(self, msg):
        if self.level == "INFO":
            self.logger.info(msg)
        elif self.level == "WARNING":
            # 只输出WARNING及以上
            pass
        elif self.level == "ERROR":
            # 只输出ERROR
            pass

    def warning(self, msg):
        if self.level in ["INFO", "WARNING"]:
            self.logger.warning(msg)
        elif self.level == "ERROR":
            pass

    def error(self, msg):
        self.logger.error(msg)

# 实例化logger对象供外部使用
LOGGER = Logger()