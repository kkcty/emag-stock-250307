import asyncio
from pathlib import Path
from time import perf_counter

from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000
from scraper_utils.utils.file_util import read_file
from scraper_utils.utils.json_util import write_json

from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.list_page import add_to_cart, wait_page_load as wait_list_page_load
from emag_stock_monitor.utils.browser_util import block_emag_track

# TODO 需要提高健壮性
# TODO 怎么检测验证码？
# TODO 网络超时怎么办？

CWD = Path.cwd()

# 浏览器
user_data_dir = CWD.joinpath('chrome_data')
executable_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
abort_res_types = (ResourceType.IMAGE, ResourceType.FONT, ResourceType.MEDIA)

# 隐藏 cookie 提示
hide_cookie_banner_js = read_file(file=CWD.joinpath('js/hide-cookie-banner.js'), mode='str', async_mode=False)


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
        # args=['--window-size=1000,750'],
        args=['--start-maximized'],
    ) as bm:
        bc = await bm.new_context(
            abort_res_types=abort_res_types,
            need_stealth=True,
            default_timeout=60 * MS1000,
            default_navigation_timeout=60 * MS1000,
            add_init_script=hide_cookie_banner_js,
        )
        await block_emag_track(bc)

        list_page = await bc.new_page()
        # await list_page.goto('https://www.emag.ro/accesorii-fitness/c',wait_until='networkidle')
        # await list_page.goto('https://www.emag.ro/accesorii-fitness/p2/c',wait_until='networkidle')
        await list_page.goto('https://www.emag.ro/accesorii-fitness/p3/c', wait_until='networkidle')
        await wait_list_page_load(list_page)

        result = await add_to_cart(list_page)
        await write_json(
            file=CWD.joinpath('result.json'),
            data=list(_.as_dict() for _ in result),
            async_mode=True,
            indent=4,
        )

    ##########

    end_time = perf_counter()
    logger.info(f'程序结束，总用时 {round(end_time-start_time, 2)} 秒')


if __name__ == '__main__':
    asyncio.run(main())
