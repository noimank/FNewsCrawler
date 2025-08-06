from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager


async def get_history_funds_flow(stock_code)-> str:
    """
    获取股票历史资金流信息
    :return: 历史资金流信息
    """
    url = f"https://stockpage.10jqka.com.cn/{stock_code}/funds/"

    context = await context_manager.get_context("iwencai")
    page = None
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # 提取表格的 HTML 字符串
        table_html = await page.locator("#history_table .m_table_3").inner_html()
        html_content = f"<table>{table_html}</table>"  # 添加完整的table标签
        # 使用 pandas.read_html 解析 HTML 表格
        # io.StringIO 将字符串伪装成文件，以便 pandas 读取
        current_df = pd.read_html(StringIO(html_content))[0]
        if not current_df.empty:
            # 手动设置列名
            current_df.columns = ["日期","收盘价", "涨跌幅", "资金净流入", "5日主力净额", "大单(主力)净额","大单(主力)净占比", "中单净额", "中单净占比", "小单净额", "小单净占比"]
            final_df = current_df.drop_duplicates()
            # 使用 pandas 的 to_markdown 方法转换为 Markdown 格式
            markdown_table = final_df.to_markdown(index=False)
            return markdown_table
        else:
            return "没有历史资金流信息"

    except Exception as e:
        return f"获取历史资金流信息失败: {e}"

    finally:
        if page:
            await page.close()






