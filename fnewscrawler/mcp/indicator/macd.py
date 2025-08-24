import numpy as np
import pandas as pd

from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server
from fnewscrawler.utils import format_param


@mcp_server.tool(
    title="获取指定股票的MACD技术指标"
)
def stock_macd(
        stock_code: str,
        start_date: str,
        end_date: str,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9
):
    """
    计算指定股票的MACD技术指标（与同花顺/通达信完全一致），基于前复权数据计算

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'
        fastperiod (int, optional): 快线周期. 默认值: 12
        slowperiod (int, optional): 慢线周期. 默认值: 26
        signalperiod (int, optional): 信号线周期. 默认值: 9

    Returns:
        str: 包含MACD指标数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date, adjfactor=True)

    if data.empty:
        return "获取股票数据失败"

    fastperiod = format_param(fastperiod, int)
    slowperiod = format_param(slowperiod, int)
    signalperiod = format_param(signalperiod, int)

    required_length = max(fastperiod, slowperiod, signalperiod)
    if len(data) < required_length:
        return "数据不足，无法计算MACD指标"

    # 按交易日升序排序（必须！）
    data = data.sort_values(by='trade_date').reset_index(drop=True)

    # 确保收盘价为数值
    close = pd.to_numeric(data['close'], errors='coerce')

    # print(f"前5个收盘价: {close.head().values}")

    # ------------------------ 修正版 EMA：与同花顺完全一致 ------------------------
    def calc_ema(series, period):
        """
        计算 EMA，初始值为第一个值，后续按 α=2/(N+1) 递推
        符合同花顺、通达信标准
        """
        ema = np.zeros(len(series)) * np.nan
        alpha = 2.0 / (period + 1)

        for i in range(len(series)):
            if i == 0:
                ema[i] = series.iloc[i]  # 第一天 EMA = 当日收盘价
            else:
                # EMA_today = α * price_today + (1 - α) * EMA_yesterday
                ema[i] = alpha * series.iloc[i] + (1 - alpha) * ema[i - 1]
            # 注意：前面不设 NaN，所有值都参与递推（从第1天开始就有值）
        return ema

    # ------------------------ 计算 DIF（快线 - 慢线）------------------------
    ema_fast = calc_ema(close, fastperiod)
    ema_slow = calc_ema(close, slowperiod)

    # DIF = EMA(12) - EMA(26)
    dif = ema_fast - ema_slow

    # ------------------------ 计算 DEA（DIF 的 EMA）------------------------
    # 注意：DEA 的 EMA 也是从 DIF 的第一天开始递推，不是从第9天开始补 SMA
    dea = calc_ema(pd.Series(dif), signalperiod)

    # ------------------------ MACD 柱状图 = (DIF - DEA) * 2 ------------------------
    macd_hist = (dif - dea) * 2  # ← 同花顺柱状图是差值的 2 倍！

    # ------------------------ 构造结果 DataFrame ------------------------
    result_df = pd.DataFrame({
        'trade_date': data['trade_date'],
        'DIF': np.round(dif, 4),
        'DEA': np.round(dea, 4),
        'MACD': np.round(macd_hist, 4)  # 红绿柱
    })

    # 去除前面可能因 slowperiod 导致的无效值（可选）
    result_df = result_df.iloc[slowperiod - 1:].reset_index(drop=True)
    # 转为 Markdown 表格
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
