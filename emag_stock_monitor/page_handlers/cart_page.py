"""购物车页面"""

from playwright.async_api import BrowserContext, Page
from scraper_utils.constants.time_constant import MS1000
from scraper_utils.exceptions.browser_exception import PlaywrightError

from ..logger import logger
from ..regexps import cart_page_api_routes
from ..urls import CART_PAGE_URL

# WARNING 未完成


async def goto_cart_page(context: BrowserContext) -> Page:
    """打开该上下文对应的购物车页面,并且等待页面加载完毕"""
    logger.info(f'正在打开购物车页面 "{CART_PAGE_URL}"')
    page = await context.new_page()
    await page.goto(CART_PAGE_URL, wait_until='networkidle')
    return page


async def increment_item_quantity(page: Page):
    """在购物车界面，追加商品至上限"""
    raise NotImplementedError  # TODO


async def clean_cart(page: Page):
    """清空购物车：把所有商品移出购物车"""
    logger.info('开始清理购物车')

    # BUG 产品标签 xpath 不对
    # TODO 捆绑销售的该怎么办？

    line_item_divs = page.locator('xpath=//div[@class="line-item-details"]')
    line_item_count = await line_item_divs.count()

    while line_item_count > 0:
        try:
            sterge_button = page.locator(
                (
                    f'xpath=(//div[@class="line-item-details"])[{line_item_count}]'
                    f'/div/div[@class="mb-1"]'
                    f'/button[contains(@class, "remove-product")]'
                )
            )
            preloader_div = page.locator(
                'xpath=//div[@class="cart-widget cart-line "]/div[@class="preloader"]'
            )

            # 等待 remove 这个请求成功
            async with page.expect_response(cart_page_api_routes['cart/remove']) as remove_response_event:
                await sterge_button.click()
                await preloader_div.wait_for(state='visible', timeout=1 * MS1000)
            remove_response = await remove_response_event.value
            if remove_response.ok:
                await preloader_div.wait_for(state='detached')
                await page.wait_for_timeout(MS1000)
                await preloader_div.wait_for(state='detached')
                line_item_count -= 1
                logger.success(f'清理购物车成功，剩余 {line_item_count}')
            else:
                continue

        except PlaywrightError as pe:
            logger.error(f'清理购物车时出错\n{pe}')

    logger.info('购物车清理结束')
