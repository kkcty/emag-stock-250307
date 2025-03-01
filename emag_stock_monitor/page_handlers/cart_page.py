"""购物车页面"""

from playwright.async_api import BrowserContext, Page
from scraper_utils.constants.time_constant import MS1000
from scraper_utils.exceptions.browser_exception import PlaywrightError

from ..constants.regex import CART_RENDER_VENDORS_API
from ..constants.url import CART_PAGE_URL
from ..constants.xpath import CART_PAGE_STERGE_BUTTON_XPATH
from ..logger import logger


async def goto_cart_page(context: BrowserContext) -> Page:
    """打开该上下文对应的购物车页面,并且等待页面加载完毕"""
    logger.info(f'正在打开购物车页面 "{CART_PAGE_URL}"')
    page = await context.new_page()
    await page.goto(CART_PAGE_URL, wait_until='networkidle')
    return page


async def increment_item_quantity(page: Page):
    """在购物车界面，追加商品至上限"""
    raise NotImplementedError  # TODO


async def remove_item_from_cart(page: Page):
    """购物车页面：将商品移出购物车"""
    # BUG 时好时坏
    while True:
        try:
            await page.wait_for_timeout(MS1000)

            sterge_button = page.locator(CART_PAGE_STERGE_BUTTON_XPATH)
            sterge_button_count = await sterge_button.count()
            logger.debug(f'找到 {sterge_button_count} 个 sterge "{page.url}"')

            if sterge_button_count == 0:
                break

            async with page.expect_response(CART_RENDER_VENDORS_API) as response_info:
                await sterge_button.first.click(timeout=MS1000)
                logger.info(f'点击了 sterge "{page.url}"')
            response = await response_info.value
            if response.ok:
                logger.success(f'点击 sterge 成功 "{page.url}"')
            else:
                logger.error(f'点击 sterge 失败 "{page.url}"')

        except PlaywrightError as pe:
            logger.error(pe)
