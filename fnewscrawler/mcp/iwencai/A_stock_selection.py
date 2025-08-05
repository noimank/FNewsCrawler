from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.iwencai import iwencai_A_stock_selection


@mcp_server.tool(title="智能A股股票筛选工具")
async def iwencai_select_A_stock(select_condition: str):
    """
    智能A股股票筛选工具

    这是一个基于同花顺iWencai的语义化A股股票筛选工具，能够根据自然语言描述的条件筛选出符合要求的A股股票。

    功能特点：
    1. 支持语义化的筛选条件输入，无需复杂的技术指标代码
    2. 返回结构化的markdown表格格式结果
    3. 支持多种技术指标和基本面指标的组合筛选
    4. 实时获取最新的股票数据

    参数说明：
    select_condition (str): 语义化的股票筛选条件，支持以下类型的条件：
        - 基本面指标：总股本、流通股本、市值、营收、净利润、ROE等
        - 技术指标：MACD、BOLL、BIAS、KDJ、RSI、均线系统等
        - 价格相关：股价、涨跌幅、成交量、换手率等
        - 行业板块：所属行业、概念板块等
        - 财务指标：PE、PB、毛利率、负债率等

    筛选条件示例：
    1. "总股本大于等于2亿小于等于5亿，macd买入信号"
    2. "多头排列，boll突破上轨，bias买入信号"
    3. "市值小于100亿，ROE大于15%，PE小于20"
    4. "昨日涨停，今日高开，成交量放大"
    5. "新能源概念，市盈率小于30，净利润增长率大于20%"

    条件连接规则：
    - 多个条件之间使用中文逗号"，"进行连接
    - 支持范围条件：大于、小于、大于等于、小于等于、等于
    - 支持信号类条件：买入信号、卖出信号、突破、跌破等
    - 支持趋势类条件：多头排列、空头排列、上升趋势等

    返回格式：
    返回结构化的markdown表格，包含以下信息：
    - 股票代码
    - 股票名称
    - 现价
    - 涨跌幅
    - 市值
    - 相关技术指标数值
    - 其他筛选条件相关的数据

    使用建议：
    1. 条件描述要具体明确，避免过于宽泛
    2. 技术指标名称使用常见的中文表述
    3. 数值条件要明确范围或阈值
    4. 可以结合基本面和技术面条件进行综合筛选

    注意事项：
    - 股票数据具有时效性，建议及时查看
    - 技术指标信号仅供参考，投资需谨慎
    - 筛选结果数量可能因条件严格程度而变化
    """
    try:
        result = await iwencai_A_stock_selection(select_condition)
        return result
    except Exception as e:
        return f"股票筛选过程中出现错误：{str(e)}\n请检查筛选条件是否正确，或稍后重试。"