from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager


async def get_secu_margin_trading_info(stock_code, data_num=40)-> str:
    """
    获取股票融资融券信息
    :return: 融资融券信息
    """
    # url = f"https://data.10jqka.com.cn/market/rzrqgg/op/code/code/{stock_code}"

    #默认获取前两页的融资融券信息
    urls  = [f"https://data.10jqka.com.cn/ajax/rzrqgg/op/code/code/{stock_code}/",f"https://data.10jqka.com.cn/ajax/rzrqgg/op/code/code/{stock_code}/order/desc/page/2/" ]

    context = await context_manager.get_context("iwencai")
    page = None
    columns_name =  ["序号","交易时间", "融资余额(元)", "融资买入额(元)", "融资偿还额(元)", "融资净买入(元)", "融券余量(万股)", "融券卖出量(万股)", "融券偿还额(万股)", "融券净卖出(万股)", "融资融券余额(元)"]
    all_dfs = []
    try:
        page = await context.new_page()
        for url in urls:
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            # 提取表格的 HTML 字符串
            table_html = await page.locator(".m-table").inner_html()
            html_content = f"<table>{table_html}</table>"  # 添加完整的table标签
            # 使用 pandas.read_html 解析 HTML 表格
            # io.StringIO 将字符串伪装成文件，以便 pandas 读取
            current_df = pd.read_html(StringIO(html_content))[0]

            if not current_df.empty:
                # 手动设置列名
                current_df.columns = columns_name
                all_dfs.append(current_df)
            else:
                return "没有融资融券信息"


        if len(all_dfs) == 0:
            return "没有融资融券信息"
        else:
            # 手动设置列名
            final_df = pd.concat(all_dfs,axis=0)
            final_df = final_df.drop_duplicates()
            # 只返回data_num条数据
            data_num = min(data_num, 100)
            final_df = final_df.head(data_num)
            # 转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table


    except Exception as e:
        return f"获取融资融券信息失败: {e}"

    finally:
        if page:
            await page.close()






