from fnewscrawler.spiders.tushare import stock_cyq_chips, stock_cyq_perf
import asyncio
async def test_stock_cyq_chips():
    df = await stock_cyq_chips("000001", "20230101", "20230105")
    print(df)


async def test_stock_cyq_perf():
    df = await stock_cyq_perf("600519", "20240101", "20250101")
    print(df)
    print(df.shape)


if __name__ == "__main__":
    # asyncio.run(test_stock_cyq_chips())
    asyncio.run(test_stock_cyq_perf())
