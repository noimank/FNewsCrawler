import akshare as ak
import pandas as pd


def ak_news_cctv(date: str)->str:
    """获取央视新闻联播文字稿数据

    Args:
        date: 日期，格式'YYYYMMDD'，如'20250829'

    Returns:
        包含新闻数据的DataFrame，列名包括：日期、内容
    """
    news_cctv_df = ak.news_cctv(date=date)
    #丢弃title
    news_cctv_df = news_cctv_df.drop(columns=["title"])
    #重命名列
    news_cctv_df = news_cctv_df.rename(columns={"date": "日期", "content": "内容"})
    markdown_table = news_cctv_df.to_markdown(index=False)
    return markdown_table


def ak_stock_news_em(stock_code: str)->str:
    """获取akshare股票新闻数据

    来源：东方财富，最近100条相关新闻，新闻内容并非完整，只是截取的部分内容

    Args:
        stock_code: 股票代码，如'600000'

    Returns:
        包含新闻数据的DataFrame，列名包括：新闻标题、新闻内容、发布时间、文章来源
    """
    stock_news_em_df = ak.stock_news_em(symbol=stock_code)
    #丢弃一些列
    stock_news_em_df = stock_news_em_df.drop(columns=["关键词", "新闻链接"])
    markdown_table = stock_news_em_df.to_markdown(index=False)
    return markdown_table



def ak_stock_news_main_cx(start_date: str = "20250829")->str:
    """获取akshare财经内容精选数据

    来源： 财新网-财新数据通-内容精选,返回start_date之后的新闻

    Args:
        start_date: 开始日期，格式'YYYYMMDD'，如'20250829'

    Returns:
        包含新闻数据的markdown表格，列名包括：新闻标题、新闻内容、发布时间、文章来源
    """
    stock_news_main_cx_df = ak.stock_news_main_cx()
    # 转换日期格式用于比较
    start_date = pd.to_datetime(start_date)
    # 转换pub_time为日期时间格式
    stock_news_main_cx_df["pub_time"] = pd.to_datetime(stock_news_main_cx_df["pub_time"])
    # 丢弃一些列
    stock_news_main_cx_df = stock_news_main_cx_df[stock_news_main_cx_df["pub_time"] >= start_date]
    stock_news_main_cx_df = stock_news_main_cx_df.drop(columns=["url", "interval_time"])
    # 重命名列
    stock_news_main_cx_df = stock_news_main_cx_df.rename(columns={"tag": "新闻标签", "summary": "新闻内容", "pub_time": "发布时间"})
    # 转换为markdown表格
    markdown_table = stock_news_main_cx_df.to_markdown(index=False)
    return markdown_table
