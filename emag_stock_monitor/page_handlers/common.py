"""共通的页面处理器"""

from playwright.async_api import BrowserContext

from ..constants.regex import LOGGER_JSON_API, BY_ZONE_POSITION_API


async def block_emag_track(context: BrowserContext):
    """屏蔽 eMAG 的页面埋点"""
    await context.route(LOGGER_JSON_API, lambda r: r.abort('aborted'))
    await context.route(BY_ZONE_POSITION_API, lambda r: r.abort('aborted'))
