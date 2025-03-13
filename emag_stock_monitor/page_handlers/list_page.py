"""处理产品列表页"""

from asyncio.locks import Lock
from asyncio.tasks import create_task
from random import randint
from time import perf_counter
from typing import Optional

from playwright.async_api import Page
from scraper_utils.constants.time_constant import MS1000
from scraper_utils.exceptions.browser_exception import PlaywrightError
from scraper_utils.utils.emag_util import parse_pnk, validate_pnk

from emag_stock_monitor.logger import logger
from emag_stock_monitor.models import ListPageProduct, Products
from emag_stock_monitor.page_handlers.cart_page import handle_cart


async def wait_page_load(page: Page, expect_count: int = 60, timeout: float = 10) -> bool:
    """等待页面加载完成（等待加载出足够数量的产品卡片）"""
    logger.info(f'等待页面 "{page.url}" 加载...')
    start_time = perf_counter()

    while True:
        # 时间超时就退出
        if perf_counter() - start_time > timeout:
            logger.warning(f'等待页面 "{page.url}" 加载超时')
            return False

        # 统计产品卡片数量
        card_item_without_promovat_divs = page.locator(
            (
                'xpath='
                '//div[starts-with(@class, "card-item")]'
                '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
            ),
        )
        # BUG Promovat 标签需要等待网络加载完毕才会出现
        card_item_without_promovat_div_count = await card_item_without_promovat_divs.count()
        logger.debug(f'找到 {card_item_without_promovat_div_count} 个 card_item_without_promovat_div')

        # 数量达标就退出
        if card_item_without_promovat_div_count >= expect_count:
            logger.debug(
                f'等待页面 "{page.url}" 加载成功，检测到 {card_item_without_promovat_div_count} 个商品'
            )
            return True

        # 模拟鼠标滑动
        await page.mouse.wheel(delta_x=0, delta_y=randint(200, 1000))
        await page.wait_for_timeout(randint(0, 500))


# 点击加购按钮与点击加购弹窗关闭按钮的锁
_add_cart_lock = Lock()


async def add_to_cart(page: Page) -> Products:
    """加购页面上的产品"""
    # WARNING 购物车一次最多放 50 种产品
    # TODO 要不要主动检测购物车种类加购上限？

    # 整页的产品
    total_result = Products()

    # 启动检测加购弹窗作为后台任务
    check_cart_dialog_task = create_task(check_cart_dialog(page))

    # 去除 Promovat、有加购按钮的 card-item
    add_cart_able_card_item_without_promovat_divs = page.locator(
        '//div[starts-with(@class, "card-item")]'
        '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])'
        ' and .//form/button]'
    )
    # 产品 pnk 列表
    pnks: list[str] = [
        parse_pnk(await div.get_attribute('data-url', timeout=MS1000))  # type: ignore
        for div in await add_cart_able_card_item_without_promovat_divs.all()
    ]
    logger.debug(f'找到 {len(pnks)} 个 data-url，解析出如下 pnk\n["{'", "'.join(pnks)}"]')

    # 去除 Promovat 的加购按钮
    add_cart_buttons = page.locator(
        (
            'xpath='
            '//div[starts-with(@class, "card-item")]'
            '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
            '//form/button'
        ),
    )
    # 统计页面上的加购按钮总数
    add_cart_button_count = await add_cart_buttons.count()
    logger.debug(f'找到 {add_cart_button_count} 个符合条件的加购按钮')

    if add_cart_button_count != len(pnks):
        logger.error(f'解析到的 pnk 总数 {len(pnks)} 与加购按钮总数 {add_cart_button_count} 不同')

    for i, pnk in enumerate(pnks, start=1):
        total_result.append(ListPageProduct(pnk=pnk, source_url=page.url, rank=i))

    # 当前加进购物车的产品
    added_products = Products()

    added_count = 1
    while added_count < add_cart_button_count:
        # 加购达到一定数量（40）就打开购物车页面，统计已加购的产品，然后清空购物车
        if added_count % 40 == 0:
            total_result += await handle_cart(page.context, added_products)
            added_products = Products()

        async with _add_cart_lock:
            ##### 点击加购按钮，等待弹窗出现，点击关闭弹窗 #####
            try:
                add_cart_button = page.locator(
                    'xpath='
                    '(//div[starts-with(@class, "card-item")]'
                    '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
                    f'//form/button)[{added_count}]'
                )
                # 点击加购按钮
                await add_cart_button.click(timeout=5 * MS1000)

            # 如果点击加购失败了就重试
            except PlaywrightError as pe_add_cart:
                # logger.warning(f'尝试点击加购按钮失败\n{pe_add_cart}')
                continue

            # 点击加购成功
            else:
                # WARNING 要是解析 data-pnk 时得到的是 None 该怎么办？
                try:
                    pnk = await add_cart_button.get_attribute('data-pnk', timeout=0.1 * MS1000)
                except PlaywrightError:
                    pass
                else:
                    added_count += 1
                    logger.debug(f'加购 "{pnk}" 成功，当前加购至 {added_count}/{add_cart_button_count}')
                    if pnk is None or not validate_pnk(pnk=pnk):
                        logger.error(f'"{pnk}" 不符合 pnk 规则')
                        continue
                    added_products.append(ListPageProduct(pnk, page.url, added_count))

    # 当整个页面的加购完成就打开购物车页面，统计已加购产品
    total_result += await handle_cart(page.context, added_products)

    await page.close()
    await check_cart_dialog_task

    return total_result


async def check_cart_dialog(page: Page, interval: int = 1000):
    """每间隔 `interval` 毫秒检测一次页面有无加购弹窗，有则点击关闭"""
    while True:
        if page.is_closed():
            logger.debug('页面关闭，监测加购弹窗任务即将停止')
            break
        dialog_close_button = page.locator('xpath=//button[@class="close gtm_6046yfqs"]')
        async with _add_cart_lock:
            try:
                # logger.debug('正在寻找并尝试关闭加购弹窗')
                await dialog_close_button.click(timeout=interval)
            except PlaywrightError:
                pass
            # else:
            #     logger.debug('关闭了一个加购弹窗')


async def have_next_page(page: Page) -> bool:
    """当前页面是否有下一页（针对类目页）"""
    # TODO
