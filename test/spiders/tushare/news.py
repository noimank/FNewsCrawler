
from fnewscrawler.spiders.tushare.news import short_news


def test_short_news():
    df = short_news( "2025-08-29", "2025-08-30")
    print(df)





if __name__ == "__main__":
    test_short_news()



