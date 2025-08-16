from fnewscrawler.spiders.eastmoney import eastmoney_market_history_funds_flow
from fnewscrawler.mcp import mcp_server


@mcp_server.tool(title="获取大盘资金流数据")
async def get_eastmoney_market_history_funds_flow(market_type: str= "沪深两市", data_num: int = 40):
    """从东方财富网获取大盘资金流数据。
    
    Args:
        market_type: 市场类型,默认沪深两市,仅支持沪深两市,沪市,深市,创业板,沪B,深B
        data_num: 数据数量,默认40条
        
    Returns:
        str: 大盘资金流数据,Markdown格式
    """
    markdown_table = await eastmoney_market_history_funds_flow(market_type, data_num)
    return markdown_table

