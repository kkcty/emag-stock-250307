from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from scraper_utils.utils.time_util import now_str

if TYPE_CHECKING:
    pass


class CaptchaError(Exception):
    """遇到验证码时抛出的异常"""

    def __init__(self, url: str, status: int, message: str, time: Optional[str] = None) -> None:
        self.url = url
        self.status = status
        self.message = message
        self.time = time if time is not None else now_str()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.message}\t{{url="{self.url}", status={self.status}, time="{self.time}"}}'
