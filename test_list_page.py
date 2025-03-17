import asyncio
import csv
from pathlib import Path
import re

from playwright.async_api import Response
from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000
from scraper_utils.utils.file_util import read_file

from emag_stock_monitor.browser_util import block_emag_track
from emag_stock_monitor.exceptions import CaptchaError
from emag_stock_monitor.logger import logger
from emag_stock_monitor.page_handlers.list_page import handle_list_page, wait_page_load


# TODO 验证码: 响应状态码 511


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
        context.on('response', check_captcha_test)
        await block_emag_track(context)
        page = await context.new_page()
        await page.add_init_script(hide_cookie_banner_js)

        # input('Enter...')

        await page.goto('https://www.emag.ro/jocuri-societate/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p2/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p3/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p4/c')
        # await page.goto('https://www.emag.ro/jocuri-societate/p5/c')

        # await page.goto('https://www.emag.ro/accesorii-fitness/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p2/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p3/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p4/c')
        # await page.goto('https://www.emag.ro/accesorii-fitness/p5/c')

        # input('Enter...')
        # return  # TEMP

        # await page.goto('https://www.emag.ro/aparate-masaj/c')
        # await page.goto('https://www.emag.ro/aparate-masaj/p2/c')
        # await page.goto('https://www.emag.ro/aparate-masaj/p3/c')
        # await page.goto('https://www.emag.ro/aparate-masaj/p4/c')
        # await page.goto('https://www.emag.ro/aparate-masaj/p5/c')

        # await page.goto('https://www.emag.ro/navomodele/c')
        await wait_page_load(page)
        result = await handle_list_page(page)

        # 保存成 csv 文件
        result_save_path = 'result.csv'
        with open(result_save_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=['pnk', 'source_url', 'rank', 'top_favorite', 'review_count', 'qty'],
            )
            writer.writeheader()
            for p in result:
                p_d = p.as_dict()
                p_d.pop('url', None)
                writer.writerow(p_d)

        logger.success(f'程序结束，爬取结果保存至 "{result_save_path}"')


async def check_captcha_test(response: Response) -> None:
    """检测验证码（测试）"""
    """
    www.emag.ro 511
    challenges.cloudflare.com 401
    """
    # WARNING 明明已经屏蔽 by-zone-position 为什么在浏览器控制台还能看到它的 204，不过响应拦截器中确实没有 by-zone-position
    # TODO 目前只解决了打开链接时的验证码，怎么处理点击按钮等发起的请求是否触发验证码呢？
    url = response.url
    status = response.status
    if any(
        (
            # NOTICE 单单这些判断就够了吗？
            re.search(r'.*?www.emag.ro.*', url) is not None and status == 511,
            re.search(r'.*?challenges.cloudflare.com.*', url) is not None and status == 401,
        )
    ):
        logger.error(f'"{url}" 检测到验证码 status={status}')
        raise CaptchaError(url, status, '')
    else:
        logger.debug(f'"{url}" 未检测到验证码 status={status}')


if __name__ == '__main__':
    asyncio.run(main())
