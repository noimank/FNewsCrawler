import asyncio

from fnewscrawler.core.context import context_manager


page_global = None

async def crawl(url, context):
    page_global = await context.new_page()
    await page_global.goto(url)
    await asyncio.sleep(2)
    print("爬取{}成功".format(url))
    await page_global.close()
    page_global = None
    print("page_global={}".format(page_global))



async  def test_perf():
    context1 = await context_manager.get_context("iwencai")
    context2 = await context_manager.get_context("eastmoney")
    await crawl("https://www.baidu.com", context1)
    await asyncio.sleep(2)
    await crawl("https://www.baidu.com/s?wd=sdf&tn=15007414_23_dg&ie=utf-8", context1)
    # await crawl("https://www.zhihu.com", context2)
    await asyncio.sleep(2)



if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_perf())
    loop.close()

