import akshare as ak

from fnewscrawler.mcp import mcp_server


@mcp_server.tool(title="akshare南北向资金流向查询工具")
async def north_south_bound_fund_flow_em_tool(symbol: str = "北向资金") -> str:
    """
    南向和北向资金流查询工具 - 获取沪深港通资金流向数据，该数据为最新一日的南北向资金流分时数据

    Args:
        symbol (str, optional): 资金类型，默认为"北向资金"。支持的选项：
            - "北向资金": 外资投资A股的资金流向
            - "南向资金": 内地投资港股的资金流向

    Returns:
        str: Markdown格式的资金流向数据表格

    示例：
        # 查询北向资金流向
        result = await north_south_bound_fund_flow_em_tool("北向资金")

        # 查询南向资金流向
        result = await north_south_bound_fund_flow_em_tool("南向资金")
    """
    try:
        # 参数验证
        valid_symbols = ["北向资金", "南向资金"]
        if symbol not in valid_symbols:
            return f"错误：无效的资金类型。支持的类型：{', '.join(valid_symbols)}"

        # 调用akshare获取资金流向数据
        try:
            fund_flow_data = ak.stock_hsgt_fund_min_em(symbol=symbol)
        except Exception as e:
            return f"错误：获取资金流向数据失败: {str(e)}"

        if fund_flow_data is None or fund_flow_data.empty:
            return "错误：获取的资金流向数据为空，可能是市场休市或数据源问题"

        # 生成Markdown格式的表格
        return fund_flow_data.to_markdown(index=False)

    except Exception as e:
        return f"错误：查询资金流向数据时发生错误: {str(e)}"




