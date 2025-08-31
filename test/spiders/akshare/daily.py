from fnewscrawler.spiders.akshare import ak_daily



def test_ak_daily():
    df = ak_daily("000001", "20250601", "20250825")
    print(df)


if __name__ == "__main__":
    test_ak_daily()
