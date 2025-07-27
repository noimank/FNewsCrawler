from fnewscrawler.spiders.iwencai import IwencaiCrawler
import asyncio

crawler = IwencaiCrawler()


async def test_crawl():
    result = await crawler.crawl("平安银行", 2)
    print(result)


if __name__ == "__main__":
    asyncio.run(test_crawl())

