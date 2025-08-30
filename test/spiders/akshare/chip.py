from fnewscrawler.spiders.akshare import stock_cyq_em


def test_stock_cyq_chips():
    df =  stock_cyq_em("000001", "")
    print(df)



if __name__ == "__main__":
    # asyncio.run(test_stock_cyq_chips())
    test_stock_cyq_chips()
