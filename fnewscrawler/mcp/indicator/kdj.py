from fnewscrawler.core import TushareDataProvider
from fnewscrawler.mcp import mcp_server
from fnewscrawler.utils import format_param


@mcp_server.tool(
    title="获取指定股票的KDJ技术指标"
)
def stock_kdj(
        stock_code: str,
        start_date: str,
        end_date: str,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3
):
    """
    计算指定股票的KDJ技术指标

    Args:
        stock_code (str): 股票代码，如'000001'
        start_date (str): 起始日期，格式'YYYYMMDD'
        end_date (str): 结束日期，格式'YYYYMMDD'
        fastk_period (int, optional): RSV周期. 默认值: 9
        slowk_period (int, optional): K值平滑周期. 默认值: 3
        slowd_period (int, optional): D值平滑周期. 默认值: 3

    Returns:
        str: 包含KDJ指标数据的Markdown格式表格
    """
    ts_data_provider = TushareDataProvider()
    ts_code = ts_data_provider.code2tscode(stock_code)
    data = ts_data_provider.get_stock_daily(ts_code, start_date, end_date)
    fastk_period = format_param(fastk_period, int)
    slowk_period = format_param(slowk_period, int)
    slowd_period = format_param(slowd_period, int)
    if data.empty:
        return "获取股票数据失败"

    # 检查数据是否足够
    if len(data) < max(fastk_period, slowk_period, slowd_period):
        return "数据不足，无法计算KDJ指标"

    # 按交易日升序排序
    data = data.sort_values(by='trade_date').reset_index(drop=True)

    # ------------------------ 计算 RSV（未成熟随机值）------------------------
    # 公式：RSV = (CLOSE - LLV(LOW,9)) / (HHV(HIGH,9) - LLV(LOW,9)) * 100
    data['LLV'] = data['low'].rolling(window=fastk_period).min()
    data['HHV'] = data['high'].rolling(window=fastk_period).max()

    # 防止除零（如一字板导致 HHV == LLV）
    rsv_raw = (data['close'] - data['LLV']) / (data['HHV'] - data['LLV']) * 100
    data['RSV'] = rsv_raw.fillna(0).clip(0, 100)  # 填充 NaN 为 0，并限制在 [0,100]

    # ------------------------ 手动计算 K、D、J ------------------------
    k_values = []
    d_values = []

    for i in range(len(data)):
        rsv = data['RSV'].iloc[i]
        if i == 0:
            # 初始值：K=50, D=50
            k = 50.0
            d = 50.0
        else:
            prev_k = k_values[-1]
            prev_d = d_values[-1] if d_values else 50.0

            # 使用 m1 实现 SMA(RSV, m1, 1): K = (m1-1)/m1 * K_前 + 1/m1 * RSV
            k = ((slowk_period - 1) * prev_k + rsv) / slowk_period

            # 使用 m2 实现 SMA(K, m2, 1): D = (m2-1)/m2 * D_前 + 1/m2 * K
            d = ((slowd_period - 1) * prev_d + k) / slowd_period

        k_values.append(k)
        d_values.append(d)

    # 添加到 DataFrame
    data['K'] = k_values
    data['D'] = d_values
    data['J'] = 3 * data['K'] - 2 * data['D']

    # ------------------------ 输出结果 ------------------------
    # 只保留从第 n 天开始的有效数据（前 n-1 天 RSV 不完整）
    result_df = data[['trade_date', 'K', 'D', 'J']].iloc[fastk_period - 1:].reset_index(drop=True)

    # 丢弃nan
    result_df = result_df.dropna()
    # 转换为Markdown格式
    markdown_table = result_df.to_markdown(index=False)

    return markdown_table
