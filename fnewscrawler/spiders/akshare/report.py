from datetime import datetime

import akshare as ak


def ak_stock_zh_a_disclosure_report_cninfo(stock_code: str = "000001", start_date: str = "20230619"):
    """从akshare获取股票 信息披露公告 数据
    巨潮资讯-首页-公告查询-信息披露公告-沪深京股票
    Args:
        stock_code: 股票代码，如'000001'
        start_date: 开始日期，格式'YYYYMMDD'，如'20230619'
    """
    end_date = datetime.now().strftime("%Y%m%d")
    stock_zh_a_disclosure_report_cninfo_df = ak.stock_zh_a_disclosure_report_cninfo(symbol=stock_code, market='沪深京',
                                                                                    start_date=start_date,
                                                                                    end_date=end_date)
    # 去重
    stock_zh_a_disclosure_report_cninfo_df = stock_zh_a_disclosure_report_cninfo_df.drop_duplicates(subset=["公告链接"])

    stock_zh_a_disclosure_report_cninfo_df = stock_zh_a_disclosure_report_cninfo_df.drop(columns=["简称"])

    return stock_zh_a_disclosure_report_cninfo_df




if __name__ == '__main__':
    stock_zh_a_disclosure_report_cninfo_df = ak_stock_zh_a_disclosure_report_cninfo("000001", "20240619")
    print(stock_zh_a_disclosure_report_cninfo_df)
