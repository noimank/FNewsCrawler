import os

from fnewscrawler.mcp import mcp_server
from fnewscrawler.core.news_crawl import news_crawl_from_url
import asyncio


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


@mcp_server.tool(title="批量新闻内容提取工具")
async def news_crawl_batch(urls: list[str]) -> list[dict]:
    """批量从多个URL抓取新闻内容并返回结构化结果

    该工具可并发处理多个新闻URL，自动提取每个网页的核心新闻正文内容，
    并返回包含原始URL和对应新闻内容的字典列表。系统会自动过滤广告、
    导航栏等无关内容，仅保留纯净的新闻文本。

    Args:
        urls (list[str]):
            - 需要抓取的新闻网页URL列表
            - 每个URL必须以http://或https://开头
            - 建议每次调用URL数量不超过50个以保证性能

    Returns:
        list[dict]: 返回结果列表，每个元素为包含以下键的字典:
            - url (str): 原始请求URL
            - content (str): 提取的新闻正文纯文本
            (对于失败的请求会返回错误信息)

    Raises:
        ValueError: 当输入不是列表或包含无效URL时
        Exception: 当服务器端处理出现异常时

    Example:
        >>> await news_crawl_batch([
                "https://news.example.com/1",
                "https://news.example.com/2"
            ])
        返回：
        [
            {"url": "https://news.example.com/1", "content": "新闻1正文..."},
            {"url": "https://news.example.com/2", "content": "新闻2正文..."}
        ]

    Notes:
        1. 建议批量URL来自同一新闻站点以获得最佳解析效果
        2. 每个URL处理超时时间为10秒
        3. 返回列表顺序与输入URL顺序保持一致
        4. 对于无法解析的页面，content可能为空字符串
    """
    # 创建信号量限制最大并发数为20
    semaphore = asyncio.Semaphore(int(os.getenv("MAX_CRAWL_CONCURRENCY", 20)))

    async def fetch_with_semaphore(url):
        async with semaphore:
            return await news_crawl_from_url(url)

    # 使用信号量控制并发抓取所有URL内容
    tasks = [fetch_with_semaphore(url) for url in urls]
    results = await asyncio.gather(*tasks)

    # 将结果和URL组合成字典列表
    return [{"url": url, "content": content}
            for (url, (_, content)) in zip(urls, results)]