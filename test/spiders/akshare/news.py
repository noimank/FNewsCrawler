from fnewscrawler.spiders.akshare import ak_news_cctv,ak_stock_news_em


def test_ak_news_cctv():
    news_cctv_df = ak_news_cctv('20250829')
    print(news_cctv_df)

def test_ak_stock_news_em():
    stock_news_em_df = ak_stock_news_em('000001')
    print(stock_news_em_df)

if __name__ == '__main__':
    # test_ak_news_cctv()

    test_ak_stock_news_em()
