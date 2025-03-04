import asyncio
from pathlib import Path
from time import perf_counter

from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000

from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.cart_page import goto_cart_page, wait_page_load as wait_cart_page_load
from emag_stock_monitor.page_handlers.list_page import add_to_cart, wait_page_load as wait_list_page_load
from emag_stock_monitor.utils.browser_util import block_emag_track

# TODO 怎么检测验证码？

CWD = Path.cwd()
user_data_dir = CWD.joinpath('chrome_data')
executable_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
abort_res_types = (ResourceType.IMAGE, ResourceType.FONT, ResourceType.MEDIA)


async def main():
    """"""
    logger.info('程序启动')
    start_time = perf_counter()

    ##########

    async with BrowserManager(
        executable_path=executable_path,
        channel='chrome',
        headless=False,
        slow_mo=1 * MS1000,
        args=['--window-size=1000,750'],
    ) as bm:
        bc = await bm.new_context(
            abort_res_types=abort_res_types,
            need_stealth=True,
            default_timeout=60 * MS1000,
            default_navigation_timeout=60 * MS1000,
        )
        await block_emag_track(bc)

        # TODO

        input('打开产品列表页...')
        list_page = await bc.new_page()
        await list_page.goto('https://www.emag.ro/masinute/c')
        await wait_list_page_load(list_page)

        # TEMP
        # BUG 为什么是空的？
        for i in await add_to_cart(list_page):
            print(i.url, i.qty)

        input('打开购物车页...')
        cart_page = await goto_cart_page(bc)
        await wait_cart_page_load(cart_page)

        input('结束程序...')

    ##########

    end_time = perf_counter()
    logger.info(f'程序结束，总用时 {round(end_time-start_time, 2)} 秒')


if __name__ == '__main__':
    asyncio.run(main())
