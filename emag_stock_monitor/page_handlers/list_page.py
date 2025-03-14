"""处理产品列表页"""

from asyncio.locks import Lock
from asyncio.tasks import create_task
from random import randint
from time import perf_counter

from playwright.async_api import Page
from scraper_utils.constants.time_constant import MS1000
from scraper_utils.exceptions.browser_exception import PlaywrightError

from emag_stock_monitor.logger import logger
from emag_stock_monitor.models import Product
from emag_stock_monitor.page_handlers.cart_page import handle_cart

# TODO 需要检测验证码
# /html/body[contains(@class,"captcha")]

# TODO 每个类目爬 5 页


async def wait_page_load(page: Page, expect_count: int = 60, timeout: float = 10) -> bool:
    """等待页面加载完成（等待加载出足够数量的产品卡片）"""
    logger.info(f'等待页面 "{page.url}" 加载...')
    start_time = perf_counter()

    while True:
        # 统计产品卡片数量
        card_item_without_promovat_divs = page.locator(
            (
                'xpath='
                '//div[starts-with(@class, "card-item")]'
                '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
            ),
        )
        card_item_without_promovat_div_count = await card_item_without_promovat_divs.count()
        # logger.debug(f'找到 {card_item_without_promovat_div_count} 个 card_item_without_promovat_div')

        # 数量达标就退出
        if card_item_without_promovat_div_count >= expect_count:
            logger.debug(
                f'等待页面 "{page.url}" 加载成功，检测到 {card_item_without_promovat_div_count} 个产品'
            )
            return True

        # 时间超时就退出
        if perf_counter() - start_time > timeout:
            logger.warning(
                f'等待页面 "{page.url}" 加载失败，检测到 {card_item_without_promovat_divs} 个产品，期望 {expect_count}'
            )
            return False

        # 模拟鼠标滑动
        await page.mouse.wheel(delta_x=0, delta_y=randint(200, 1000))
        await page.wait_for_timeout(randint(0, 500))


# 点击加购按钮与点击加购弹窗关闭按钮的锁
_add_cart_lock = Lock()


async def handle_cart_dialog(page: Page, interval: int = MS1000) -> None:
    """每间隔 `interval` 毫秒检测一次页面有无加购弹窗，有则点击关闭"""
    logger.info('启动检测加购弹窗任务...')
    while True:
        if page.is_closed():
            logger.info('检测到页面关闭，检测加购弹窗任务即将关闭...')
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
    logger.info('检测加购弹窗任务已关闭')


async def handle_list_page(page: Page) -> list[Product]:
    """
    处理产品列表页

    ---

    1. 统计页面上非 Promovat、非 Vezi Detalii 的加购按钮总数
    2. 启动处理加购弹窗的任务
    3. 判断加购按钮总数
        1. 如果小于等于 40，遍历点击所有加购按钮，每次加购时将已加购产品的 pnk、source_url、rank 放到 added_products 中，
        然后统计最大可加购数
        2. 如果超过 40，先遍历加购前 40 个产品，统计一边最大可加购数后再加购剩下产品
        3. 加购时判断当前加购的产品是否与 rank_pnk 的排序相同

    """
    # NOTICE 一个产品列表页默认 60 个产品（不算 Promovat）
    # NOTICE 购物车一次最多放 50 种产品

    # 启动检测加购弹窗作为后台任务
    check_cart_dialog_task = create_task(handle_cart_dialog(page))

    # 非 Promovat、非 Vezi Detalii 的加购按钮
    add_cart_buttons = page.locator(
        (
            'xpath=//div[starts-with(@class, "card-item")]'
            '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
            '//form/button[@data-pnk]'
        ),
    )
    # 页面上的加购按钮总数
    add_cart_button_count = await add_cart_buttons.count()
    logger.debug(f'找到 {add_cart_button_count} 个非 Promovat、非 Vezi Detalii 的加购按钮')

    # 页面上产品与其序号
    rank_pnk: dict[int, str] = {
        _ + 1: await add_cart_buttons.nth(_).get_attribute('data-pnk', timeout=MS1000)
        for _ in range(add_cart_button_count)
    }  # type: ignore
    logger.debug(
        f'从加购按钮找到 {len(rank_pnk)} 个 data-pnk\n{{{', '.join(f'{r}: "{p}"' for r, p in rank_pnk.items())}}}'
    )

    ##### 加购产品 #####
    cur = 1
    added_products: list[Product] = list()
    # 如果加购按钮不超过 40 个
    if add_cart_button_count <= 40:
        while cur < add_cart_button_count:
            if page.is_closed():
                break
            async with _add_cart_lock:
                try:
                    logger.debug(f'尝试点击第 {cur} 个加购按钮...')
                    await add_cart_buttons.nth(cur - 1).click(timeout=MS1000)
                except PlaywrightError as pe_click:
                    # logger.warning(f'尝试点击第 {cur} 个加购按钮失败\n{pe_click}')
                    continue
                else:
                    try:
                        pnk: str = await add_cart_buttons.nth(cur - 1).get_attribute('data-pnk', timeout=MS1000)  # type: ignore
                    except PlaywrightError as pe_getattr:
                        logger.error(f'尝试获取第 {cur} 个点击的加购按钮的 data-pnk 失败\n{pe_getattr}')
                    else:
                        if pnk == rank_pnk[cur]:
                            logger.debug(f'第 {cur} 个产品加购成功 pnk="{pnk}"')
                            added_products.append(Product(pnk=pnk, source_url=page.url, rank=cur))
                            cur += 1
                        else:
                            logger.error(
                                f'当前点击的第 {cur} 个加购按钮的 pnk 应当是 "{rank_pnk[cur]}" 实际是 "{pnk}"'
                            )

        result = await handle_cart(page.context, added_products, False)

    # 如果加购按钮超过 40 个
    else:
        while cur < add_cart_button_count:
            if page.is_closed():
                break
            if cur % 40 == 0:
                # 前 40 个产品的购物车数据
                result_pre_40 = await handle_cart(page.context, added_products, True)
                added_products.clear()
            async with _add_cart_lock:
                try:
                    logger.debug(f'尝试点击第 {cur} 个加购按钮...')
                    await add_cart_buttons.nth(cur - 1).click(timeout=MS1000)
                except PlaywrightError as pe_click:
                    # logger.warning(f'尝试点击第 {cur} 个加购按钮失败\n{pe_click}')
                    continue
                else:
                    try:
                        pnk: str = await add_cart_buttons.nth(cur - 1).get_attribute('data-pnk', timeout=MS1000)  # type: ignore
                    except PlaywrightError as pe_getattr:
                        logger.error(f'尝试获取第 {cur} 个点击的加购按钮的 data-pnk 失败\n{pe_getattr}')
                    else:
                        if pnk == rank_pnk[cur]:
                            logger.debug(f'第 {cur} 个产品加购成功 pnk="{pnk}"')
                            added_products.append(Product(pnk=pnk, source_url=page.url, rank=cur))
                            cur += 1
                        else:
                            logger.error(
                                f'当前点击的第 {cur} 个加购按钮的 pnk 应当是 "{rank_pnk[cur]}" 实际是 "{pnk}"'
                            )

        # 从第 41 个开始的产品
        result_past_40 = await handle_cart(page.context, added_products, False)
        result: list[Product] = result_past_40 + result_pre_40  # type: ignore

    await page.close()
    await check_cart_dialog_task

    return result
