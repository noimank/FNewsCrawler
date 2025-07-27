import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from fnewscrawler.core.context import context_manager
from fnewscrawler.utils.logger import LOGGER


class IwencaiCrawler:
    def __init__(self, use_login: bool = True):
        self._base_url = "https://www.iwencai.com/unifiedwap/info/news"

    async def crawl(self, query: str, pageno: int = 1) -> List[Dict[str, str]]:
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
        news_list = []
        
        try:
            # 访问问财新闻页面
            await page.goto(self._base_url)
            await page.wait_for_load_state("networkidle")
            
            # 点击搜索框并输入查询内容
            await page.locator(".input-base-box").click()
            await page.locator("#searchInput").click()
            await page.locator("#searchInput").fill(query)
            
            # 点击搜索按钮
            await page.locator("div").filter(has_text=re.compile(r"^加入动态板块收藏此问句$")).locator("i").first.click()
            await page.wait_for_load_state("networkidle")
            
            
            # 如果不是第一页，需要翻页
            if pageno > 1:
                await self._navigate_to_page(page, pageno)
            
            # 提取新闻列表
            news_list = await self._extract_news_list(page)

        except Exception as e:
            LOGGER.error(f"爬取过程中发生错误: {e}")
            return []
        finally:
            await page.close()

        # 处理获取详细的新闻内容
        for new_item in news_list:
            url = new_item["url"]
            source = new_item["source"]
            new_content, real_url = await self._get_news_content(url, source)
            new_item["content"] = new_content
            new_item["url"] = real_url
            break
        
        return news_list


    
    async def _navigate_to_page(self, page, target_page: int):
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
            await page.wait_for_load_state("networkidle")
                    
        except Exception as e:
            print(f"翻页过程中发生错误: {e}")
    
    async def _extract_news_list(self, page) -> List[Dict[str, str]]:
        """
        从页面中提取新闻列表信息
        
        Args:
            page: Playwright页面对象
            
        Returns:
            List[Dict]: 新闻列表
        """
        news_list = []
        
        try:
            # 等待新闻列表容器加载
            await page.wait_for_selector(".info-result-list", timeout=10000)
            
           
            items = await page.locator(".split-style.entry-4").all()
            if items:
                LOGGER.info(f"找到新闻列表，共{len(items)}条")

            # 提取每条新闻的信息
            for i, item in enumerate(items):
                try:
                    news_info = await self._extract_single_news(item)
                    if news_info and news_info.get('url'):
                        news_list.append(news_info)
                except Exception as e:
                    LOGGER.error(f"提取第{i+1}条新闻时发生错误: {e}")
                    continue
            
            LOGGER.info(f"成功提取{len(news_list)}条新闻")
            return news_list
            
        except Exception as e:
            LOGGER.error(f"提取新闻列表时发生错误: {e}")
            return []
    
    async def _extract_single_news(self, item) -> Optional[Dict[str, str]]:
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
                'source': '',
                'summary': ''
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
            
            #提取摘要
            summary_element = item.locator(".baike-info p").first
            if await summary_element.count() > 0:
                summary = await summary_element.inner_text()
                if summary:
                    news_info['summary'] = summary.strip()

            
            # 如果没有找到时间，使用当前时间
            if not news_info['time']:
                news_info['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 验证必要字段
            if news_info['url'] and news_info['title']:
                return news_info
            else:
                return None
                
        except Exception as e:
            LOGGER.error(f"提取单条新闻信息时发生错误: {e}")
            return None
    
    async def _get_news_content(self, url: str, source: str) -> Tuple[str, str]:
        """
        根据URL获取新闻详细内容（预留接口）
        
        Args:
            url: 新闻详情页URL
            source: 新闻来源
            
        Returns:
            Tuple[str, str]: (新闻详细内容, 实际URL)
        """
        # 这里可以调用其他接口或工具来获取详细内容
        context = await context_manager.get_context("iwencai")
        page = await context.new_page()

        # 示例URL，实际应该使用传入的url参数
        test_url = "https://www.taihainet.com/news/finance/txlc/2025/2837574.html"

        try:
            await page.goto(test_url)
            await page.wait_for_load_state("networkidle")
            content = await page.locator(".article-content").inner_text()
            actual_url = page.url  # 获取实际访问的URL
            return content, actual_url
        except Exception as e:
            LOGGER.error(f"获取新闻详细内容时发生错误: {e}")
            return "", url
        finally:
            await page.close()


        
        

