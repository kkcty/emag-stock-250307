"""产品列表页"""

import asyncio
from random import randint, uniform
from time import perf_counter

from playwright.async_api import Locator, Page
from scraper_utils.constants.time_constant import MS1000
from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.file_util import read_file
from ..constants.xpath import (
    LIST_PAGE_CARD_ITEM_WITHOUT_PROMOVAT_DIV_XPATH,
    LIST_PAGE_ADD_CART_BUTTON_XPATH,
    LIST_PAGE_ADD_CART_DIALOG_CLOSE_BUTTON_XPATH,
)
from ..logger import logger


async def wait_page_load(page: Page, expect_count: int = 60, timeout: float = 10):
    """等待页面加载完毕（等待出现足够数量的不带 Promovat 的 card-item）"""
    logger.debug(f'开始等待产品列表页加载完毕 "{page.url}"')
    start_time = perf_counter()
    while True:
        card_item_tags = page.locator(LIST_PAGE_CARD_ITEM_WITHOUT_PROMOVAT_DIV_XPATH)
        count = await card_item_tags.count()

        # 数量达标就退出
        if count >= expect_count:
            break

        # 模拟鼠标向下滚动
        await page.mouse.wheel(delta_x=0, delta_y=randint(500, 1000))
        await page.wait_for_timeout(uniform(0, 0.5) * MS1000)

        # 时间超时就退出
        if perf_counter() - start_time >= timeout:
            break
    logger.success(f'产品列表页加载完毕 "{page.url}"')
    return count


async def add_item_to_cart(page: Page, card_item_tag_count: int):
    """把页面内的所有产品加入到购物车（跳过 Promovat）"""
    # # TODO 要不改成每点击一次购物车就等待弹窗出现，等关闭弹窗了再点击下一个？
    # BUG 如果没弹出加购弹窗会在关闭加购弹窗处卡住
    # NOTICE 购物车一次只能放 50 个产品
    while card_item_tag_count > 0:
        try:
            await page.locator(
                f'xpath=//div[(@class="card-item card-standard js-product-data js-card-clickable " or '
                f'@class="card-item card-fashion js-product-data js-card-clickable") and @data-url!=""]'
                f'[not(.//span[@class="card-v2-badge-cmp badge bg-light bg-opacity-90 text-neutral-darkest"])'
                f' and .//form]'
                f'[{card_item_tag_count}]'
                f'//button[@class="btn btn-sm btn-emag btn-block yeahIWantThisProduct"]'
            ).click()
        except PlaywrightError as pe_1:
            logger.error(f'点击加购时出错\n{pe_1}')
            continue
        else:
            while True:
                try:
                    await page.locator(LIST_PAGE_ADD_CART_DIALOG_CLOSE_BUTTON_XPATH).click()
                except PlaywrightError as pe_2:
                    logger.error(f'点击关闭加购弹窗时出错\n{pe_2}')
                else:
                    break
            logger.debug(f'成功加购，剩余 {card_item_tag_count} 个')
            card_item_tag_count -= 1
