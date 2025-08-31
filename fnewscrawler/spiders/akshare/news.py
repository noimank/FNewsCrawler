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
