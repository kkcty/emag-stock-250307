"""处理购物车页"""

from time import perf_counter
from typing import Literal, Optional

from playwright.async_api import BrowserContext, Page
from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.constants.time_constant import MS1000

from emag_stock_monitor.logger import logger
from emag_stock_monitor.models import CartProduct, CartProducts
from emag_stock_monitor.urls import CART_PAGE_URL
from emag_stock_monitor.utils.parse_util import parse_pnk


async def goto_cart_page(
    context: BrowserContext,
    wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = 'load',
    timeout: Optional[int] = None,
) -> Page:
    """打开购物车页面"""
    page = await context.new_page()
    await page.goto(CART_PAGE_URL, wait_until=wait_until, timeout=timeout)
    return page


async def wait_page_load(page: Page, timeout: float = 60) -> bool:
    """等待页面加载完成（检测页面是否有商品）"""
    logger.info('等待购物车页面加载...')
    vendors_item_div = page.locator('xpath=//div[@class="vendors-item fade in"]')  # BUG

    start_time = perf_counter()
    while True:
        try:
            await vendors_item_div.wait_for(timeout=MS1000)
        except PlaywrightError:
            if perf_counter() - start_time > timeout:
                logger.warning('购物车页面检测不到商品')
                return False
        else:
            logger.success('购物车页面检测到商品')
            return True


async def parse_stock(page: Page) -> CartProducts:
    """统计购物车页面的所有产品的库存（最大可加购数）"""

    ##### 单项商品 #####
    '//div[@class="main-product-title-container"]/a'  # 商品链接
    '//div[@class="main-product-title-container"]/ancestor::div[@class="line-item-details"]//input[@max]'  # 商品最大加购数

    ##### 捆绑商品 #####
    '//div[@class="line-item bundle-main d-flex "]//div[@class="bundle-item-title fw-semibold"]/a'  # 商品链接
    '//div[@class="line-item bundle-main d-flex "]/ancestor::div[@class="cart-widget cart-line"]//input[@max]'  # 商品最大加购数

    result = CartProducts()

    single_item_count = await page.locator('xpath=//div[@class="main-product-title-container"]/a').count()
    bundle_item_count = await page.locator(
        (
            'xpath=//div[@class="line-item bundle-main d-flex "]'
            '//div[@class="bundle-item-title fw-semibold"]/a'
        )
    ).count()
    logger.debug(f'找到 {single_item_count} 个单项商品，{bundle_item_count} 个捆绑商品')

    # 解析单项商品
    for i in range(single_item_count):
        i_url_a = page.locator(f'xpath=(//div[@class="main-product-title-container"]/a)[{i+1}]')
        i_qty_input = page.locator(
            (
                f'xpath=(//div[@class="main-product-title-container"]'
                f'/ancestor::div[@class="line-item-details"]//input[@max])[{i+1}]'
            )
        )
        i_pnk: str = parse_pnk(await i_url_a.get_attribute('href', timeout=MS1000))  # type: ignore
        i_qty: int = int(await i_qty_input.get_attribute('max', timeout=MS1000))  # type: ignore
        result.add(CartProduct(i_pnk, i_qty))

    # 解析捆绑商品
    for i in range(bundle_item_count):
        i_url_a = page.locator(
            (
                f'xpath=//div[@class="line-item bundle-main d-flex "]'
                f'//div[@class="bundle-item-title fw-semibold"]/a'
            )
        )
        i_qty_input = page.locator(
            (
                f'xpath=//div[@class="line-item bundle-main d-flex "]/ancestor::f'
                f'div[@class="cart-widget cart-line"]//input[@max]'
            )
        )
        i_pnk: str = parse_pnk(await i_url_a.get_attribute('href', timeout=MS1000))  # type: ignore
        i_qty: int = int(await i_qty_input.get_attribute('max', timeout=MS1000))  # type: ignore
        result.add(CartProduct(i_pnk, i_qty))

    return result


async def clear_cart(page: Page):
    """清空购物车"""
    # TODO
