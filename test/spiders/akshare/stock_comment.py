
from fnewscrawler.spiders.akshare import ak_stock_comment_detail


def test_ak_stock_comment_detail():
    stock_code = "600000"
    df = ak_stock_comment_detail(stock_code)
    print(df)


if __name__ == '__main__':
    test_ak_stock_comment_detail()
