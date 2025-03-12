import asyncio
from pathlib import Path

from scraper_utils.utils.browser_util import PersistentContextManager, ResourceType, MS1000

from emag_stock_monitor.page_handlers.cart_page import clear_cart, goto_cart_page


CWD = Path.cwd()


async def main():
    async with PersistentContextManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        user_data_dir=CWD.joinpath('chrome_data'),
        channel='chrome',
        headless=False,
        abort_res_types=(ResourceType.MEDIA, ResourceType.IMAGE),
        default_navigation_timeout=60 * MS1000,
        default_timeout=60 * MS1000,
    ) as pcm:
        page = await goto_cart_page(pcm.context, wait_until='networkidle')
        await clear_cart(page)


if __name__ == '__main__':
    asyncio.run(main())
