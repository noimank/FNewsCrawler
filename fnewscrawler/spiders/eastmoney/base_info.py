from io import StringIO

import pandas as pd

from fnewscrawler.core import context_manager
from fnewscrawler.core import get_redis


async def eastmoney_stock_base_info(stock_code: str)-> str | dict[str, str]:
    """
    获取股票基本信息，目前仅支持沪深股票
    :return: 股票基本信息
    """
    stock_code_prefix = None
    if stock_code.startswith("60"):
        stock_code_prefix = "sh"
    elif stock_code.startswith("00"):
        stock_code_prefix = "sz"
    elif stock_code.startswith("30"):
        stock_code_prefix = "sz"
    else:
        raise ValueError("股票代码格式错误")

    url = f"https://quote.eastmoney.com/{stock_code_prefix}{stock_code}.html"

    redis_client = get_redis()

    if redis_client.exists(url):
        return redis_client.get(url)


    context = await context_manager.get_context("eastmoney")
    page = None
    base_info = {
        #股票名称
        "stock_name": "",
        #所属行业名称
        "industry_name": "",
        #公司核心信息
        "company_core_info": "",
        #行业比较信息
        "company_compare_info": ""
    }
    try:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # 刷新页面是为了把弹窗去掉
        await page.reload()
        await page.wait_for_load_state("domcontentloaded")


        #股票名称
        stock_name = await page.locator("div.breadcrumb > span:nth-last-child(1)").inner_text()
        base_info["stock_name"] = stock_name

        #所属行业名称
        industry_name = await page.locator("div.breadcrumb > span:nth-last-child(2)").inner_text()
        base_info["industry_name"] = industry_name

        #公司核心信息
        company_core_info = await page.locator("div.quotecore").inner_text()
        base_info["company_core_info"] = company_core_info

        table_html = await page.locator(".finance4.afinance4").inner_html()
        table_content = pd.read_html(StringIO(table_html))[0]
        base_info["company_compare_info"] = table_content.to_markdown(index=False)
        #一天后过期
        redis_client.set(url, base_info, ex=24*60*60)

        return base_info


    except Exception as e:
        return f"获取股票基本信息失败: {e}"

    finally:
        if page:
            await page.close()