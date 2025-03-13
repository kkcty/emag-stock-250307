"""处理购物车页"""

from typing import Literal, Optional

from playwright.async_api import BrowserContext, Page
from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.browser_util import wait_for_selector
from scraper_utils.constants.time_constant import MS1000

from emag_stock_monitor.exceptions import GotoCartPageError
from emag_stock_monitor.logger import logger
from emag_stock_monitor.models import Products, ListPageProduct
from emag_stock_monitor.urls import CART_PAGE_URL

# TODO 需要判断验证码

# NOTICE 可以通过 /products 中的 max_quantity 字段来解析 qty


async def goto_cart_page(
    context: BrowserContext,
    wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = 'load',
    retry_count: int = 3,
    timeout: Optional[int] = None,
) -> Page:
    """打开购物车页面"""
    logger.info(f'打开购物车页...')

    page = await context.new_page()
    for i in range(retry_count):
        logger.debug(f'尝试打开购物车页 {i+1}/{retry_count}')
        try:
            await page.goto(CART_PAGE_URL, wait_until=wait_until, timeout=timeout)
        except PlaywrightError as pe:
            logger.error(f'尝试打开购物车页时出错\n{pe}')
            continue
        else:
            break
    else:
        logger.error(f'尝试 {retry_count} 次后仍无法打开购物车页')
        raise GotoCartPageError

    if await check_have_product(page):
        logger.debug('购物车页检测到产品')
    else:
        logger.warning('购物车页检测不到产品')

    return page


async def check_have_product(
    page: Page,
    timeout: int = 30 * MS1000,
) -> bool:
    """检测页面是否有商品"""
    # logger.info('检测购物车内是否有产品...')
    return await wait_for_selector(page=page, selector='xpath=//input[@max]', timeout=timeout)


async def clear_cart(page: Page, retry_count: int = 3) -> None:
    """清空购物车"""
    logger.info('清空购物车...')

    # 倒序遍历所有 sterge 按钮，如果是 visible 的就点击它
    sterge_button = page.locator('xpath=//button[contains(@class,"remove-product")]')
    for i in range(await sterge_button.count(), 0, -1):
        if await check_have_product(page, timeout=MS1000) is False:
            break
        if await sterge_button.nth(i).is_visible():
            try:
                await sterge_button.nth(i).click(timeout=MS1000)
            except PlaywrightError as pe:
                logger.warning(f'尝试 Sterge #{i} 时出错\n{pe}')
            else:
                logger.debug(f'Sterge #{i}')

    logger.info('购物车已清空')


async def parse_qty(page: Page, products: Products) -> Products:
    """解析购物车页的产品数据"""
    logger.info('解析购物车的产品数据...')

    # BUG 结果的 qty 都是 None

    # //a[contains(@href,"DV1ZCFYBM")]/ancestor::div[@class="cart-widget cart-line "]//div[@data-phino="Qty"]/input[@max]
    # //a[contains(@href,"DZ2RFGMBM")]/ancestor::div[starts-with(@class,"cart-widget cart-line")]//div[@data-phino="Qty"]/input[@max]

    # 根据 pnk 解析 qty 用的 xpath
    # f'xpath=(//a[contains(@href,"{pnk}")]/ancestor::div[starts-with(@class,"cart-widget cart-line")]//div[@data-phino="Qty"]/input[@max])[1]'

    for p in products:
        qty_input = page.locator(
            f'xpath=(//a[contains(@href,"{p._pnk}")]/ancestor::div[starts-with(@class,"cart-widget cart-line")]//div[@data-phino="Qty"]/input[@max])[1]'
        )
        try:
            qty: str = await qty_input.get_attribute('max', timeout=MS1000)  # type: ignore
            p.qty = int(qty)
        except PlaywrightError as pe:
            logger.error(f'尝试获取 "{p._pnk}" 的 qty 时出错\n{pe}')
        except ValueError as ve:
            logger.error(f'尝试将 input[@max] 解析成整数时出错\n{ve}')
        else:
            logger.debug(f'获取到 "{p._pnk}" 的 qty={p.qty}')
    return products


async def handle_cart(context: BrowserContext, products: Products) -> Products:
    """处理购物车

    ---

    * 打开购物车页面
    * 等待页面加载
    * 解析购物车数据
    * 清空购物车
    """

    page = await goto_cart_page(context, wait_until='networkidle')
    result = await parse_qty(page, products)
    await clear_cart(page)
    await page.close()

    return result
