import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import tushare as ts

from fnewscrawler.utils import LOGGER
from .redis_manager import redis_manager
import threading


class TushareDataProvider:
    _instance = None
    _lock = threading.Lock()
    """Tushare数据提供者"""

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定模式
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化Tushare连接"""
        # 防止重复初始化
        if hasattr(self, '_initialized'):
            return
        with self._lock:
            if hasattr(self, '_initialized'):
                return
            token = os.getenv("TUSHARE_TOKEN", None)
            if token:
                ts.set_token(token)
                self.pro = ts.pro_api()
                LOGGER.info("Tushare API初始化成功")
            else:
                LOGGER.warning("Tushare token未配置，某些功能将不可用")
                self.pro = None
            self._initialized = True

    def cache_dataframe(self, query_key: str, df: pd.DataFrame, expired_time: int = None) -> bool:
        """缓存股票数据"""
        key = f"stock:dataframe:{query_key}"
        # 从环境变量获取过期时间,单位天,默认3天
        if expired_time is None:
            expired_time = int(os.environ.get("STOCK_DATAFRAME_EXPIRED_TIME", 3)) * 86400
        return redis_manager.set(key, df, ex=expired_time, serializer='pickle')

    def get_cached_dataframe(self, query_key: str) -> Optional[pd.DataFrame]:
        """获取缓存的股票数据"""
        key = f"stock:dataframe:{query_key}"
        return redis_manager.get(key, serializer='pickle')

    def code2tscode(self, stock_code: str) -> str:
        """将股票代码转换为Tushare格式

        Args:
            stock_code: 股票代码，如'600519'

        Returns:
            Tushare格式的股票代码，如'600519.SH'或'000001.SZ'
        """
        if stock_code.startswith('6'):
            return f"{stock_code}.SH"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            return f"{stock_code}.SZ"
        else:
            raise ValueError(f"未知股票代码类型: {stock_code}")

    def get_stock_daily(self, ts_code: str, start_date: str = None, end_date: str = None, adjfactor=False) -> pd.DataFrame:
        """获取股票日线数据

        Args:
            ts_code: 股票代码，如'000001.SZ'
            start_date: 开始日期，格式'YYYYMMDD'
            end_date: 结束日期，格式'YYYYMMDD'

        Returns:
            包含股票日线数据的DataFrame
        """
        if not self.pro:
            raise ValueError("Tushare API未初始化")

        try:
            # 默认获取最近30天数据
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

            querry_key = f"{ts_code}_{start_date}_{end_date}_{adjfactor}"
            df = self.get_cached_dataframe(querry_key)
            if df is not None:
                LOGGER.info(f"adjfactor={adjfactor}，从缓存获取{ts_code}日线数据成功，共{len(df)}条记录")
                return df
            if adjfactor:
                # adj: 复权类型, None不复权, qfq: 前复权, hfq: 后复权
                df = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, adj='qfq', adjfactor=adjfactor)
            else:
                df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date, fields=[
                "ts_code",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "pre_close",
                "change",
                "pct_chg",
                "vol",
                "amount"
            ])
            LOGGER.info(f"获取{ts_code}日线数据成功，共{len(df)}条记录")
            if not df.empty:
                #10分钟缓存，主要是考虑到当天数据可能没进入tushare数据库，缓存太久可能导致不能获取最新的数据
                self.cache_dataframe(querry_key, df, expired_time=60 * 10)
            return df

        except Exception as e:
            LOGGER.error(f"获取股票日线数据失败: {e}")
            return pd.DataFrame()

    def get_stock_basic(self, exchange: str = None) -> pd.DataFrame:
        """获取股票基本信息

        Args:
            exchange: 交易所代码，如'SSE'(上交所)、'SZSE'(深交所)

        Returns:
            包含股票基本信息的DataFrame
        """
        if not self.pro:
            raise ValueError("Tushare API未初始化")

        try:
            querry_key = f"stock_basic_{exchange}"
            df = self.get_cached_dataframe(querry_key)
            if df is not None:
                LOGGER.info(f"从缓存获取股票基本信息成功，共{len(df)}只股票")
                return df

            df = self.pro.stock_basic(exchange=exchange, list_status='L')
            LOGGER.info(f"获取股票基本信息成功，共{len(df)}只股票")
            if not df.empty:
                self.cache_dataframe(querry_key, df)
            return df

        except Exception as e:
            LOGGER.error(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()

    def get_trade_cal(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取交易日历

        Args:
            start_date: 开始日期，格式'YYYYMMDD'
            end_date: 结束日期，格式'YYYYMMDD'

        Returns:
            包含交易日历的DataFrame
        """
        if not self.pro:
            raise ValueError("Tushare API未初始化")

        try:
            querry_key = f"trade_cal_{start_date}_{end_date}"
            df = self.get_cached_dataframe(querry_key)
            if df is not None:
                LOGGER.info(f"从缓存获取交易日历成功，共{len(df)}条记录")
                return df

            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            df = self.pro.trade_cal(start_date=start_date, end_date=end_date)
            LOGGER.info(f"获取交易日历成功，共{len(df)}条记录")
            if not df.empty:
                self.cache_dataframe(querry_key, df)
            return df

        except Exception as e:
            LOGGER.error(f"获取交易日历失败: {e}")
            return pd.DataFrame()
