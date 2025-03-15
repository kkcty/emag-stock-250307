"""正则表达式"""

from __future__ import annotations

from typing import TYPE_CHECKING
from re import compile

if TYPE_CHECKING:
    from re import Pattern


cart_page_api_routes: dict[str, Pattern[str]] = {
    'cart/remove': compile(r'.*?emag\.ro/cart/remove.*'),
    'cart/get-totals': compile(r'.*?emag\.ro/cart/get-totals.*'),
    'cart/refresh-vouchers': compile(r'.*?emag\.ro/cart/refresh-vouchers.*'),
    'cart/render-vendors': compile(r'.*?emag\.ro/cart/render-vendors.*'),
    'cart/get-notifications': compile(r'.*?emag\.ro/cart/get-notifications.*'),
    'shopping/header-cart': compile(r'.*?emag\.ro/shopping/header-cart.*'),
}
"""购物车页面的 API"""

cart_page_track_routes: dict[str, Pattern[str]] = {
    'ams.creativecdn.com/tags/v2': compile(r'.*?ams\.creativecdn\.com/tags/v2.*'),
    'ingest.de.sentry.io/api': compile(r'.*?ingest\.de\.sentry\.io/api.*'),
    'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js': compile(
        r'.*?pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js.*'
    ),
    'pdr.emag.ro/g/collect': compile(r'.*?pdr.emag.ro/g/collect.*'),
    'px.ads.linkedin.com': compile(r'.*?px\.ads\.linkedin\.com.*'),
    'sapi.emag.ro/recommendations/by-zone-position': compile(
        r'.*?sapi\.emag\.ro/recommendations/by-zone-position.*'
    ),
    'stats.g.doubleclick.net/j/collect': compile(r'.*?stats\.g\.doubleclick\.net/j/collect.*'),
    'emag.ro/logger.json': compile(r'.*?emag\.ro/logger\.json.*'),
}
"""购物车页面的埋点 API"""
