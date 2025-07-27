from fnewscrawler.spiders.iwencai import IwencaiLogin
import asyncio
from fnewscrawler.core.browser import browser_manager
from fnewscrawler.core.context import context_manager

async def get_qr_url():
    qr_url = await IwencaiLogin().get_qr_code()
    print(qr_url)

async def test_login():
    login_ma =  IwencaiLogin()
    qr_url = await login_ma.get_qr_code("ths")

    print(qr_url)
    await asyncio.sleep(20)

    is_login_success = await  login_ma.verify_login_success()
    if is_login_success:
        await login_ma.save_context_state()
        print("save context state")
    else:
        print("login fail")



async def test_login2():
    login_ma =  IwencaiLogin()
    qr_url = await login_ma.get_qr_code("qq")

    print(qr_url)
    await asyncio.sleep(2)

    is_login_success = await  login_ma.verify_login_success()
    if is_login_success:
        await login_ma.save_context_state()
        print("save context state")
    else:
        print("login fail")

    flag = await login_ma.close()
    if flag:
        print("login sucess")
    else:
        print("login fail")

async def ttt():

    bb = await browser_manager.get_browser()
    cc =  await context_manager.get_context("iwencxai")
    print(cc)
    await asyncio.sleep(2)









def test_run():

    # asyncio.run(get_qr_url())
    asyncio.run(test_login())
    # asyncio.run(test_login2())
    # asyncio.run(ttt())





if __name__ == '__main__':
    # test_run()
    obj1 = IwencaiLogin()
    obj2 = IwencaiLogin()
    print(id(obj1), id(obj2))


