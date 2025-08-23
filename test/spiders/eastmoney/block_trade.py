from fnewscrawler.spiders.eastmoney import eastmoney_block_trade_detail
import asyncio

async def test_get_block_trade_detail():

    table = await eastmoney_block_trade_detail("300059")
    print(table)

if __name__ == '__main__':
    asyncio.run(test_get_block_trade_detail())
