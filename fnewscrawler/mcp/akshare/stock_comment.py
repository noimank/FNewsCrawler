from fnewscrawler.spiders.akshare import ak_stock_comment_detail
from fnewscrawler.mcp import mcp_server



@mcp_server.tool(title="从akshare获取股票机构参与度数据")
def get_ak_stock_comment_detail(stock_code: str)->str:
    """从akshare获取股票机构参与度数据
    大约最近的44个交易日的数据

    Args:
        stock_code: 股票代码，如'600000'

    Returns:
        包含股票机构参与度数据的markdown表格，列名包括：日期、机构参与度(%)
    """
    markdown_table = ak_stock_comment_detail(stock_code)
    return markdown_table
