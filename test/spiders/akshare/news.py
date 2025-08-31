from fnewscrawler.spiders.akshare import ak_news_cctv


def test_ak_news_cctv():
    news_cctv_df = ak_news_cctv('20250829')
    print(news_cctv_df)

if __name__ == '__main__':
    test_ak_news_cctv()
