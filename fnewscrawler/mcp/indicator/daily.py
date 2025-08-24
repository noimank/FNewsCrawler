from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server


@mcp_server.tool(
    title="获取指定股票指定日期范围的日线数据"
)
def stock_daily(
        stock_code: str,
        start_date: str,
        end_date: str
):
    """
    获取指定股票的日线数据

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'

    Returns:
        str: 包含股票日线数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date)
    if data.empty:
        return "获取股票数据失败"

    # 按照trade_date排序
    data = data.sort_values(by='trade_date')

    # 选择需要展示的列
    result_df = data[['trade_date', 'open', 'high', 'low', 'close', "change", "pct_chg", 'vol', 'amount']]
    # 重命名列
    result_df.columns = ['日期', '开盘价', '最高价', '最低价', '收盘价', '涨跌额', '涨跌幅', '成交量', '成交额']

    # 转换为Markdown格式
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
