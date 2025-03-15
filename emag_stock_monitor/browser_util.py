"""浏览器工具"""

from __future__ import annotations

from typing import TYPE_CHECKING

from emag_stock_monitor.regexps import cart_page_track_routes

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext


async def block_emag_track(context: BrowserContext):
    """屏蔽 eMAG 的页面埋点"""
    for k, v in cart_page_track_routes.items():
        await context.route(v, lambda r: r.abort())
