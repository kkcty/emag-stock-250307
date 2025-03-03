import asyncio
from pathlib import Path
from time import perf_counter

from playwright.async_api import BrowserContext
from scraper_utils.utils.browser_util import BrowserManager, ResourceType, MS1000

from .logger import logger
from .page_handlers.common import block_emag_track
from .page_handlers.cart_page import (
    goto_cart_page,
    clean_cart,
)
from .page_handlers.list_page import (
    wait_page_load as wait_list_page_load,
    add_item_to_cart,
)

"""
NOTICE 加购流程
1. 创建若干个非持久上下文
    * 隐藏上下文
    * 屏蔽日志埋点
    * 屏蔽特定资源类型以加快页面加载时间
2. 每个上下文创建若干个产品列表页面
    1. 等待产品列表页面加载
    2. 添加加购弹窗的处理器
    3. 遍历产品列表页面的加购按钮
3. 加购完成后打开购物车页面
    1. 遍历所有增加产品按钮，点击至最大值 50
    2. 统计每个产品的 pnk 和 最大加购数量
    3. 清空购物车

"""

cwd = Path.cwd()

abort_res_types = (
    ResourceType.MEDIA,
    ResourceType.IMAGE,
    ResourceType.FONT,
)

wait = lambda: input('Enter...')


async def test(context: BrowserContext):  # TEMP
    """测试"""
    list_page_1 = await context.new_page()
    # list_page_2 = await context.new_page()

    await list_page_1.goto('https://www.emag.ro/masinute/c')
    # await list_page_2.goto('https://www.emag.ro/masinute/p2/c')

    card_item_tag_count = await wait_list_page_load(list_page_1)
    # await wait_list_page_load(list_page_2)

    wait()

    add_item_to_cart_tasks = [
        add_item_to_cart(list_page_1, card_item_tag_count),
        # add_item_to_cart(list_page_2),
    ]
    await asyncio.gather(*add_item_to_cart_tasks)
    wait()

    cart_page = await goto_cart_page(context)
    wait()

    # await remove_item_from_cart(cart_page)
    # wait()


if __name__ == '__main__':

    async def main():
        """"""
        logger.info('程序启动')
        start_time = perf_counter()

        chrome_data_dir = cwd.joinpath('chrome_data')
        chrome_data_dir.mkdir(exist_ok=True)
        async with BrowserManager(
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            channel='chrome',
            headless=False,
            timeout=60 * MS1000,
        ) as bm:

            list_page_test_context = await bm.new_context(
                need_stealth=True,
                abort_res_types=abort_res_types,
            )
            await block_emag_track(list_page_test_context)
            await test(list_page_test_context)

        end_time = perf_counter()
        logger.info(f'程序结束，总用时 {round(end_time-start_time,2)} 秒')

    asyncio.run(main())
