from fnewscrawler.spiders.eastmoney import eastmoney_market_history_funds_flow
import asyncio

async def test_get_market_history_funds_flow():
    market_type = "沪深两市"
    market_type = "沪市"
    market_type = "深市"
    market_type = "创业板"
    market_type = "沪B"
    market_type = "深B"
    data_num = 40
    info = await eastmoney_market_history_funds_flow(market_type,data_num)
    print(info)

if __name__ == '__main__':
    asyncio.run(test_get_market_history_funds_flow())
