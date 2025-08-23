
from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager


async def eastmoney_block_trade_detail(stock_code: str)-> str:
    """
    获取股票大宗交易每日明细
    :return: 股票大宗交易每日明细
    """
    url = f"https://data.eastmoney.com/dzjy/detail/{stock_code}.html"

    column_names = ["序号","交易日期", "涨跌幅(%)", "收盘价(元)", "成交价(元)", "折溢率(%)","成交量(万股)", "成交额(万元)", "成交额/流通市值", "买方营业部", "卖方营业部", "上榜1日后涨跌幅(%)"
                   , "上榜5日后涨跌幅(%)", "上榜10日后涨跌幅(%)", "上榜20日后涨跌幅(%)"]

    context = await context_manager.get_context("eastmoney")
    page = None
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # 刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")

        # 确保表格主体可见，避免在数据加载前抓取
        await page.locator(".dataview-body").wait_for(state="visible")
            # 提取表格的 HTML 字符串
            # await page.locator(".dataview-body").wait_for(state="visible")
        table_html = await page.locator(".dataview-body").inner_html()
        table_content = await page.locator(".dataview-body table tbody tr").all()
        buyer_list = []
        seller_list = []
        for item in table_content:
            #处理买方营业部从title中获取完整的名称
            buyer_title = await item.locator("td:nth-child(10)").locator("a").get_attribute("title")
            #处理卖方营业部从title中获取完整的名称
            seller_title = await item.locator("td:nth-child(11)").locator("a").get_attribute("title")
            buyer_list.append(buyer_title)
            seller_list.append(seller_title)

        current_df = pd.read_html(StringIO(table_html))[0]


        if not current_df.empty:
            # 手动设置列名
            current_df.columns = column_names
            current_df["买方营业部"] = buyer_list
            current_df["卖方营业部"] = seller_list
            final_df = current_df.drop_duplicates()
            # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table

        else:
            return "没有大宗交易历史数据"


    except Exception as e:
        return f"获取大宗交易历史数据失败: {e}"

    finally:
        if page:
            await page.close()