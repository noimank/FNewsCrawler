import asyncio
import io

import pandas as pd

from fnewscrawler.core import get_redis
from fnewscrawler.core.context import context_manager
from fnewscrawler.utils import LOGGER


async def fetch_page_data(context, url, rank_type):
    """获取单个页面的数据"""
    redis = get_redis()
    redis_key = f"iwencai_concept_funds_{rank_type}_{url}"
    # redis.delete(redis_key)
    if redis.exists(redis_key) and rank_type in ["3day", "5day", "10day", "20day"]:
        return redis.get(redis_key, serializer="pickle")

    page = None
    try:
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector("table", timeout=5000)
        
        # 获取表格的HTML内容
        html_content = await page.locator("table").inner_html()
        html_content = f"<table>{html_content}</table>"  # 添加完整的table标签
        
        # 使用pandas解析HTML表格
        df = pd.read_html(io.StringIO(html_content))[0]

        # 缓存数据，半天后过期
        if rank_type.lower() in ["3day", "5day", "10day", "20day"]:
            redis.set(redis_key, df, ex=43200, serializer="pickle")

        return df
    except Exception as e:
        LOGGER.error(f"iwencai_concept_funds：获取页面 {url} 数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        if page:
            try:
                await page.close()
            except Exception as e:
                LOGGER.error(f"iwencai_concept_funds：关闭页面失败: {str(e)}")


async def iwencai_concept_funds(rank_type: str = "1day"):
    """
    获取概念资金排名
    :param rank_type: 排名类型，可选值：1day（1天），3day（3天），5day（5天），10day（10天），20day（20天）
    :return: 概念资金排名数据
    """
    
    url_map = {
        "1day": ["https://data.10jqka.com.cn/funds/gnzjl/field/tradezdf/order/desc/ajax/1/"] + [f"https://data.10jqka.com.cn/funds/gnzjl/field/tradezdf/order/desc/page/{i}/ajax/1/" for i in range(2, 9)],
        "3day": ["https://data.10jqka.com.cn/funds/gnzjl/board/3/ajax/1/"] + [f"https://data.10jqka.com.cn/funds/gnzjl/board/3/field/tradezdf/order/desc/page/{i}/ajax/1/" for i in range(2, 9)],
        "5day": ["https://data.10jqka.com.cn/funds/gnzjl/board/5/ajax/1/"] + [f"https://data.10jqka.com.cn/funds/gnzjl/board/5/field/tradezdf/order/desc/page/{i}/ajax/1/" for i in range(2, 9)],
        "10day": ["https://data.10jqka.com.cn/funds/gnzjl/board/10/ajax/1/"] + [f"https://data.10jqka.com.cn/funds/gnzjl/board/10/field/tradezdf/order/desc/page/{i}/ajax/1/" for i in range(2, 9)],
        "20day": ["https://data.10jqka.com.cn/funds/gnzjl/board/20/ajax/1/"] + [f"https://data.10jqka.com.cn/funds/gnzjl/board/20/field/tradezdf/order/desc/page/{i}/ajax/1/" for i in range(2, 9)],
    }

    context = await context_manager.get_context("iwencai")

    try:
        urls = url_map.get(rank_type, [])
        
        # 使用gather并发获取所有页面数据，每个URL创建独立的page
        tasks = [fetch_page_data(context, url, rank_type) for url in urls]
        dfs = await asyncio.gather(*tasks)
        
        # 过滤掉空的DataFrame并合并所有页面数据
        valid_dfs = [df for df in dfs if not df.empty]
        if valid_dfs:
            # 使用pandas concat直接合并DataFrame，保留原有列名
            result_df = pd.concat(valid_dfs, ignore_index=True)
            
            # 转换为markdown格式
            markdown_table = result_df.to_markdown(index=False)
            return markdown_table
        else:
            return "未获取到数据"

    except Exception as e:
        LOGGER.error(f"iwencai_concept_funds：获取概念资金排名失败: {str(e)}")
        return f"获取数据失败: {str(e)}"
