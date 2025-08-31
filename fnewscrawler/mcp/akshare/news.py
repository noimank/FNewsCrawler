from fnewscrawler.spiders.akshare import ak_news_cctv, ak_stock_news_em
from fnewscrawler.mcp import mcp_server



@mcp_server.tool(title="从akshare获取新闻联播文字稿数据")
def get_ak_news_cctv(date: str)->str:
    """从akshare获取新闻联播文字稿数据

    Args:
        date: 日期，格式'YYYYMMDD'，如'20250829'

    Returns:
        包含新闻数据的markdown表格，列名包括：日期、内容
    """
    markdown_table = ak_news_cctv(date)
    return markdown_table


@mcp_server.tool(title="从akshare获取股票新闻数据")
def get_ak_stock_news_em(stock_code: str)->str:
    """从akshare获取股票新闻数据

    来源：东方财富，最近100条相关新闻，新闻内容并非完整，只是截取的部分内容

    Args:
        stock_code: 股票代码，如'600000'

    Returns:
        包含新闻数据的markdown表格，列名包括：新闻标题、新闻内容、发布时间、文章来源
    """
    markdown_table = ak_stock_news_em(stock_code)
    return markdown_table



