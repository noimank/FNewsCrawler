import time

from fnewscrawler.spiders.iwencai import iwencai_concept_funds
import time
import asyncio



async def test_iwencai_concept_funds():
    markdown_table = await iwencai_concept_funds("1day")
    print(markdown_table)
    print("------------3day-------------------")
    markdown_table = await iwencai_concept_funds("3day")
    print(markdown_table)
    print("------------5day-------------------")
    markdown_table = await iwencai_concept_funds("5day")
    print(markdown_table)
    print("------------10day-------------------")
    markdown_table = await iwencai_concept_funds("10day")
    print(markdown_table)
    print("------------20day-------------------")
    markdown_table = await iwencai_concept_funds("20day")
    print(markdown_table)
    await asyncio.sleep(6)


if __name__ == '__main__':
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_iwencai_concept_funds())
    loop.close()
    print("测试完成")







