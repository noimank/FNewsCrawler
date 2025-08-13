from fnewscrawler.spiders.eastmoney import get_industry_history_funds_flow,get_industry_stock_funds_flow



async def test_get_industry_stock_funds_flow():
    industry_name = "中药"  #两页的
    industry_name = "教育"  #一页的
    industry_name = "电子元件"  #三页的
    rank_type = "1day"
    rank_type = "5day"
    # rank_type = "10day"
    info = await get_industry_stock_funds_flow(industry_name,rank_type)
    print(info)



async def test_get_industry_history_funds_flow():
    industry_name = "中药"  #两页的
    industry_name = "教育"  #一页的
    industry_name = "电子元件"  #三页的

    info = await get_industry_history_funds_flow(industry_name)
    print(info)




if __name__ == '__main__':
    import asyncio
    asyncio.run(test_get_industry_stock_funds_flow())


