from fnewscrawler.mcp import mcp_server
from fnewscrawler.core.news_crawl import news_crawl_from_url


@mcp_server.tool(title="通用新闻内容提取工具")
async def news_crawl(url: str) -> str:
    """从指定URL抓取新闻内容并返回纯文本格式的新闻正文

    该工具专门用于从新闻类网页URL中提取核心新闻内容，自动去除网页中的广告、
    导航栏、页脚等无关元素，只返回纯净的新闻正文文本。

    Args:
        url (str): 需要抓取的新闻网页URL，必须以http://或https://开头

    Returns:
        str: 返回从网页中提取的新闻正文内容纯文本

    Raises:
        ValueError: 当输入的URL格式不正确或无法访问时抛出异常
        Exception: 当网页内容解析失败或不符合新闻网页结构时可能抛出异常

    Example:
        >>> await news_crawl("https://example.com/news/123")
        "这里是新闻正文内容...自动去除网页其他无关元素..."

    Notes:
        - 仅适用于标准的新闻类网页，对于论坛、博客等非标准页面可能效果不佳
        - 返回内容已自动去除HTML标签、JavaScript代码等非文本内容
        - 对于需要登录才能查看的新闻页面无法抓取
    """
    _, news_content = await news_crawl_from_url(url)
    return news_content
