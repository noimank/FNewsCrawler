from fnewscrawler.spiders.iwencai import get_secu_margin_trading_info



async def test_get_secu_margin_trading_info():
    stock_code = "600519"
    data_num = 1000
    info = await get_secu_margin_trading_info(stock_code, data_num)
    print(info)


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_get_secu_margin_trading_info())


