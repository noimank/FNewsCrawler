from fnewscrawler.core.news_crawl import news_crawl_from_url



async def test_news_crawl_from_url():
    url = "http://news.10jqka.com.cn/20250810/c670260043.shtml"
    context_type = "iwencai"
    news_url, news_content = await news_crawl_from_url(url, context_type)
    print(news_content)



if __name__ == '__main__':
    import asyncio
    asyncio.run(test_news_crawl_from_url())
