from fnewscrawler.spiders.akshare import ak_super_fun



def test_ak_super_fun():
    result = ak_super_fun('stock_zh_a_gbjg_em',  drop_columns="总股本，流通受限股份",symbol='603392.SH', return_type='json')
    print(result)
    print(type(result))




if __name__ == '__main__':
    test_ak_super_fun()

