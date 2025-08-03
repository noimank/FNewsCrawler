import asyncio
import re
from typing import List
from io import StringIO

import pandas as pd
from playwright.async_api import Page

from fnewscrawler.core.context import context_manager
from fnewscrawler.utils import LOGGER


async def fetch_page_data(page: Page, url: str) -> pd.DataFrame:
    """获取单页数据的辅助函数"""
    await page.goto(url)
    await page.wait_for_selector('table')

    # 获取表格HTML内容
    table_html = await page.evaluate('() => document.querySelector("table").outerHTML')

    # 使用StringIO包装HTML字符串，避免deprecation警告
    html_io = StringIO(table_html)
    df = pd.read_html(html_io)[0]

    # 清理列名，移除可能的多级表头
    df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]

    # 清理数据中的特殊字符
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: re.sub(r'[\s%]+', '', str(x)) if pd.notnull(x) else x)

    return df


async def iwencai_industry_funds(rank_type="1day"):
    """获取同花顺行业资金流向数据"""

    # 定义不同时间周期对应的页面编号
    period_map = {
        "1day": ["https://data.10jqka.com.cn/funds/hyzjl/ajax/1/",
                 "https://data.10jqka.com.cn/funds/hyzjl/field/tradezdf/order/desc/page/2/ajax/1/"],
        "3day": ["https://data.10jqka.com.cn/funds/hyzjl/board/3/ajax/1/",
                 "https://data.10jqka.com.cn/funds/hyzjl/board/3/field/tradezdf/order/desc/page/2/ajax/1/"],
        "5day": ["https://data.10jqka.com.cn/funds/hyzjl/board/5/ajax/1/",
                 "https://data.10jqka.com.cn/funds/hyzjl/board/5/field/tradezdf/order/desc/page/2/ajax/1/"],
        "10day": ["https://data.10jqka.com.cn/funds/hyzjl/board/10/ajax/1/",
                  "https://data.10jqka.com.cn/funds/hyzjl/board/10/field/tradezdf/order/desc/page/2/ajax/1/"],
        "20day": ["https://data.10jqka.com.cn/funds/hyzjl/board/20/ajax/1/",
                  "https://data.10jqka.com.cn/funds/hyzjl/board/20/field/tradezdf/order/desc/page/2/ajax/1/"]
    }

    if rank_type not in period_map:
        raise ValueError(f"不支持的rank_type: {rank_type}，支持的选项为: {list(period_map.keys())}")

    context = None
    pages: List[Page] = []
    try:
        context = await context_manager.get_context("iwencai")

        # 根据URL数量创建对应数量的页面
        pages = [await context.new_page() for _ in range(len(period_map[rank_type]))]

        # 直接使用period_map中定义的URL
        urls = period_map[rank_type]

        # 使用gather并发获取数据
        tasks = [fetch_page_data(page, url) for page, url in zip(pages, urls)]
        dfs = await asyncio.gather(*tasks)

        # 合并数据
        final_df = pd.concat(dfs, ignore_index=True)

        # 转换为markdown格式
        markdown_table = final_df.to_markdown(index=False)

        return markdown_table

    except Exception as e:
        LOGGER.error(f"iwencai_industry_funds 错误: {str(e)}")
        raise

    finally:
        # 确保资源正确关闭
        for page in pages:
            try:
                await page.close()
            except Exception as e:
                LOGGER.error(f"iwencai_industry_funds 关闭页面时发生错误: {str(e)}")
