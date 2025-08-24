from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.iwencai import iwencai_concept_funds
from typing import Literal


@mcp_server.tool(
    title="同花顺问财概念板块资金流向查询"
)
async def get_iwencai_concept_funds(
        rank_type: Literal["1day", "3day", "5day", "10day", "20day"] = "1day"
) -> str:
    """
    获取同花顺问财平台的概念板块资金流向数据
    显示各热门概念的资金净流入/流出情况。

    Args:
        rank_type: 统计时间周期
            - "1day": 1日资金流向 (默认) - 适合捕捉短期题材热点
            - "3day": 3日资金流向 - 观察短期趋势持续性
            - "5day": 5日资金流向 - 分析周度概念轮动
            - "10day": 10日资金流向 - 判断中期资金偏好
            - "20day": 20日资金流向 - 识别长期投资主题

    Returns:
        str: Markdown表格格式的概念板块资金流向数据，包含以下列：
            - 序号：概念排名
            - 行业：概念板块名称（注意：此处显示为"行业"列名，实际为概念板块）
            - 公司家数：该概念相关上市公司数量
            - 行业指数：对应概念板块指数值
            - 阶段涨跌幅：时间周期内涨跌幅，格式为百分比（如16.82%）
            - 流入资金(亿)：资金流入金额
            - 流出资金(亿)：资金流出金额
            - 净额(亿)：净流入金额(正数=净流入，负数=净流出)

    Raises:
        ValueError: 当传入不支持的rank_type参数时
        Exception: 数据获取失败时

    Example:
        >>> result = await get_iwencai_concept_funds("1day")
        >>> print(result)
        # 输出示例：
        # |   序号 | 行业           |   公司家数 |     行业指数 | 阶段涨跌幅   |   流入资金(亿) |   流出资金(亿) |   净额(亿) |
        # |-----:|:-------------|-------:|---------:|:--------|----------:|----------:|--------:|
        # |    1 | CRO概念        |     67 |   869.44 | 16.82%  |     71.55 |     69.48 |    2.07 |
        # |    2 | 创新药          |    242 |  1435.63 | 16.78%  |    255.8  |    258.76 |   -2.96 |
        # |    3 | 减肥药          |     55 |  1460.43 | 14.46%  |     84.82 |     84.7  |    0.12 |
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
        markdown_table = await iwencai_concept_funds(rank_type)

        time_mapping = {
            "1day": "1日",
            "3day": "3日",
            "5day": "5日",
            "10day": "10日",
            "20day": "20日"
        }

        result = f"""# 同花顺问财 - {time_mapping[rank_type]}概念板块资金流向

> **数据说明**：{time_mapping[rank_type]}内各概念板块资金流入流出统计
> **数据来源**：同花顺问财平台（实时更新）
> **金额单位**：亿元

{markdown_table}

**投资解读**：
- **强势概念**：涨幅较高且净流入为正的概念板块，如示例中的CRO概念、细胞免疫治疗
- **分歧概念**：涨幅较高但净流出的概念，如创新药，反映获利了结压力
- **平衡概念**：流入流出相对均衡的概念，如减肥药，市场观点相对中性
- **涨幅评估**：关注10%以上涨幅的概念，通常为当期市场热点

**选股建议**：
- **优选标准**：涨幅适中(5%-15%)且净流入为正的概念板块
- **公司筛选**：在热门概念中选择公司家数适中(30-100家)的板块
- **持续跟踪**：对比多日数据，关注资金流向的连续性和稳定性
"""

        return result

    except Exception as e:
        error_msg = f"获取概念板块资金流向数据失败: {str(e)}"
        return f"## 错误\n\n{error_msg}\n\n请稍后重试或检查网络连接。"


# 提供便捷的热点概念查询工具
@mcp_server.tool(
    title="今日热门概念板块资金流向",
    description="快速获取当日最热门的概念板块资金流向，用于捕捉市场短期热点和题材机会",
    enabled=False
)
async def get_today_hot_concepts() -> str:
    """
    获取今日热门概念板块资金流向

    Returns:
        str: Markdown格式的概念板块资金流向数据
    """
    return await iwencai_concept_funds("1day")


@mcp_server.tool(
    title="概念板块周度资金趋势分析",
    description="获取5日概念板块资金流向，用于分析概念轮动趋势和中短期投资机会",
    enabled=False

)
async def get_weekly_concept_trends() -> str:
    """
    获取概念板块周度资金流向趋势

    Returns:
        str: Markdown格式的概念板块周度资金流向数据
    """
    return await iwencai_concept_funds("5day")


@mcp_server.tool(
    title="概念板块资金流向对比分析",
    description="同时获取1日和5日概念资金流向数据，便于对比分析短期热点与中期趋势",
    enabled=False

)
async def compare_concept_fund_flows() -> str:
    """
    对比分析概念板块短期与中期资金流向

    Returns:
        str: Markdown格式的概念板块资金流向对比数据
    """
    try:
        daily_data = await iwencai_concept_funds("1day")
        weekly_data = await iwencai_concept_funds("5day")

        result = f"""# 概念板块资金流向对比分析

## 短期热点（1日数据）
{daily_data}

---

## 中期趋势（5日数据）  
{weekly_data}

---

**对比分析建议**：
- 在两个时间周期都表现强势的概念，通常具有更好的持续性
- 仅在短期表现的概念，需警惕题材炒作风险
- 中期强势但短期回调的概念，可能存在低吸机会
"""
        return result

    except Exception as e:
        return f"## 错误\n\n获取对比数据失败: {str(e)}\n\n请稍后重试。"