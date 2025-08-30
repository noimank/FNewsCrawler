from fnewscrawler.spiders.akshare import stock_cyq_em
from fnewscrawler.mcp import mcp_server

@mcp_server.tool(title="akshare股票筹码分布获取工具")
def get_stock_cyq_em(stock_code: str, adjust: str = "") -> str:
    """获取股票的筹码分布数据。

    该函数通过调用akshare接口获取指定股票近90个交易日的筹码分布数据，并以markdown表格格式返回。

    Args:
        stock_code (str): 股票代码，例如："600519"或"000001"。
        adjust (str, optional): 复权类型。默认为空字符串，表示不复权。
            可选值:
            - "": 不复权
            - "qfq": 前复权
            - "hfq": 后复权

    Returns:
        str: 包含筹码分布数据的markdown格式表格字符串。

    Examples:
        >>> result =  get_stock_cyq_em("600519")
        >>> print(result)
        | 日期 | 获利比例 | 平均成本 | ...
    """
    markdown_table = stock_cyq_em(stock_code, adjust)
    return markdown_table
