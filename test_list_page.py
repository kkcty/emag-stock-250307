import asyncio
import csv
from pathlib import Path

from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000
from scraper_utils.utils.file_util import read_file

from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.list_page import handle_list_page, wait_page_load


CWD = Path.cwd()


async def main():
    hide_cookie_banner_js = read_file(CWD.joinpath('js/hide-cookie-banner.js'), mode='str', async_mode=False)
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
        await page.add_init_script(hide_cookie_banner_js)

        # await page.goto('https://www.emag.ro/jocuri-societate/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p2/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p3/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p4/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p5/c')

        await page.goto('https://www.emag.ro/accesorii-fitness/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p2/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p3/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p4/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p5/c')

        # await page.goto('https://www.emag.ro/navomodele/c')
        await wait_page_load(page)
        result = await handle_list_page(page)

        # 保存成 csv 文件
        result_save_path = 'result.csv'
        with open(result_save_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['pnk', 'source_url', 'rank', 'qty'])
            writer.writeheader()
            for p in result:
                p_d = p.as_dict()
                p_d.pop('url', None)
                writer.writerow(p_d)

        logger.success(f'程序结束，爬取结果保存至 "{result_save_path}"')


if __name__ == '__main__':
    asyncio.run(main())
