"""测试购物车页的解析器"""

import asyncio
from pathlib import Path

from scraper_utils.utils.browser_util import PersistentContextManager, ResourceType, MS1000

from emag_stock_monitor.models import Product
from emag_stock_monitor.page_handlers.cart_page import clear_cart, goto_cart_page, parse_qty


CWD = Path.cwd()


async def main():
    async with PersistentContextManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        user_data_dir=CWD.joinpath('chrome_data'),
        channel='chrome',
        headless=False,
        abort_res_types=(ResourceType.MEDIA, ResourceType.IMAGE),
        default_navigation_timeout=60 * MS1000,
        default_timeout=60 * MS1000,
        # no_viewport=False,
        # viewport={'height': 900, 'width': 1600},
    ) as pcm:
        page = await goto_cart_page(pcm.context, wait_until='networkidle')

        ##########
        # # 测试清空购物车
        # input('清空购物车...')
        # await clear_cart(page)

        ##########
        # # 测试统计 qty
        # input('统计购物车 qty...')
        # added_prodcuts = Products(
        #     [
        #         ListPageProduct(pnk=pnk, source_url='', rank=i)
        #         for i, pnk in enumerate(
        #             [
        #                 'D6X0QBBBM',
        #                 'DJ4XKKMBM',
        #                 'DHTSBQYBM',
        #                 'DQYX5M3BM',
        #                 'D8KRFWYBM',
        #                 'D1GTNWYBM',
        #             ],
        #             start=1,
        #         )
        #     ]
        # )
        # result = await parse_qty(page, added_prodcuts)
        # for r in result:
        #     print(r, r.rank)

        ##########
        input('程序结束...')


if __name__ == '__main__':
    asyncio.run(main())
