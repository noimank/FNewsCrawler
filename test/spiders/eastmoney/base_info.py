from fnewscrawler.spiders.eastmoney import eastmoney_stock_base_info
import asyncio

async def test_get_stock_base_info():

    table = await eastmoney_stock_base_info("002402")
    print(table)

if __name__ == '__main__':
    asyncio.run(test_get_stock_base_info())
