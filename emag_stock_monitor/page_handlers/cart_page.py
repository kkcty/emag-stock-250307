"""处理购物车页"""

from typing import Literal, Optional

from playwright.async_api import BrowserContext, Page
from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.browser_util import wait_for_selector
from scraper_utils.constants.time_constant import MS1000

from emag_stock_monitor.exceptions import GotoCartPageError
from emag_stock_monitor.logger import logger
from emag_stock_monitor.urls import CART_PAGE_URL


async def goto_cart_page(
    context: BrowserContext,
    wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = 'load',
    retry_count: int = 3,
    timeout: Optional[int] = None,
) -> Page:
    """打开购物车页面"""
    # WARNING 为什么用 networkidle 打开购物车页时，产品加载出来后仍然要等待一段时间？
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


async def check_have_product(page: Page, timeout: int = 30 * MS1000) -> bool:
    """检测页面是否有商品"""
    logger.info('检测购物车内是否有产品...')
    return await wait_for_selector(page=page, selector='xpath=//input[@max]', timeout=timeout)


async def clear_cart(page: Page, retry_count: int = 3) -> None:
    """清空购物车"""
    # WARNING 尝试点击第一个 Sterge 时需要重试很多次才会成功
    # TODO 修改成检测页面是否 sterge 按钮，有则点击
    logger.info('清空购物车...')

    # TEMP
    # https://www.emag.ro/-/pd/D0QV44YBM/
    # https://www.emag.ro/-/pd/DZ2RFGMBM/
    # https://www.emag.ro/jocuri-societate/c
    # https://www.emag.ro/cart/products

    # BUG 为什么总是点击失败？为什么一打开浏览器控制台就能成功？

    # TODO 改成先统计 sterge 个数依次点击一遍，然后用下面的持续检测的方式清理可能失败的

    single_sterge_button = page.locator(
        (
            'xpath=//div[@class="main-product-title-container"]/ancestor::'
            # 'div[@class="line-item-details"]'
            'div[@class="cart-widget cart-line "]'
            '//button[contains(@class, "btn-remove-product")]'
        )
    )
    bundle_sterge_button = page.locator(
        (
            'xpath=//div[@class="line-item bundle-main d-flex "]/ancestor::'
            'div[@class="cart-widget cart-line"]'
            '//button[contains(@class, "btn-remove-product")]'
        )
    )

    single_sterge_button_count = await single_sterge_button.count()
    bundle_sterge_button_count = await bundle_sterge_button.count()

    for i in range(single_sterge_button_count, 0, -1):
        for j in range(retry_count):
            logger.debug(f'第 {j+1} 次尝试点击第 {i} 个单项 sterge 按钮')
            try:
                await single_sterge_button.nth(i).click(timeout=MS1000)
            except PlaywrightError:
                pass
            else:
                break
        else:
            logger.warning(f'尝试点击第 {i} 个单项 sterge 按钮失败')

    for i in range(bundle_sterge_button_count, 0, -1):
        for j in range(retry_count):
            logger.debug(f'第 {j+1} 次尝试点击第 {i} 个捆绑 sterge 按钮')
            try:
                await bundle_sterge_button.nth(i).click(timeout=MS1000)
            except PlaywrightError:
                pass
            else:
                break
        else:
            logger.warning(f'尝试点击第 {i} 个捆绑 sterge 按钮失败')

    # 持续检测页面上是否还有 sterge 按钮，有则点击
    while await have_sterge_button(page):
        try:
            await single_sterge_button.first.click(timeout=MS1000)
        except PlaywrightError:
            pass
        else:
            logger.debug(f'点击了一个单项商品 sterge')

        try:
            await bundle_sterge_button.first.click(timeout=MS1000)
        except PlaywrightError:
            pass
        else:
            logger.debug(f'点击了一个捆绑商品 sterge')

    logger.info('购物车已清空')


async def have_sterge_button(page: Page) -> bool:
    """检测页面上是否还有 sterge 按钮"""
    single_item_sterge_button = page.locator(
        (
            'xpath=//div[@class="main-product-title-container"]/ancestor::'
            'div[@class="line-item-details"]'
            '//button[contains(@class, "btn-remove-product")]'
        )
    )
    bundle_item_sterge_button = page.locator(
        (
            'xpath=//div[@class="line-item bundle-main d-flex "]/ancestor::'
            'div[@class="cart-widget cart-line"]'
            '//button[contains(@class, "btn-remove-product")]'
        )
    )
    return await single_item_sterge_button.count() > 0 or await bundle_item_sterge_button.count() > 0


# async def handle_cart(context: BrowserContext, added_products: Products) -> Products:
#     """处理购物车

#     ---

#     * 打开购物车页面
#     * 等待页面加载
#     * 解析购物车数据
#     * 清空购物车
#     """

#     page = await goto_cart_page(context, wait_until='networkidle')
#     if not await wait_page_load(page):
#         logger.error('等待购物车页面加载失败')
#         raise RuntimeError

#     result = await parse_cart(page)
#     await clear_cart(page)
#     await page.close()

#     return result
