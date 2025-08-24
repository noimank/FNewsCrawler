import pandas as pd
import talib as ta

from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server
from fnewscrawler.utils import parse_params2list


@mcp_server.tool(
    title="获取指定股票的移动平均线技术指标"
)
def stock_ma(
        stock_code: str,
        start_date: str,
        end_date: str,
        ma_types: str = "5"
):
    """
    计算指定股票的移动平均线技术指标

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'
        ma_types (str, optional): 移动平均线周期，支持多个周期，逗号分隔. 默认值: "5"

    Returns:
        str: 包含移动平均线指标数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date)

    if data.empty:
        return "获取股票数据失败"

    ma_types = parse_params2list(ma_types, int)
    # 检查数据是否足够
    if len(data) < max(ma_types):
        return "数据不足，无法计算移动平均线指标"

    # 按照trade_date排序
    data = data.sort_values(by='trade_date')
    close = data['close'].values
    result_df = None
    for ma_type in ma_types:
        ma = ta.MA(close, timeperiod=ma_type)
        if result_df is None:
            result_df = pd.DataFrame({
                'trade_date': data['trade_date'],
                f'MA{ma_type}': ma
            })
        else:
            result_df[f'MA{ma_type}'] = ma

    # # 将计算结果组织成DataFrame
    # result_df = pd.DataFrame({
    #     'trade_date': data['trade_date'],
    #     f'MA{ma_type}': ma
    # })

    # 丢弃nan
    result_df = result_df.dropna()
    # 转换为Markdown格式
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
