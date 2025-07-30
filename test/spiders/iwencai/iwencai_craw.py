from fnewscrawler.spiders.iwencai import iwencai_crawl_from_query
import asyncio



async def test_crawl():
    result = await iwencai_crawl_from_query("三七互娱", 2)
    print(result)


if __name__ == "__main__":
    asyncio.run(test_crawl())

