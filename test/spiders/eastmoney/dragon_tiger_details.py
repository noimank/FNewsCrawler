from fnewscrawler.spiders.eastmoney import eastmoney_dragon_tiger_detail
import asyncio

async def test_get_dragon_tiger_detail():

    rank_type = "3day"
    page_num = 2

    table = await eastmoney_dragon_tiger_detail(rank_type, page_num)
    print(table)

if __name__ == '__main__':
    asyncio.run(test_get_dragon_tiger_detail())
