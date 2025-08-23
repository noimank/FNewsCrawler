from fnewscrawler.spiders.eastmoney import eastmoney_dragon_tiger_detail, eastmoney_stock_dragon_tiger_detail
import asyncio

async def test_get_dragon_tiger_detail():

    rank_type = "3day"
    page_num = 2

    table = await eastmoney_dragon_tiger_detail(rank_type, page_num)
    print(table)

async def test_get_stock_dragon_tiger_detail():

    # stock_code = "002214"
    stock_code = "002214"

    table = await eastmoney_stock_dragon_tiger_detail(stock_code)
    print(table)




if __name__ == '__main__':
    # asyncio.run(test_get_dragon_tiger_detail())
    asyncio.run(test_get_stock_dragon_tiger_detail())
