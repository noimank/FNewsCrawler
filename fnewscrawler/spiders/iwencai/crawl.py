import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from fnewscrawler.core.context import context_manager
from fnewscrawler.utils.logger import LOGGER
import asyncio
from fnewscrawler.core.news_crawl import news_crawl_from_url


async def navigate_to_page(page, target_page: int):
    """
    翻页到指定页码
    
    Args:
        page: Playwright页面对象
        target_page: 目标页码
    """
    try:
        # 等待分页器加载
        await page.wait_for_selector(".paginate-wrapper", timeout=5000)
        
        await page.locator(f".pcwencai-pagination").locator(f"text={target_page}").click()
        await page.wait_for_load_state("domcontentloaded")
                
    except Exception as e:
        LOGGER.error(f"处理 {page.url} 翻页过程中发生错误: {e}")



async def extract_single_news(item) -> Optional[Dict[str, str]]:
    """
    提取单条新闻的信息
    
    Args:
        item: 新闻项的Locator对象
        
    Returns:
        Dict: 单条新闻信息
    """
    try:
        news_info = {
            'url': '',
            'title': '',
            'time': '',
            'source': ''
        }
        
        # 提取URL
        url_element = item.locator("a").first
        if await url_element.count() > 0:
            url = await url_element.get_attribute('href')
            if url:
                # 处理相对URL
                if url.startswith('//'):
                    url = 'https:' + url
                news_info['url'] = url

        # 提取标题
        title_element = item.locator(".baike-info a").first
        if await title_element.count() > 0:
            title = await title_element.inner_text()
            if title and title.strip():
                news_info['title'] = title.strip()
            
        
        # 提取时间
        time_element = item.locator("time").first
        time_str = await time_element.inner_text()
        if time_str:
            news_info['time'] = time_str.replace('发布时间：', '')

        # 提取来源
        source_element = item.locator(".source").first
        if await source_element.count() > 0:
            source_text = await source_element.inner_text()
            if source_text:
                news_info['source'] = source_text.strip().replace('来源：', '')

        
        # 如果没有找到时间，使用当前时间
        if not news_info['time']:
            news_info['time'] = "未知发布时间"
        
        # 验证必要字段
        if news_info['url'] and news_info['title']:
            return news_info
        else:
            return None
            
    except Exception as e:
        # LOGGER.error(f"提取单条新闻信息时发生错误: {e}")
        return None

async def extract_news_list(page) -> List[Dict[str, str]]:
    """
    从页面中提取新闻列表信息
    
    Args:
        page: Playwright页面对象
        
    Returns:
        List[Dict]: 新闻列表
    """
    try:
        # 等待新闻列表容器加载
        await page.wait_for_selector(".info-result-list", timeout=10000)
        
        items = await page.locator(".split-style.entry-4").all()
        # if items:
        #     LOGGER.info(f"找到新闻列表，共{len(items)}条")

        # 使用asyncio.gather并发提取新闻信息
        news_tasks = [extract_single_news(item) for item in items]
        news_results = await asyncio.gather(*news_tasks)
        
        # 过滤出有效的新闻信息
        news_list = [
            news for news in news_results 
            if isinstance(news, dict) and news.get('url')
        ]

        LOGGER.info(f"iwencai：成功提取{len(news_list)}条新闻")
        return news_list
        
    except Exception as e:
        LOGGER.error(f"iwencai：提取新闻列表时发生错误: {e}")
        return []

async def iwencai_crawl_from_query(query: str, pageno: int = 1) -> List[Dict[str, str]]:
    """
    爬取同花顺问财新闻列表
    
    Args:
        query: 查询关键词
        pageno: 页码，默认为1
        
    Returns:
        List[Dict]: 新闻列表，每个元素包含url、title、time、source等字段
    """
    context = await context_manager.get_context("iwencai")
    page = await context.new_page()
    base_url = "https://www.iwencai.com/unifiedwap/info/news"
    try:
        # 访问问财新闻页面
        await page.goto(base_url)
        await page.wait_for_load_state("domcontentloaded")
        
        # 点击搜索框并输入查询内容
        await page.locator(".input-base-box").click()
        await page.locator("#searchInput").click()
        await page.locator("#searchInput").fill(query)
        
        # 点击搜索按钮
        await page.locator("div").filter(has_text=re.compile(r"^加入动态板块收藏此问句$")).locator("i").first.click()
        await page.wait_for_load_state("domcontentloaded")
        
        
        # 如果不是第一页，需要翻页
        if pageno > 1:
            await navigate_to_page(page, pageno)
        
        # 提取新闻列表
        news_list = await extract_news_list(page)
        # 使用gather并发处理获取详细的新闻内容
        async def process_news_item(item):
            url = item["url"]
            real_url,new_content = await news_crawl_from_url(url, context_type="iwencai")
            item["content"] = new_content
            item["url"] = real_url
            return item

        # 并发执行所有新闻内容获取任务
        news_tasks = [process_news_item(item) for item in news_list]
        news_list = await asyncio.gather(*news_tasks)
        
        return news_list

    except Exception as e:
        LOGGER.error(f"iwencai：爬取 “{query}”第{pageno} 页过程中发生错误: {e}")
        return []
    finally:
        await page.close()

    

        
        

