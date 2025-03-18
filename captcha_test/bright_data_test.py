import asyncio
from playwright.async_api import async_playwright
from scraper_utils.utils.browser_util import abort_resources, ResourceType, BrowserManager


async def test_wss():
    print('程序启动...')
    async with async_playwright() as pwr:
        print('连接浏览器...')
        browser = await pwr.chromium.connect_over_cdp(
            'wss://brd-customer-hl_d4d0acc0-zone-scraping_browser1:jz0nrx7g7r6k@brd.superproxy.io:9222'
        )
        context = await browser.new_context()
        await abort_resources(
            context_page=context,
            res_types=(ResourceType.IMAGE, ResourceType.MEDIA),
        )
        page = await context.new_page()
        print('打开链接...')
        # response = await page.goto('https://geo.brdtest.com/welcome.txt')
        response = await page.goto('https://www.emag.ro')
        print('检查响应...')
        if response is not None:
            print((await response.body()).decode())
        print('截图...')
        await page.screenshot(path='temp/emagtest.png')
    print('程序结束')


async def test_datacenter():
    async with BrowserManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        channel='chrome',
        headless=False,
        args=['--start-maximized'],
    ) as bm:
        context = await bm.new_context(
            proxy={
                'server': 'servercountry-cn.brd.superproxy.io:33335',
                'username': 'brd-customer-hl_d4d0acc0-zone-datacenter_proxy1',
                'password': 'b9jcafic88vt',
            },
            need_stealth=True,
            abort_res_types=(ResourceType.IMAGE, ResourceType.MEDIA),
            default_navigation_timeout=120_000,
            default_timeout=120_000,
        )
        page = await context.new_page()
        # await page.goto('https://geo.brdtest.com/welcome.txt')
        await page.goto('https://www.emag.ro')  # WARNING 会弹验证码
        # NOTICE 刚好可以拿来做验证码测试
        input('Enter...')


async def test_residential():
    async with BrowserManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        channel='chrome',
        headless=False,
        args=['--start-maximized'],
    ) as bm:
        context = await bm.new_context(
            proxy={
                'server': 'servercountry-cn.brd.superproxy.io:33335',
                'username': 'brd-customer-hl_d4d0acc0-zone-residential_proxy2',
                'password': 'l34e79ydwj3b',
            },
            need_stealth=True,
            abort_res_types=(ResourceType.IMAGE, ResourceType.MEDIA),
            default_navigation_timeout=120_000,
            default_timeout=120_000,
        )
        page = await context.new_page()
        await page.goto('https://geo.brdtest.com/welcome.txt')
        # await page.goto('https://www.emag.ro')
        input('Enter...')


if __name__ == '__main__':
    # asyncio.run(test_wss())
    asyncio.run(test_datacenter())
