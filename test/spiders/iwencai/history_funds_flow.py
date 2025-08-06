from fnewscrawler.spiders.iwencai import get_history_funds_flow



async def test_get_history_funds_flow():
    stock_code = "600519"
    info = await get_history_funds_flow(stock_code)
    print(info)


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_get_history_funds_flow())


