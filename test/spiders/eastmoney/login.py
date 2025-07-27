from fnewscrawler.spiders.eastmoney import EastMoneyLogin
import asyncio
from fnewscrawler.core.browser import browser_manager
from fnewscrawler.core.context import context_manager

async def get_qr_url():
    qr_url = await EastMoneyLogin().get_qr_code("微信")
    print(qr_url)

async def test_login():
    login_ma =  EastMoneyLogin()
    qr_url = await login_ma.get_qr_code("微信")

    print(qr_url)
    await asyncio.sleep(20)

    is_login_success = await  login_ma.verify_login_success()
    if is_login_success:
        await login_ma.save_context_state()
        print("save context state")
    else:
        print("login fail")

async def test_login2():
    login_ma =  EastMoneyLogin()

    is_login_success = await  login_ma.get_login_status()
    if is_login_success:
        # await login_ma.save_context_state()
        print("已经登录")
    else:
        print("未登录")




def test_run():

    # asyncio.run(get_qr_url())
    # asyncio.run(test_login())
    asyncio.run(test_login2())
    # asyncio.run(ttt())





if __name__ == '__main__':
    test_run()



