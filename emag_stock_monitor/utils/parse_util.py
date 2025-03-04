"""解析用工具"""

import re
from typing import Optional


parse_pnk_pattern = re.compile(r'pd/([0-9A-Z]{9})($|/|\?)')


def parse_pnk(url: str) -> Optional[str]:
    """从链接中解析 pnk"""
    pnk_match = parse_pnk_pattern.search(url)
    if pnk_match is not None:
        return pnk_match.group(1)
    return None
