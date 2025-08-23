from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.eastmoney import eastmoney_stock_base_info


@mcp_server.tool(title="获取股票基本信息", enabled=False)
async def get_eastmoney_stock_base_info_tool(stock_code: str):
    """从东方财富网获取股票基本信息。
    仅支持沪深股票，不支持港股和美股

    Args:
        stock_code: 股票代码,例如:600519

    Returns:
        str: 股票基本信息
        股票名称
        所属行业名称
        公司核心信息
        行业比较信息
    """
    stock_info = await eastmoney_stock_base_info(stock_code)
    return stock_info


