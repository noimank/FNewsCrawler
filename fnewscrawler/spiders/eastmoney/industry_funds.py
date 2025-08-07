import asyncio

from fnewscrawler.core import  context_manager
from .utils import  eastmoney_industry_map


from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager


async def get_industry_stock_funds_flow(industry_name: str)-> str:
    """
    获取股票行业个股资金流信息
    :return: 行业个股资金流信息
    """
    industry_code = eastmoney_industry_map.get(industry_name)
    if not industry_code:
        return "行业名称不存在"
    url = f"https://data.eastmoney.com/bkzj/{industry_code}.html"

    context = await context_manager.get_context("eastmoney")
    clumns_name = ["序号", "代码", "名称", "相关","最新价", "今日涨跌幅", "今日主力净流入净额", "今日主力净流入净占比", "今日超大单净流入净额", "今日超大单净流入净占比", "今日大单净流入净额", "今日大单净流入净占比", "今日中单净流入净额", "今日中单净流入净占比", "今日小单净流入净额", "今日小单净流入净占比"]
    page = None
    dfs =[]
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        #刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")
        # 确保表格主体可见，避免在数据加载前抓取
        await page.locator(".dataview-body").wait_for(state="visible")
        while True:
            # 提取表格的 HTML 字符串
            # await page.locator(".dataview-body").wait_for(state="visible")
            table_html = await page.locator(".dataview-body").inner_html()
            current_df = pd.read_html(StringIO(table_html))[0]

            if not current_df.empty:
                    # 手动设置列名
                    current_df.columns = clumns_name
                    # final_df = current_df.drop_duplicates()
                    # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
                    # markdown_table = final_df.to_markdown(index=False)
                    dfs.append(current_df)

            # page_text = await page.locator(".pagerbox").inner_text()
            page_text = await page.locator(".dataview-pagination.tablepager").inner_text()
            #
            if "下一页" not in page_text:
                break

            if "下一页" in page_text:
                await page.locator("text=下一页").click()
                await page.wait_for_load_state("domcontentloaded")
                #不加这个一定会有莫名其妙的问题，选择1秒还是比较激进了，后期如果有问题，考虑增大，这条语句的位置不要该，domcontentloaded不要改，换成networkidle会卡死
                await asyncio.sleep(1)

        if len(dfs) ==0:
            return "没有行业资金流信息"
        else:
            final_df = pd.concat(dfs, ignore_index=True)
            #把相关这一列删除
            final_df = final_df.drop(columns=["相关"])
            final_df = final_df.drop_duplicates()
            return final_df.to_markdown(index=False)

    except Exception as e:
        return f"获取行业资金流信息失败: {e}"

    finally:
        if page:
            await page.close()



async def get_industry_history_funds_flow(industry_name: str)-> str:
    """
        获取股票行业个股资金流信息
        :return: 行业个股资金流信息
        """
    industry_code = eastmoney_industry_map.get(industry_name)
    if not industry_code:
        return "行业名称不存在"
    url = f"https://data.eastmoney.com/bkzj/{industry_code}.html"

    context = await context_manager.get_context("eastmoney")
    clumns_name = ["日期",  "主力净流入净额", "主力净流入净占比",
                   "超大单净流入净额", "超大单净流入净占比", "大单净流入净额", "大单净流入净占比",
                   "中单净流入净额", "中单净流入净占比", "小单净流入净额", "小单净流入净占比"]
    page = None
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # 刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")

        await page.locator("text=行业历史资金流").click()
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
            # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table

        else:
            return "没有行业历史资金流信息"


    except Exception as e:
        return f"获取行业历史资金流信息失败: {e}"

    finally:
        if page:
            await page.close()



