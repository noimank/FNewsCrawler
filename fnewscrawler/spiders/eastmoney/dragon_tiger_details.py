import asyncio
from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager


async def eastmoney_dragon_tiger_detail(rank_type="1day", page_num=1)-> str:
    """
    获取龙虎榜信息
    :param rank_type: 排行类型，1day, 3day, 5day, 10day, 30day
    :param page_num: 页码
    :return: 龙虎榜信息
    """
    url = "https://data.eastmoney.com/stock/tradedetail.html"
    if rank_type not in ["1day", "3day","5day", "10day", "30day"]:
        return "rank_type参数错误,仅支持：1day, 3day, 5day, 10day, 30day"

    context = await context_manager.get_context("eastmoney")
    columns_name = ["序号", "代码", "名称", "相关","解读", "收盘价", "涨跌幅",
                   "龙虎榜净买额(万)", "龙虎榜买入额(万)", "龙虎榜卖入额(万)", "龙虎榜成交额(万)", "市场总成交额(万)", "净买额占总成交比", "成交额占总成交比", "换手率",
            "流通市值(亿)", "上榜原因"]
    if rank_type != "1day":
        columns_name =  ["序号", "代码", "名称", "相关","上榜日", "解读", "收盘价", "涨跌幅",
                   "龙虎榜净买额(万)", "龙虎榜买入额(万)", "龙虎榜卖入额(万)", "龙虎榜成交额(万)", "市场总成交额(万)", "净买额占总成交比", "成交额占总成交比", "换手率",
            "流通市值(亿)", "上榜原因", "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日"]


    page = None
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        #刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(1.2)

        if rank_type == "3day":
            await page.locator("text=近3日").click()
            #控制页面下滑
            await page.mouse.wheel(0, 1000)
        elif rank_type == "5day":
            await page.locator("text=近5日").click()
            await page.mouse.wheel(0, 1300)
        elif rank_type == "10day":
            await page.locator("text=近10日").click()
            await page.mouse.wheel(0, 900)
        elif rank_type == "30day":
            await page.locator("text=近30日").click()
            await page.mouse.wheel(0, 1100)

        await asyncio.sleep(1)
        # 增加分页逻辑
        if page_num > 1:
            page_text = await page.locator(".dataview-pagination.tablepager").inner_text()
            if "下一页" not in page_text:
                return "没有更多数据了，只有一页的数据"
            page_box = await page.locator(".pagerbox a").all()
            if page_num > len(page_box)-1:
                return f"切换到{page_num}页失败,没有更多数据了，只有{len(page_box)-1}页的数据"

            #填写跳转页码
            await page.locator("#gotopageindex").fill(str(page_num))
            # await page.locator(".btn").click()
            await asyncio.sleep(0.5)
            await page.get_by_role("button", name="确定").click()
            await page.wait_for_load_state("domcontentloaded")
            # await asyncio.sleep(2)

        #增加sleep，不然实在无法保证排行的表格会加载完成
        await asyncio.sleep(1)
        # 确保表格主体可见，避免在数据加载前抓取
        await page.locator(".dataview-body").wait_for(state="visible")
        # 提取表格的 HTML 字符串
        # await page.locator(".dataview-body").wait_for(state="visible")
        table_html = await page.locator(".dataview-body").inner_html()
        current_df = pd.read_html(StringIO(table_html))[0]

        #获取完整的上榜原因文字
        reason_list = []
        table_content = await page.locator(".dataview-body table tbody tr").all()
        for item in table_content:
            if rank_type == "1day":
                reason_title = await item.locator("td:nth-child(17)").locator("a").get_attribute("title")
                reason_list.append(reason_title)
            else:
                reason_title = await item.locator("td:nth-child(18)").locator("a").get_attribute("title")
                reason_list.append(reason_title)

        if not current_df.empty:
                # 手动设置列名
                current_df.columns = columns_name
                # 将“代码”列的数据类型转换为字符串
                current_df['代码'] = current_df['代码'].astype(str)
                # 使用 str.zfill() 方法补全前导零，例如，补到6位
                current_df['代码'] = current_df['代码'].str.zfill(6)
                current_df["上榜原因"] = reason_list
                final_df = current_df.drop(columns=["相关"])

                final_df = final_df.drop_duplicates()
                # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
                markdown_table = final_df.to_markdown(index=False)
                return markdown_table
        else:
                return "没有龙虎榜信息"

    except Exception as e:
        return f"获取龙虎榜信息失败: {e}"

    finally:
        if page:
            await page.close()

