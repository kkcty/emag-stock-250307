from __future__ import annotations

import re
from sys import stderr
from typing import TYPE_CHECKING

from loguru import logger


if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Response, ProxySettings


__all__ = [
    'logger',
    'block_emag_track_endpoint',
    'captcha_handler',
]


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


logger.remove()
logger.add(
    stderr,
    format=(
        '[<green>{time:HH:mm:ss}</green>] [<level>{level:.3}</level>] '
        '[<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>] >>> '
        '<level>{message}</level>'
    ),
)


async def block_emag_track_endpoint(context: BrowserContext) -> None:
    """屏蔽 eMAG 的页面埋点"""
    for ep in _track_endpoints:
        await context.route(ep, lambda r: r.abort())


async def captcha_handler(response: Response) -> None:
    """处理验证码"""
    # TODO


async def get_proxy() -> ProxySettings:
    """获取代理"""
    # TODO
