import asyncio

import aiohttp

from fnewscrawler.spiders.iwencai import iwencai_A_stock_selection



async def test_select_condition():

    condition = "成交量小于100万，涨跌幅大于等于-5%小于等于0，macd买入信号，"
    condition = "机器人概念，涨超3%，非创业板，非st，流通股本大于10亿，每股现金流大于0.5元，每股收益增长率大于500%，"
    condition = "机器人概念"
    result = await iwencai_A_stock_selection(condition)
    print(result)



if __name__ == '__main__':
    asyncio.run(test_select_condition())



