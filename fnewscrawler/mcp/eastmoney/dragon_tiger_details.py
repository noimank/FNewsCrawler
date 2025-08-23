from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.eastmoney import eastmoney_dragon_tiger_detail


@mcp_server.tool(title="获取龙虎榜明细")
async def get_eastmoney_dragon_tiger_detail(rank_type: str, page_num: int = 1):
    """从东方财富网获取股票龙虎榜每日明细。

    Args:
        rank_type: 龙虎榜排行类型，1day, 3day, 5day, 10day, 30day
        page_num: 页码,默认第1页

    Returns:
        str: 龙虎榜明细,Markdown格式
    """
    markdown_table = await eastmoney_dragon_tiger_detail(rank_type, page_num)
    return markdown_table
