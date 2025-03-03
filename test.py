import asyncio
from pathlib import Path

from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.browser_util import PersistentContextManager, ResourceType, MS1000

from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.cart_page import clean_cart
from emag_stock_monitor.page_handlers.common import block_emag_track
from emag_stock_monitor.regexps import cart_page_api_routes
from emag_stock_monitor.urls import CART_PAGE_URL


cwd = Path.cwd()


async def main():
    async with PersistentContextManager(
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        cwd.joinpath('chrome_data'),
        'chrome',
        headless=False,
        default_timeout=60 * MS1000,
        default_navigation_timeout=60 * MS1000,
        need_stealth=True,
        abort_res_types=(ResourceType.IMAGE, ResourceType.MEDIA, ResourceType.FONT),
    ) as pcm:
        await block_emag_track(pcm.context)

        page = await pcm.new_page()
        await page.goto(CART_PAGE_URL)

        input('Enter 清理购物车...')

        ##########

        await clean_cart(page)

        ##########

        input('Enter 结束程序...')


if __name__ == '__main__':
    asyncio.run(main())
