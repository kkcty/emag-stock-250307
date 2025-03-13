import asyncio
from pathlib import Path

from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000
from scraper_utils.utils.json_util import write_json

from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.list_page import add_to_cart, wait_page_load


CWD = Path.cwd()


async def main():
    async with BrowserManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        channel='chrome',
        headless=False,
        args=['--start-maximized'],
    ) as bm:
        context = await bm.new_context(
            need_stealth=True,
            abort_res_types=(ResourceType.IMAGE, ResourceType.MEDIA),
            default_navigation_timeout=60 * MS1000,
            default_timeout=60 * MS1000,
        )
        page = await context.new_page()
        await page.goto('https://www.emag.ro/accesorii-fitness/c')
        await wait_page_load(page)
        result = await add_to_cart(page)
        # print(result)
        result_save_path = write_json(
            'result.json',
            data=list(_.as_dict() for _ in result),
            async_mode=False,
            indent=4,
        )
        logger.success(f'程序结束，爬取结果保存至 "{result_save_path}"')


if __name__ == '__main__':
    asyncio.run(main())
