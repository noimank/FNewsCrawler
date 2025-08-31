from fnewscrawler.spiders.akshare import ak_news_cctv
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
