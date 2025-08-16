from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager




table_columns_map={
    "沪深两市": ["日期",  "上证收盘价", "上证涨跌幅",
                   "深市收盘价", "深市涨跌幅", "主力净流入净额", "主力净流入净占比","超大单净流入净额", "超大单净流入净占比","大单净流入净额", "大单净流入净占比",
                   "中单净流入净额", "中单净流入净占比", "小单净流入净额", "小单净流入净占比"],
    "沪市": ["日期", "上证收盘价", "上证涨跌幅", "沪市主力净流入净额", "沪市主力净流入净占比",
                   "沪市超大单净流入净额", "沪市超大单净流入净占比", "沪市大单净流入净额", "沪市大单净流入净占比",
                   "沪市中单净流入净额", "沪市中单净流入净占比", "沪市小单净流入净额", "沪市小单净流入净占比"],
    "深市": ["日期", "深市收盘价", "深市涨跌幅", "深市主力净流入净额", "深市主力净流入净占比",
                   "深市超大单净流入净额", "深市超大单净流入净占比", "深市大单净流入净额", "深市大单净流入净占比",
                   "深市中单净流入净额", "深市中单净流入净占比", "深市小单净流入净额", "深市小单净流入净占比"],
    "创业板": ["日期", "创业板收盘价", "创业板涨跌幅", "创业板主力净流入净额", "创业板主力净流入净占比",
                   "创业板超大单净流入净额", "创业板超大单净流入净占比", "创业板大单净流入净额", "创业板大单净流入净占比",
                   "创业板中单净流入净额", "创业板中单净流入净占比", "创业板小单净流入净额", "创业板小单净流入净占比"],
    "沪B": ["日期", "沪B收盘价", "沪B涨跌幅", "沪B主力净流入净额", "沪B主力净流入净占比",
             "沪B超大单净流入净额", "沪B超大单净流入净占比", "沪B大单净流入净额", "沪B大单净流入净占比",
             "沪B中单净流入净额", "沪B中单净流入净占比", "沪B小单净流入净额", "沪B小单净流入净占比"],
    "深B": ["日期", "深B收盘价", "深B涨跌幅", "深B主力净流入净额", "深B主力净流入净占比",
             "深B超大单净流入净额", "深B超大单净流入净占比", "深B大单净流入净额", "深B大单净流入净占比",
             "深B中单净流入净额", "深B中单净流入净占比", "深B小单净流入净额", "深B小单净流入净占比"]
}



async def eastmoney_market_history_funds_flow(market_type: str= "沪深两市", data_num: int = 40)-> str:
    """
        获取股票行业个股资金流信息
        :return: 行业个股资金流信息
        """
    url = "https://data.eastmoney.com/zjlx/dpzjlx.html"
    if market_type not in table_columns_map:
        return "不支持的市场类型,仅支持沪深两市,沪市,深市,创业板,沪B,深B"

    clumns_name = table_columns_map[market_type]

    context = await context_manager.get_context("eastmoney")
    page = None
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # 刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")

        await page.locator(f".linklab:has-text('{market_type}')").click()
        await page.wait_for_load_state("domcontentloaded")
        # 确保表格主体可见，避免在数据加载前抓取
        await page.locator("#table_ls.dataview").wait_for(state="visible")
            # 提取表格的 HTML 字符串
            # await page.locator(".dataview-body").wait_for(state="visible")
        table_html = await page.locator("#table_ls.dataview").inner_html()
        current_df = pd.read_html(StringIO(table_html))[0]

        if not current_df.empty:
            # 手动设置列名
            current_df.columns = clumns_name
            final_df = current_df.drop_duplicates()
            data_num = min(data_num, len(final_df))
            final_df = final_df.head(data_num)
            # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table

        else:
            return "没有大市场历史资金流信息"


    except Exception as e:
        return f"获取大市场历史资金流信息失败: {e}"

    finally:
        if page:
            await page.close()