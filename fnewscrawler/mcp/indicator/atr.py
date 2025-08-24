import pandas as pd
import talib as ta

from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server
from fnewscrawler.utils import parse_params2list

@mcp_server.tool(
    title="计算股票的ATR技术指标"
)
def stock_atr(
        stock_code: str,
        start_date: str,
        end_date: str,
        timeperiod: str = "14"
):
    """
    计算指定股票的ATR技术指标,主要用来衡量市场的波动性,默认计算14天的ATR指标

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'
        timeperiod (str, optional): ATR计算周期，支持多个周期，逗号分隔. 默认值: "14"

    Returns:
        str: 包含ATR指标数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date)

    if data.empty:
        return "获取股票数据失败"

    timeperiod = parse_params2list(timeperiod, int)
    # 检查数据是否足够
    if len(data) < max(timeperiod):
        return "数据不足，无法计算ATR指标"

    # 按照trade_date排序
    data = data.sort_values(by='trade_date')
    # 将计算结果组织成DataFrame
    result_df = pd.DataFrame({
        'trade_date': data['trade_date'],
    })

    for tp in timeperiod:
        # 计算ATR指标
        atr = ta.ATR(data['high'].values,
                     data['low'].values,
                     data['close'].values,
                     timeperiod=tp)
        result_df[f'ATR_{tp}'] = atr


    # 丢弃nan
    result_df = result_df.dropna()
    # 转换为Markdown格式
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
