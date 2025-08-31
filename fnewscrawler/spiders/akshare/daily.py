
import akshare as ak
import pandas as pd


def ak_daily(stock_code: str, start_date: str , end_date: str, adjust: str = "") -> pd.DataFrame:
    """获取股票日线数据

    Args:
        stock_code: 股票代码，如'000001'
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'
        adjust: 复权类型, None不复权, qfq: 前复权, hfq: 后复权

    Returns:
        包含股票日线数据的DataFrame，列名包括：日期、股票代码、开盘价、收盘价、最高价、最低价、成交量、成交额、振幅(%)、涨跌幅(%)、涨跌额(元)、换手率(%)
    """
    column_names = ["日期", "股票代码", "开盘价", "收盘价","最高价", "最低价", "成交量",   "成交额", "振幅(%)",  "涨跌幅(%)","涨跌额(元)","换手率(%)"]
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    stock_zh_a_hist_df.columns = column_names
    return stock_zh_a_hist_df



