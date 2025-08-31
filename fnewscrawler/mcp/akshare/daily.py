


from fnewscrawler.spiders.akshare import ak_daily
from fnewscrawler.mcp import mcp_server

@mcp_server.tool(title="akshare股票日线数据获取工具")
def get_stock_daily(stock_code: str, start_date: str, end_date: str, adjust: str = "") -> str:
    """获取股票的日线数据。

    Args:
        stock_code: 股票代码，如'000001'
        start_date: 开始日期，格式'YYYYMMDD'，如'20250829'
        end_date: 结束日期，格式'YYYYMMDD'，如'20250830'
        adjust: 复权类型, None不复权, qfq: 前复权, hfq: 后复权, 默认None

    Returns:
        包含股票日线数据的markdown格式表格字符串，列名包括：日期、股票代码、开盘价、收盘价、最高价、最低价、成交量、成交额、振幅(%)、涨跌幅(%)、涨跌额(元)、换手率(%)
    """
    daily_table = ak_daily(stock_code, start_date, end_date, adjust)
    if daily_table is None:
        return "获取股票日线数据失败"
    if daily_table.empty:
        return "获取股票日线数据为空"

    return daily_table.to_markdown(index=False)
