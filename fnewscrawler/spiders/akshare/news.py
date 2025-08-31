import akshare as ak


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
