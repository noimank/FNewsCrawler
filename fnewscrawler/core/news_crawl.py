import asyncio

from playwright.async_api import TimeoutError

from fnewscrawler.core.context import context_manager
from fnewscrawler.core.redis_manager import get_cached_news_content, cache_news_content
from fnewscrawler.utils import extract_second_level_domain, LOGGER

# 采用二级域名来映射选择器，选择器都是 CSS 或 ID 类型，不要填写其他选择器，否则没有提速加成
news_selector_map = {
    # 台海网
    "taihainet": ".article-content",
    # 同花顺
    "10jqka": [
        # 同花顺财经
        "#contentApp",
        # 同顺号
        ".post-detail-text"
    ],
    # 新浪网
    "sina": [
        ".article",
        "#content"
    ],
    # 微信公众号
    "qq": "#js_content",
    "weixin": "#js_content",
    #搜狐
    "sohu": ".article",
    #IT门户
    "donews": [".general-article"
               "#content"],
    #36氪
    "36kr":[".articleDetailContent", ".content"],
    #中国能源网
    "china5e": ".showcontent",
    #第一机械工程
    "d1cm":".wzCon",
    # 证券之星
    "stockstar": ".jour_text",
    #和讯网
    "hexun": ".art_contextBox",
    "163": ".post_body",
    #电子发烧友
    "elecfans": [
        ".simditor-body.clearfix",
        ".simditor-body",
        ".clearfix"
    ],
    #金融界
    "jrj": ".article_content",
    #金投网
    "cngold": ".article_con",
    # 东方财富
    "eastmoney": [
        ".txtinfos",
        "#ContentBody"
    ],
    # 上海证券报
    "cnstock":".content_article",
    #中国证券报
    "cs": "founder-content",
    #中财网
    "cfi": "#tdcontent",
    #钛媒体
    "tmtpost": "article",
    #速途网
    "sootoo": ".entry-content",
    #新华网
    "news": "#detailContent",
    #上海新闻网
    "casas-pkucis": ".article_content",
    #东南网
    "fjsen": "#new_message_id",
    #云南网
    "yunnan": "#layer216",
    #人民网
    "people": ".rm_txt_con.cf",
    #张家口新闻网
    "zjknews": ".i_left_body",
    #盖世汽车
    "gasgoo": ".ant-spin-container",
    #中华网
    "china": ["#artiCon", ".artiCon.re_cut"],
    #凤凰网
    "ifeng": ".index_articleBox_6mBbT",
    "futunn": [
        ".inner.origin_content.zh-cn",
        ".origin_content"
    ],
    #商洛之窗
    "slrbs": ".content",
    #每日经济网
    "mrjjxw": ".m-articleContent",
    #cctv
    "cctv": ".content_area",
    #中国经济网
    "ce": ["#ozoom.content", "founder-content"],
    #广州日报
    "dayoo": ".info",
    #四川
    "thecover":".article-content"

}



async def get_real_url(page, initial_url):
        # 尝试等待 URL 变化
        try:
            # 等待 URL 发生变化，设置一个较短的超时时间，例如 5 秒
            await page.wait_for_url(lambda url: url != initial_url, timeout=1500)
            # print("检测到 URL 跳转。")
        except TimeoutError:
            # 如果超时，说明 URL 没有变化，这是预期的行为
            # print("URL 没有跳转。")
            pass

        # 无论是否发生跳转，都可以安全地获取最终 URL
        final_url = page.url
        # print(f"最终 URL 是: {final_url}")

        return final_url


async def news_crawl_from_url(url: str, context_type: str = "common") -> tuple:
    """从指定URL爬取新闻内容。

       该函数会首先检查缓存中是否存在对应URL的新闻内容。如果存在则直接返回缓存内容，
       否则会使用浏览器访问URL并提取新闻内容。对于不同网站，使用预定义的CSS选择器
       来定位新闻正文。如果选择器无法获取内容，则返回整个页面内容。最后将获取的内容
       缓存以供后续使用。

       Args:
           url: 需要爬取的新闻URL。
           context_type: 浏览器上下文类型，默认为"common"。

       Returns:
           tuple: 包含新闻URL和新闻内容的元组。如果新闻内容为空，则返回空字符串。
           新闻URL是指实际访问的URL，可能与输入的URL不同，比如带了跳转链接的URL。

   """
    page = None
    try:
        # 在浏览器没进行实际跳转操作时就查询有没有缓存，避免浪费浏览器资源
        news_content = get_cached_news_content(url)
        if news_content:
            return url, news_content

        context = await context_manager.get_context(context_type)
        # 可以考虑在这里设置一个全局的默认超时，比如 10 秒
        # context.set_default_timeout(10000)
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded")
        await page.reload()

        # 获取当前url (可能因为跳转而改变)
        current_url = await get_real_url(page, url)
        # print("current url:" , current_url)
        # 再次尝试获取缓存内容，主要是针对url是带有跳转的情况
        news_content = get_cached_news_content(current_url)
        if news_content:
            return current_url, news_content

        # 获取二级域名
        second_level_domain = extract_second_level_domain(current_url)

        # 获取新闻选择器
        news_selector = news_selector_map.get(second_level_domain, None)
        # 用一个更明确的变量名
        fail_to_get_specific_content = False

        # 尝试提取指定选择器下的新闻内容
        if isinstance(news_selector, str):
            try:
                # 默认会等待元素出现并可见，可以根据需要设置更短的 timeout
                news_content = await page.locator(news_selector).inner_text(timeout=3000)  # 5秒超时
            except TimeoutError:  # 捕获特定的超时错误
                fail_to_get_specific_content = True
            except Exception as e:  # 捕获其他可能的错误
                fail_to_get_specific_content = True
        elif isinstance(news_selector, list):
            try:
                # 组合选择器，一次查询
                combined_selector = ",".join(news_selector)
                news_content = await page.locator(combined_selector).inner_text(timeout=3000)  # 5秒超时
            except TimeoutError:  # 捕获特定的超时错误
                fail_to_get_specific_content = True
            except Exception as e:  # 捕获其他可能的错误
                fail_to_get_specific_content = True
        else:  # 如果没有定义选择器
            fail_to_get_specific_content = True

        # 如果通过特定选择器未能获取内容，则获取整个页面的文本内容
        if fail_to_get_specific_content:
            news_content = await page.locator("body").inner_text()  # 这个也会有默认超时

        # 将html内容缓存，如果url不同就缓存两份，主要是假设能尽快的获取到跳转后的内容
        if url != current_url:
            cache_news_content(url, news_content)
        cache_news_content(current_url, news_content)

        return current_url, news_content
    except Exception as e:
        LOGGER.error(f"从URL {url} 爬取新闻内容时发生错误: {e}")
        return url, ""
    finally:
        if page:
            await page.close()