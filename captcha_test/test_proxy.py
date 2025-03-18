"""测试代理是否可用"""

import asyncio

from scraper_utils.utils.browser_util import BrowserManager


async def main():
    async with BrowserManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        channel='chrome',
        headless=False,
        args=[
            '--start-maximized',
            # r'--ssl-client-certificate-file=C:\Python\emag-stock-monitor\BrightData SSL certificate (port 33335).crt',
        ],
    ) as bm:
        context = await bm.new_context(
            proxy={
                'server': 'brd.superproxy.io:33335',
                'username': 'brd-customer-hl_d4d0acc0-zone-residential_proxy1',
                'password': 'vaalgbizhon8',
            },
            # need_stealth=True,
            default_navigation_timeout=120_000,
            default_timeout=120_000,
        )
        page = await context.new_page()

        try:
            response = await page.goto('https://geo.brdtest.com/welcome.txt?product=resi&method=native')
            if response is not None:
                print(await response.json())
        except Exception:
            pass

        input('Enter...')


if __name__ == '__main__':
    asyncio.run(main())
