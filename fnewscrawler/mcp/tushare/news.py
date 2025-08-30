import pandas as pd

from fnewscrawler.spiders.tushare import short_news
from fnewscrawler.mcp import mcp_server


def dataframe2str(df: pd.DataFrame) -> str:
    """将 DataFrame 转换为字符串
    格式化新闻文本
    """
    str_content = ""
    for index, row in df.iterrows():
        str_content += f"时间：{row['datetime']}\n"
        str_content += f"内容：{row['content']}\n"
        str_content += "\n\n"
    return str_content


@mcp_server.tool(title="从指定数据源获取股票新闻数据", enabled=False)
def ts_short_news(start_date:str, end_date:str, src:str = "10jqka"):
    """从指定数据源获取股票新闻数据，该工具将获取大量的股票新闻数据，注意start_date和end_date的范围。

    Args:
        start_date: 开始日期，格式'YYYY-MM-DD'
        end_date: 结束日期，格式'YYYY-MM-DD'
        src: 数据源，默认'10jqka'
        来源名称	src标识	描述
        新浪财经	sina	获取新浪财经实时资讯
        华尔街见闻	wallstreetcn	华尔街见闻快讯
        同花顺	10jqka	同花顺财经新闻
        东方财富	eastmoney	东方财富财经新闻
        云财经	yuncaijing	云财经新闻
        凤凰新闻	fenghuang	凤凰新闻
        金融界	jinrongjie	金融界新闻
        财联社	cls	财联社快讯
        第一财经	yicai	第一财经快讯

    Returns:
        股票新闻数据，包含时间、内容

    注意：受到redis缓存的限制(一旦查询便入缓存，key为start_date和end_date组合)，获取最新一天的数据可能会造成延迟，建议获取数据时设置start_date为前一天。
    注意：获取的数据量可能会很大，建议在获取数据前先确认数据量。
    """
    df = short_news(start_date, end_date, src)
    if not df.empty:
        str_content = dataframe2str(df)
        return str_content
    return "空数据，没有新闻"

