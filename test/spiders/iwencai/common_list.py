from fnewscrawler.spiders.iwencai import financial_quick_news_info, financial_people_news_info, \
    financial_market_news_info
from fnewscrawler.spiders.iwencai import comment_news_info
from fnewscrawler.spiders.iwencai import macro_economic_news_info
from fnewscrawler.spiders.iwencai import product_economic_news_info
from fnewscrawler.spiders.iwencai import international_economic_news_info
from fnewscrawler.spiders.iwencai import region_news_info
from fnewscrawler.spiders.iwencai import company_news_info

async def test_financial_quick_news():
    news_list = await financial_quick_news_info(2)
    print(news_list)


async def test_comment_news_info():
    news_list = await comment_news_info(2)
    print(news_list)

async def test_financial_people_news_info():
    news_list = await financial_people_news_info(2)
    print(news_list)


async def test_macro_economic_news_info():
    news_list = await macro_economic_news_info(2)
    print(news_list)


async def test_financial_market_news_info():
    news_list = await financial_market_news_info(2)
    print(news_list)

async def test_product_economic_news_info():
    news_list = await product_economic_news_info(2)
    print(news_list)

async def test_international_economic_news_info():
    news_list = await international_economic_news_info(2)
    print(news_list)

async def test_region_news_info():
    news_list = await region_news_info(2)
    print(news_list)

async def test_company_news_info():
    news_list = await company_news_info(2)
    print(news_list)


async def test_all():
    await test_financial_quick_news()
    await test_comment_news_info()
    await test_financial_people_news_info()
    await test_macro_economic_news_info()
    await test_financial_market_news_info()
    await test_product_economic_news_info()
    await test_international_economic_news_info()
    await test_region_news_info()
    await test_company_news_info()


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_all())
