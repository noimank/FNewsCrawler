import pandas as pd

from fnewscrawler.core import TushareDataProvider
from fnewscrawler.utils import LOGGER
from fnewscrawler.utils import deduplicate_text_df


def short_news( start_date: str, end_date: str, src: str = "10jqka"):
    """获取股票新闻数据

    地址：https://tushare.pro/document/2?doc_id=143

    接口：news
    描述：获取主流新闻网站的快讯新闻数据,提供超过6年以上历史新闻。
    限量：单次最大1500条新闻，可根据时间参数循环提取历史
    积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明

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
        包含股票筹码分布数据的DataFrame
    """
    tushare_data_provider = TushareDataProvider()
    query_key = f"stock_news_{start_date}_{end_date}_{src}"
    df = tushare_data_provider.get_cached_dataframe(query_key)
    if df is not None:
        LOGGER.info(f"stock_news: 从缓存中获取股票（短讯）新闻数据：{query_key}")
        return df
    try:
        pro = tushare_data_provider.pro
        df = pro.news(start_date=start_date, end_date=end_date, src=src)
        #第一层去重
        df = df.drop_duplicates(subset=["content"])
        #第二层去重
        df = deduplicate_text_df(df, "content")
        if not df.empty:
            tushare_data_provider.cache_dataframe(query_key, df)
        return df
    except Exception as e:
        LOGGER.error(f"stock_news: 获取股票（短讯）新闻数据失败：{query_key}，错误信息：{e}")
        return pd.DataFrame()

