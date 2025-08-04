from fnewscrawler.core import context_manager
from fnewscrawler.utils import LOGGER
async def base_news_list(base_url: str, page_no: int) -> list:
    """
    基础新闻列表页解析函数，统一处理财经要闻、宏观经济、产经新闻、国际财经、金融市场、公司新闻、区域经济、财经评论、财经人物的新闻列表
    :param base_url: 基础URL
    :param page_no: 页码
    :return: 新闻列表
    """
    context = await context_manager.get_context("iwencai")
    page = None
    try:
        page = await context.new_page()
        await page.goto(base_url)

        await page.locator(".list-con").wait_for(state="visible")

        news_list = await page.locator(".list-con li").all()
        #获取新闻标题和链接
        news_info = []
        for news in news_list:
            title_element = news.locator(".arc-title")
            title = await title_element.inner_text()
            
            link_element = news.locator(".arc-title a")
            link = await link_element.get_attribute("href")
            
            #获取最后一个a标签的文本
            summary_element = news.locator("a").nth(-1)
            summary = await summary_element.inner_text()
            
            time_element = news.locator(".arc-title span")
            time = await time_element.inner_text()
            
            news_info.append({
                "title": title,
                "url": link,
                "summary": summary,
                "time": time
            })

        return news_info

    except Exception as e:
        LOGGER.error(f"基础新闻列表页解析失败: {e}")
        return []
    finally:
        if page:
            await page.close()




async def financial_quick_news_info(page_no: int=1) -> dict:
    """
    财经要闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/today_list/"

    if page_no >1:
        base_url += f"index_{page_no}.shtml"


    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info



async def macro_economic_news_info(page_no: int=1) -> dict:
    """
    宏观经济新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/cjzx_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def product_economic_news_info(page_no: int=1) -> dict:
    """
    产经新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/cjkx_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def international_economic_news_info(page_no: int=1) -> dict:
    """
    国际财经新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/guojicj_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def financial_market_news_info(page_no: int=1) -> dict:
    """
    金融市场新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/jrsc_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def company_news_info(page_no: int=1) -> dict:
    """
    公司新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/fssgsxw_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def region_news_info(page_no: int=1) -> dict:
    """
    区域经济新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/region_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info


async def comment_news_info(page_no: int=1) -> dict:
    """
    财经评论新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/fortune_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info

async def financial_people_news_info(page_no: int=1) -> dict:
    """
    财经人物新闻列表页解析函数
    :param page_no: 页码
    :return: 新闻列表信息
    """
    base_url = "https://news.10jqka.com.cn/cjrw_list/"

    if page_no > 1:
        base_url += f"index_{page_no}.shtml"

    news_data_list = await base_news_list(base_url, page_no)

    news_list_info = {
        "news_list": news_data_list,
        "page_no": page_no,
        "total_page": 20,
        "news_count": len(news_data_list),
        "current_page": page_no,
    }

    return news_list_info



