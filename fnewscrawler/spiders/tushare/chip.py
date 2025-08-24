from fnewscrawler.core import TushareDataProvider
from fnewscrawler.utils import LOGGER



async def stock_cyq_perf(stock_code: str, start_date: str, end_date: str):
    """获取股票筹码分布数据

    地址：https://tushare.pro/document/2?doc_id=293

    接口：cyq_perf
    描述：获取A股每日筹码平均成本和胜率情况，每天17~18点左右更新，数据从2018年开始
    来源：Tushare社区
    限量：单次最大5000条，可以分页或者循环提取
    积分：120积分可以试用(查看数据)，5000积分每天20000次，10000积分每天200000次，15000积分每天不限总量

    Args:
        stock_code: 股票代码
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'

    Returns:
        包含股票筹码分布数据的DataFrame
    """
    tushare_data_provider = TushareDataProvider()
    query_key = f"stock_cyq_perf_{stock_code}_{start_date}_{end_date}"
    df = tushare_data_provider.get_cached_dataframe(query_key)
    if df is not None:
        LOGGER.info(f"stock_cyq_perf: 从缓存中获取股票筹码分布数据：{query_key}")
        return df

    ts_code = tushare_data_provider.code2tscode(stock_code)
    pro = tushare_data_provider.pro
    df = pro.cyq_perf(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if not df.empty:
        tushare_data_provider.cache_dataframe(query_key, df)
    return df



async def stock_cyq_chips(stock_code: str, start_date: str, end_date: str):
    """获取股票筹码分布数据

    地址：https://tushare.pro/document/2?doc_id=294

    接口：cyq_chips
    描述：获取A股每日的筹码分布情况，提供各价位占比，数据从2018年开始，每天17~18点之间更新当日数据
    来源：Tushare社区
    限量：单次最大2000条，可以按股票代码和日期循环提取
    积分：120积分可以试用查看数据，5000积分每天20000次，10000积分每天200000次，15000积分每天不限总量

    Args:
        stock_code: 股票代码
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'

    Returns:
        包含股票筹码分布数据的DataFrame
    """
    tushare_data_provider = TushareDataProvider()
    query_key = f"stock_cyq_chips_{stock_code}_{start_date}_{end_date}"
    df = tushare_data_provider.get_cached_dataframe(query_key)
    if df is not None:
        LOGGER.info(f"stock_cyq_chips: 从缓存中获取股票筹码分布数据：{query_key}")
        return df

    ts_code = tushare_data_provider.code2tscode(stock_code)
    pro = tushare_data_provider.pro
    df = pro.cyq_chips(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if not df.empty:
        tushare_data_provider.cache_dataframe(query_key, df)

    return df







