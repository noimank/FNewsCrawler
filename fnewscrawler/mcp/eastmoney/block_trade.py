from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.eastmoney import eastmoney_block_trade_detail


@mcp_server.tool(title="获取股票大宗交易每日明细")
async def get_eastmoney_block_trade_detail_tool(stock_code: str):
    """从东方财富网获取股票大宗交易每日明细。

    Args:
        stock_code: 股票代码,例如:600519

    Returns:
        str: 股票大宗交易每日明细,Markdown格式
    """
    markdown_table = await eastmoney_block_trade_detail(stock_code)
    return markdown_table
