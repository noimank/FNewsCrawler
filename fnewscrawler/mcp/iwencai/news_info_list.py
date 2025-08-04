from fnewscrawler.spiders.iwencai import (
    financial_quick_news_info,
    financial_people_news_info,
    financial_market_news_info,
    comment_news_info,
    macro_economic_news_info,
    product_economic_news_info,
    international_economic_news_info,
    region_news_info,
    company_news_info
)
from fnewscrawler.mcp import mcp_server


@mcp_server.tool(title="同花顺财经快讯获取工具")
async def iwencai_financial_quick_news(page: int = 1) -> dict:
    """获取财经快讯新闻列表

    提供最新的财经快讯新闻列表，包含标题、摘要、发布时间和详情链接。
    适合需要实时跟踪财经简讯的场景。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 如需获取新闻正文内容，请使用news_crawl工具传入url字段
        2. 每页默认返回20条左右新闻
        3. 时间格式为YYYY-MM-DD HH:MM:SS
    """
    return await financial_quick_news_info(page)


@mcp_server.tool(title="同花顺财经人物新闻获取工具", enabled=False)
async def iwencai_financial_people_news(page: int = 1) -> dict:
    """获取财经人物相关新闻列表

    提供财经领域重要人物相关的新闻报道，包括企业家、经济学家等。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 人物新闻通常包含专访、观点评论等内容
        2. 可结合news_crawl工具获取完整采访内容
    """
    return await financial_people_news_info(page)


@mcp_server.tool(title="同花顺金融市场新闻获取工具")
async def iwencai_financial_market_news(page: int = 1) -> dict:
    """获取金融市场动态新闻列表

    提供股票、债券、外汇等金融市场的实时动态和分析报道。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 包含市场行情、政策解读等专业内容
        2. 适合金融分析场景使用
    """
    return await financial_market_news_info(page)


@mcp_server.tool(title="同花顺财经评论获取工具",
                 enabled=False)
async def iwencai_comment_news(page: int = 1) -> dict:
    """获取财经评论文章列表

    提供专业财经评论员和分析师的观点文章。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 评论类文章通常包含深度分析和独特见解
        2. 文章篇幅一般较长，建议使用news_crawl获取全文
    """
    return await comment_news_info(page)


@mcp_server.tool(title="同花顺宏观经济新闻获取工具")
async def iwencai_macro_economic_news(page: int = 1) -> dict:
    """获取宏观经济政策新闻列表

    提供GDP、CPI、货币政策等宏观经济指标和政策新闻。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 包含国家级经济数据和政策解读
        2. 适合宏观经济研究使用
    """
    return await macro_economic_news_info(page)


@mcp_server.tool(title="同花顺产经新闻获取工具", enabled=False)
async def iwencai_product_economic_news(page: int = 1) -> dict:
    """获取各行业经济新闻列表

    提供制造业、房地产、科技等细分行业的经济新闻。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 可按行业筛选关注的领域
        2. 包含行业数据和趋势分析
    """
    return await product_economic_news_info(page)


@mcp_server.tool(title="同花顺国际经济新闻获取工具", enabled=False)
async def iwencai_international_economic_news(page: int = 1) -> dict:
    """获取国际经济新闻列表

    提供全球主要经济体的经济动态和国际财经事件。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 包含国际贸易、汇率变动等国际财经新闻
        2. 适合跨境业务分析使用
    """
    return await international_economic_news_info(page)


@mcp_server.tool(title="同花顺区域经济新闻获取工具", enabled=False)
async def iwencai_region_news(page: int = 1) -> dict:
    """获取区域经济新闻列表

    提供各省市、经济特区的区域经济发展新闻。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 包含地方经济政策和区域发展动态
        2. 适合区域经济研究使用
    """
    return await region_news_info(page)


@mcp_server.tool(title="同花顺企业新闻获取工具", enabled=False)
async def iwencai_company_news(page: int = 1) -> dict:
    """获取上市公司和企业新闻列表

    提供上市公司公告、企业动态和商业新闻。

    Args:
        page (int): 请求的页码，默认为第1页

    Returns:
        dict: 返回结构化的新闻列表信息，格式如下：
            {
                "news_list": [
                    {
                        "title": "新闻标题",
                        "url": "新闻详情页URL",
                        "summary": "新闻摘要",
                        "time": "发布时间(格式:YYYY-MM-DD HH:MM:SS)"
                    },
                    ...
                ],
                "page_no": 当前页码,
                "total_page": 总页数(固定20页),
                "news_count": 当前页新闻数量,
                "current_page": 当前页码
            }

    Notes:
        1. 包含企业财报、并购等商业新闻
        2. 可结合公司名称筛选特定企业新闻
    """
    return await company_news_info(page)