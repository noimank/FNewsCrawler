"""
问财A股选股爬虫模块

该模块提供了从问财网站(iwencai.com)抓取A股股票数据的功能。通过指定选股条件,
可以获取符合条件的股票列表及其相关信息。

主要功能:
1. 自动访问问财网站并输入选股条件
2. 处理分页数据,支持大量数据的抓取
3. 解析表格数据并转换为markdown格式输出

使用方法:
    result = await iwencai_A_stock_selection("你的选股条件")

参数说明:
    select_condition (str): 选股条件字符串,例如"涨停"、"昨日换手率大于5%"等

返回值:
    str: 成功时返回markdown格式的表格数据
         失败时返回错误信息字符串

注意事项:
    - 需要确保网络连接正常
    - 大量数据抓取时会自动处理分页
    - 返回数据会自动去重
    - 对于同一个查询条件，不同时间查询，其结果也会不同所以不考虑加上redis缓存
"""

import asyncio
from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager
from fnewscrawler.utils import LOGGER


async def iwencai_A_stock_selection(select_condition:str):

    base_url = "https://www.iwencai.com/unifiedwap/home/stock"

    context  = await  context_manager.get_context("iwencai")
    page = None
    all_dfs = []  # 用于存储每一页的 DataFrame

    try:
        page = await context.new_page()
        await page.goto(base_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.locator(".input-base-text").fill(select_condition)
        #点击搜索
        await page.locator(".other-btns").click()
        await page.wait_for_load_state("networkidle")


        # 在循环之前先提取一次表头，因为表头不会改变，问财的表头有点特殊，由固定表头和变化表头组成
        fixed_header_locator = page.locator(".iwc-table-fixed .iwc-table-header ul li")
        header_locator = page.locator(".iwc-table-header-ul.clearfix li")
        fixed_headers = await fixed_header_locator.all_inner_texts()
        headers = await header_locator.all_inner_texts()
        # 移除第一个空的表头，它通常是复选框
        fixed_headers[1] = "check_box"
        headers = [h for h in fixed_headers+headers if h.strip()]

        # 确保表头不为空，否则无法继续
        if not headers:
            return "无法解析表头，请检查定位器是否正确。"

        #获取选出了多少股
        stock_count = await page.locator(".table-count.ui-pr12 span").last.inner_text()
        stock_count = int(stock_count)
        if stock_count == 0:
            return f"在{select_condition}条件下没有选出任何股票"

        # print("stock_count========",stock_count)

        #因为超过10支股票后会有分页的按钮
        if stock_count >10:
            #切换成显示100页
            await page.locator(".drop-down-box").click()
            # 2. 等待下拉列表的选项可见
            # 这行代码不是必须的，但能增加脚本的健壮性
            await page.wait_for_selector("text=显示100条/页", state="visible")

            # 3. 点击包含 "显示100条/页" 文本的 li 元素
            # 使用 text 定位器可以精确找到包含该文本的元素
            await page.locator("li:has-text('显示100条/页')").click()

            # 等待页面重新加载
            await page.wait_for_load_state("networkidle")

        #加一秒延迟吧，不然数据可能多一点或者少一点的情况出现
        await asyncio.sleep(1)
        if stock_count <= 100:
            await page.wait_for_selector(".iwc-table-container", state="visible")
            table_container = page.locator(".iwc-table-container")

            # 获取表格的 HTML 字符串
            table_html = await table_container.inner_html()

            # 使用 pandas.read_html 解析 HTML 表格
            # io.StringIO 将字符串伪装成文件，以便 pandas 读取
            current_df = pd.read_html(StringIO(table_html))[0]

            if not current_df.empty:
                # 手动设置列名
                current_df.columns = headers
                final_df = current_df.drop(columns=["check_box"])
                final_df = final_df.drop_duplicates()
                # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
                markdown_table = final_df.to_markdown(index=False)
                return markdown_table

        # 循环点击下一页直到无法点击为止
        while True:
            # 数据抓取逻辑
            # 定位整个表格容器，包含表头和数据
            await page.wait_for_selector(".iwc-table-container", state="visible")
            table_container = page.locator(".iwc-table-container")

            # 获取表格的 HTML 字符串
            table_html = await table_container.inner_html()

            # 使用 pandas.read_html 解析 HTML 表格
            # io.StringIO 将字符串伪装成文件，以便 pandas 读取
            current_df = pd.read_html(StringIO(table_html))[0]

            if not current_df.empty:
                # 手动设置列名
                current_df.columns = headers
                all_dfs.append(current_df)
            # 定位 '下一页' 的 a 标签，它是可点击的元素
            next_page_link = page.locator("a:has-text('下页')")

            # 使用 Playwright 的 is_enabled() 方法来判断链接是否可用
            # 这个方法会等待元素出现，并检查它是否可点击
            # 检查他的父标签是否可见
            parent_element = next_page_link.locator("xpath=..")

            class_value = await parent_element.get_attribute("class")
            is_disable = class_value == "disabled"

            if  is_disable:
                print("已到达最后一页，停止点击。")
                break  # 如果按钮不可用，则退出循环

            # 点击下一页按钮
            await next_page_link.click()
            # 等待页面加载完成
            await page.wait_for_load_state("domcontentloaded")

        # 将所有 DataFrame 合并成一个
        # print("len(all_dfs)============",len(all_dfs))
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            #删除check_box列
            final_df = final_df.drop(columns=["check_box"])
            #去重
            final_df = final_df.drop_duplicates()
            # 将“代码”列的数据类型转换为字符串
            final_df['股票代码'] = final_df['股票代码'].astype(str)
            # 使用 str.zfill() 方法补全前导零，例如，补到6位
            final_df['股票代码'] = final_df['股票代码'].str.zfill(6)
            # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table
        else:
            return "无法找到表格数据。"

    except Exception as ex:
        LOGGER.error(ex)
        return "数据获取失败"

    finally:
        if page:
            await page.close()
