"""处理购物车页"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Literal, Optional

from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.browser_util import wait_for_selector
from scraper_utils.constants.time_constant import MS1000

from emag_stock_monitor.exceptions import GotoCartPageError
from emag_stock_monitor.logger import logger
from emag_stock_monitor.urls import CART_PAGE_URL

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page

    from emag_stock_monitor.models import Product


# TODO 需要检测验证码
# /html/body[contains(@class,"captcha")]
# CF 验证会有很多形式，是搞模拟点击？还是当出现验证码时暂停程序并发出提醒？


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
        """
        1. 遍历所有的 //button[contains(@class,"remove-product")]
        2. 如果它可见就点击它
        3. 如果页面上已没有 //input[@max] 就停止
        """
        if await check_have_product(page, timeout=MS1000) is False:
            break
        if await sterge_button.nth(i).is_visible():
            try:
                await sterge_button.nth(i).click(timeout=MS1000)
            except PlaywrightError as pe:
                logger.warning(f'尝试 Sterge #{i} 时出错\n{pe}')
                pass
            else:
                logger.debug(f'Sterge #{i} 成功')

    logger.info('购物车已清空')


async def parse_qty(page: Page, products: list[Product]) -> list[Product]:
    """解析购物车页的产品数据"""
    logger.info('解析购物车的产品数据...')

    result: list[Product] = list()

    for i in products:
        """
        1. 从 products 中拿出一个产品
        2. 通过该产品的 pnk 找到该产品的最大可加购数
        3. 尝试将最大可加购数转成整数
        4. 设置该产品的最大可加购数
        """
        p = copy(i)
        qty_input = page.locator(
            f'xpath=(//a[contains(@href,"{p.pnk}")]/ancestor::div[starts-with(@class,"cart-widget cart-line")]//div[@data-phino="Qty"]/input[@max])[1]'
        )
        try:
            qty: str = await qty_input.get_attribute('max', timeout=MS1000)  # type: ignore
            p.qty = int(qty)
        except PlaywrightError as pe:
            logger.error(f'尝试获取 "{p.pnk}" rank={p.rank} 的最大可加购数时出错\n{pe}')
        except ValueError as ve:
            logger.error(f'尝试将 "{p.pnk}" rank={p.rank} 的最大可加购数解析成整数时出错\n{ve}')
        else:
            result.append(p)
            logger.debug(f'成功获取到 "{p.pnk}" rank={p.rank} 的最大可加购数 {p.qty}')

    return result


async def handle_cart(
    context: BrowserContext, products: list[Product], need_clear_cart: bool
) -> list[Product]:
    """处理购物车

    ---

    1. 打开购物车页
    2. 解析购物车页内产品
    3. 清空购物车
    """

    cart_page = await goto_cart_page(context, wait_until='networkidle')
    result = await parse_qty(cart_page, products)
    if need_clear_cart:
        await clear_cart(cart_page)
    await cart_page.close()
    return result
