from __future__ import annotations

import re
from sys import stderr
from typing import TYPE_CHECKING

from loguru import logger
from scraper_utils.utils.file_util import read_file

from .exceptions import CaptchaError


if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page, Response, ProxySettings


__all__ = [
    'logger',
    'block_track_endpoint',
    'block_cookie_banner',
    'captcha_handler',
    'get_proxy',
]


logger.remove()
logger.add(
    stderr,
    format=(
        '[<green>{time:HH:mm:ss}</green>] [<level>{level:.3}</level>] '
        '[<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>] >>> '
        '<level>{message}</level>'
    ),
)


_track_endpoints = [
    re.compile(r'.*?ams\.creativecdn\.com/tags/v2.*'),
    re.compile(r'.*?ingest\.de\.sentry\.io/api.*'),
    re.compile(r'.*?pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js.*'),
    re.compile(r'.*?pdr.emag.ro/g/collect.*'),
    re.compile(r'.*?px\.ads\.linkedin\.com.*'),
    re.compile(r'.*?sapi\.emag\.ro/recommendations/by-zone-position.*'),
    re.compile(r'.*?stats\.g\.doubleclick\.net/j/collect.*'),
    re.compile(r'.*?emag\.ro/logger\.json.*'),
]


async def block_track_endpoint(context: BrowserContext) -> None:
    """屏蔽 eMAG 的页面埋点"""
    for ep in _track_endpoints:
        await context.route(ep, lambda r: r.abort())


_hide_cookie_banner_js = read_file(file='js/hide-cookie-banner.js', mode='str', async_mode=False)


async def block_cookie_banner(page: Page) -> None:
    """屏蔽 cookie 提示"""
    await page.add_init_script(script=_hide_cookie_banner_js)


_captcha_url_status: dict[str, tuple[re.Pattern[str], int]] = {
    'www.emag.ro': (re.compile(r'.*?www.emag.ro.*'), 511),
    'challenges.cloudflare.com': (re.compile(r'.*?challenges.cloudflare.com.*'), 401),
    # TODO 还需更多 endpoints
}


async def captcha_handler(response: Response) -> None:
    """处理验证码"""
    url = response.url
    status = response.status
    if any(
        status == expect_status and url_pattern.search(url) is not None
        for url_pattern, expect_status in _captcha_url_status.values()
    ):
        logger.error(f'检测到验证码 "{url}" {status}')
        raise CaptchaError(url=url, status=status)


async def get_proxy() -> ProxySettings:
    """从 IP 池供应商那获取代理"""
    # TODO
