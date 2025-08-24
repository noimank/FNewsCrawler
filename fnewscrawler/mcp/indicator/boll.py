import pandas as pd
import talib as ta

from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server
from fnewscrawler.utils import format_param


@mcp_server.tool(
    title="获取股票的布林带技术指标"
)
def stock_boll(
        stock_code: str,
        start_date: str,
        end_date: str,
        timeperiod: int = 20,
        nbdevup: float = 2.0,
        nbdevdn: float = 2.0
):
    """
    计算指定股票的布林带技术指标

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'
        timeperiod (int, optional): 计算周期. 默认值: 20
        nbdevup (float, optional): 上轨道标准差倍数. 默认值: 2.0
        nbdevdn (float, optional): 下轨道标准差倍数. 默认值: 2.0

    Returns:
        str: 包含布林带指标数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date)
    if data.empty:
        return "获取股票数据失败"

    timeperiod = int(timeperiod)
    # 检查数据是否足够
    if len(data) < timeperiod:
        return "数据不足，无法计算布林带指标"

    # 按照trade_date排序
    data = data.sort_values(by='trade_date')
    close = data['close'].values
    nbdevup = format_param(nbdevup, float)
    nbdevdn = format_param(nbdevdn, float)
    # 计算布林带指标
    upper, middle, lower = ta.BBANDS(
        close,
        timeperiod=timeperiod,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        matype=0
    )

    # 将计算结果组织成DataFrame
    result_df = pd.DataFrame({
        'trade_date': data['trade_date'],
        'middle': middle,
        'upper': upper,
        'lower': lower
    })

    # 丢弃nan
    result_df = result_df.dropna()
    # 转换为Markdown格式
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
