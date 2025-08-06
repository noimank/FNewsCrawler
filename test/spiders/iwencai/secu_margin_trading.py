from fnewscrawler.spiders.iwencai import get_secu_margin_trading_info



async def test_get_secu_margin_trading_info():
    stock_code = "600519"
    info = await get_secu_margin_trading_info(stock_code)
    print(info)


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_get_secu_margin_trading_info())


