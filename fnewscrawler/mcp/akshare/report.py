from fnewscrawler.spiders.akshare import ak_stock_zh_a_disclosure_report_cninfo
from fnewscrawler.mcp import mcp_server



@mcp_server.tool(title="从akshare获取股票信息披露公告数据")
def get_ak_stock_zh_a_disclosure_report_cninfo(stock_code: str, start_date: str = "20250829")->str:
    """从akshare获取股票信息披露公告数据

    来源： 巨潮资讯-首页-公告查询-信息披露公告-沪深京股票

    Args:
        stock_code: 股票代码，如'000001'
        start_date: 开始日期，格式'YYYYMMDD'，如'20250829'

    Returns:
        包含股票信息披露公告数据的markdown表格，列名包括：代码、公告标题、公告时间、公告链接
    """
    df = ak_stock_zh_a_disclosure_report_cninfo(stock_code, start_date)
    markdown_table = df.to_markdown(index=False)
    return markdown_table

