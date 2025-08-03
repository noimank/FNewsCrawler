from fnewscrawler.spiders.iwencai import iwencai_industry_funds
from fnewscrawler.mcp import mcp_server
from typing import Literal


@mcp_server.tool(
    title="同花顺问财行业资金流向查询",
    description="""
    获取同花顺问财平台的行业资金流向数据，显示各行业的资金净流入/流出情况。

    数据包含字段：
    - 序号：行业排名顺序
    - 行业：具体行业名称（如中药、化学制药、影视院线等）
    - 公司家数：该行业包含的上市公司数量
    - 行业指数：对应的行业指数数值
    - 阶段涨跌幅：指定时间周期内的涨跌幅度（%）
    - 流入资金：资金流入金额（亿元）
    - 流出资金：资金流出金额（亿元）
    - 净额：净流入金额，正数表示净流入，负数表示净流出（亿元）

    使用场景：
    - 识别资金热点行业和冷门行业
    - 分析市场资金配置偏好
    - 跟踪行业资金流动趋势
    - 辅助投资决策和行业轮动分析

    注意事项：
    - 数据实时更新，反映最新市场资金流向
    - 净额为负值表示该行业资金净流出
    - 建议结合涨跌幅数据综合分析
    """
)
async def get_iwencai_industry_funds(
        rank_type: Literal["1day", "3day", "5day", "10day", "20day"] = "1day"
) -> str:
    """
    获取同花顺问财行业资金流向数据

    Args:
        rank_type: 统计时间周期
            - "1day": 1日资金流向 (默认)
            - "3day": 3日资金流向
            - "5day": 5日资金流向
            - "10day": 10日资金流向
            - "20day": 20日资金流向

    Returns:
        str: Markdown表格格式的行业资金流向数据，包含以下列：
            - 序号：行业排名
            - 行业：行业名称
            - 公司家数：该行业上市公司数量
            - 行业指数：对应行业指数值
            - 阶段涨跌幅：时间周期内涨跌幅(%)
            - 流入资金(亿)：资金流入金额
            - 流出资金(亿)：资金流出金额
            - 净额(亿)：净流入金额(正数=净流入，负数=净流出)

    Raises:
        ValueError: 当传入不支持的rank_type参数时
        Exception: 数据获取失败时

    Example:
        >>> result = await get_iwencai_industry_funds("1day")
        >>> print(result)
        # 输出示例：
        # |   序号 | 行业      |   公司家数 |     行业指数 |   阶段涨跌幅 |   流入资金(亿) |   流出资金(亿) |   净额(亿) |
        # |-----:|:--------|-------:|---------:|--------:|----------:|----------:|--------:|
        # |    1 | 中药      |     69 |  3733.52 |    5.47 |     39.31 |     55.69 |  -16.38 |
        # |    2 | 化学制药    |    158 |  7322.04 |    5.39 |    186.64 |    226.95 |  -40.31 |
    """
    # 参数验证
    valid_periods = ["1day", "3day", "5day", "10day", "20day"]
    if rank_type not in valid_periods:
        raise ValueError(
            f"不支持的时间周期参数: {rank_type}。"
            f"仅支持以下选项: {', '.join(valid_periods)}"
        )

    try:
        # 调用爬虫函数获取数据
        markdown_table = await iwencai_industry_funds(rank_type)

        # 添加数据说明头部
        time_mapping = {
            "1day": "1日",
            "3day": "3日",
            "5day": "5日",
            "10day": "10日",
            "20day": "20日"
        }

        result = f"""# 同花顺问财 - {time_mapping[rank_type]}行业资金流向

> **数据说明**：{time_mapping[rank_type]}内各行业资金流入流出统计
> **数据来源**：同花顺问财平台（实时更新）
> **金额单位**：亿元

{markdown_table}

**数据解读**：
- **净额 > 0**：该行业获得资金净流入，市场看好
- **净额 < 0**：该行业出现资金净流出，资金观望或撤离  
- **阶段涨跌幅**：可结合资金流向判断行业热度与表现匹配度
- **公司家数**：反映行业规模，家数多的行业数据更具代表性
"""
        return result

    except Exception as e:
        error_msg = f"获取行业资金流向数据失败: {str(e)}"
        return f"## 错误\n\n{error_msg}\n\n请稍后重试或检查网络连接。"


