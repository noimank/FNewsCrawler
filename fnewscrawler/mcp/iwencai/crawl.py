from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.iwencai import iwencai_crawl_from_query



@mcp_server.tool(title="同花顺问财-专业新闻查询工具")
async def iwencai_news_query(query: str, page_no: int = 1):
    """
    从同花顺问财(iWenCai)获取最新财经新闻的专业查询工具

    这是一个专业的财经资讯查询工具，能够从同花顺问财官网实时获取最新的财经新闻信息。
    该工具特别适用于股票研究、投资分析和财经市场监控等场景。

    主要功能：
    - 实时获取同花顺问财官网的最新财经资讯
    - 支持股票名称、股票代码、行业关键词等多种查询方式
    - 按时间倒序返回最相关的财经新闻
    - 分页查询支持，每页返回15条新闻记录

    适用场景：
    - 股票基本面分析和研调
    - 行业动态追踪和政策解读
    - 投资决策支持和风险评估
    - 财经事件监控和市场热点分析

    Args:
        query (str): 查询关键词，支持以下类型：
            - 股票名称：如"贵州茅台"、"比亚迪"、"腾讯控股"、"宁德时代"
            - 股票代码：如"600519"、"002594"、"00700"、"300750"
            - 行业关键词：如"新能源汽车"、"人工智能"、"半导体"、"房地产"
            - 财经概念：如"降准降息"、"IPO上市"、"并购重组"、"业绩预告"
            - 宏观经济：如"GDP增长"、"CPI数据"、"外汇储备"、"贸易数据"

        page_no (int, optional): 页码，默认为1。每页返回15条新闻。
            - 对于热门股票或重大事件，建议查询多页获取全面信息
            - 建议不超过5页以保持查询效率
            - 页码从1开始，支持正整数

    Returns:
        dict: 包含以下字段的查询结果：
            - data (list): 新闻列表，每条新闻包含：
                - title (str): 新闻标题
                - content (str): 新闻内容
                - url (str): 新闻详情链接
                - time (str): 发布时间
                - source (str): 新闻来源媒体
            - total (int): 当前页新闻数量
            - page (int): 当前页码

    使用建议：
        1. 股票查询：优先使用完整的股票名称，如"贵州茅台"而非"茅台"
        2. 行业分析：使用具体的行业术语，如"新能源汽车"而非"汽车"
        3. 时效性：返回的新闻按时间倒序排列，第一页为最新资讯
        4. 分页策略：如需全面了解，可依次查询多页信息
        5. 关键词优化：结合当前市场热点和时事调整查询词汇

    注意事项：
        - 该工具需要稳定的网络连接
        - 建议控制查询频率，避免过度访问
        - 返回信息仅供参考，投资需谨慎
        - 异步函数，需在异步环境中调用

    示例用法：
        # 查询特定股票最新动态
        result = await iwencai_news_query("贵州茅台")

        # 获取行业相关新闻的第2页
        result = await iwencai_news_query("人工智能", page_no=2)

        # 查询宏观经济政策新闻
        result = await iwencai_news_query("央行降息")
    """
    news_list = await iwencai_crawl_from_query(query, page_no)
    news_info = {
        "data": news_list,
        "total": len(news_list),
        "page": page_no,

    }
    return news_info

