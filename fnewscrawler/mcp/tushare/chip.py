from fnewscrawler.spiders.tushare import stock_cyq_perf, stock_cyq_chips
from fnewscrawler.mcp import mcp_server

@mcp_server.tool(title="获取A股每日筹码平均成本和胜率情况", enabled=False)
async def get_stock_cyq_perf(stock_code: str, start_date: str, end_date: str)->str:
    """获取A股每日筹码平均成本和胜率情况
    提供各价位的成本和胜率情况

    Args:
        stock_code: 股票代码，如'600519'
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'

    Returns:
        包含A股每日筹码平均成本和胜率情况的markdown格式字符串
    """
    try:
        df = await stock_cyq_perf(stock_code, start_date, end_date)
        if df.empty:
            return f"当前查询条件{stock_code}_{start_date}_{end_date}：获取A股每日筹码平均成本和胜率情况为空"

        df.columns = ["股票代码", "交易日期", "历史最低价", "历史最高价", "5分位成本", "15分位成本", "50分位成本", "85分位成本", "95分位成本","加权平均成本", "胜率"]
        # 转换为markdown格式
        md = df.to_markdown(index=False)
        return md
    except Exception as e:
        return f"获取A股每日筹码平均成本和胜率情况失败：{e}"




@mcp_server.tool(title="获取A股每日筹码分布情况", enabled=False)
async def get_stock_cyq_chips(stock_code: str, start_date: str, end_date: str)->str:
    """获取A股每日的筹码分布情况，提供各价位占比和筹码量占比

    Args:
        stock_code: 股票代码，如'600519'
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'

    Returns:
        包含A股每日的筹码分布情况的markdown格式字符串
    """
    try:
        df = await stock_cyq_chips(stock_code, start_date, end_date)
        if df.empty:
            return f"当前查询条件{stock_code}_{start_date}_{end_date}：获取A股每日的筹码分布情况为空"

        df.columns = ["股票代码", "交易日期", "成本价格", "价格占比 (%)"]
        # 转换为markdown格式
        md = df.to_markdown(index=False)
        return md
    except Exception as e:
        return f"获取A股每日的筹码分布情况失败：{e}"




