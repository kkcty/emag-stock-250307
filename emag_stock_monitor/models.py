"""数据模型"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Self, TypedDict

from scraper_utils.utils.emag_util import build_product_url, validate_pnk

if TYPE_CHECKING:

    class _ProductTypedDict(TypedDict):
        pnk: str
        source_url: str
        rank: int
        top_favorite: bool
        review_count: Optional[int]
        qty: Optional[int]
        url: str


class Product:
    """
    产品列表页上的一个产品

    ---

    * `pnk`
    * `source_url`: 该产品来自哪个产品列表页
    * `rank`: 该产品在其来源产品列表页上的排序（从 1 开始）
    * `top_favorite`: 是否带 TOP 标
    * `review_count`: 评论数
    * `qty`: 产品最大可加购数（`None` 或正整数）
    * `url`: 产品详情页链接

    ---

    pnk 和 source_url 都相同的会被认为是同一个产品
    """

    def __init__(
        self,
        pnk: str,
        source_url: str,
        rank: int,
        top_favorite: bool = False,
        review_count: Optional[int] = None,
        qty: Optional[int] = None,
    ) -> None:
        if not validate_pnk(pnk=pnk):
            raise ValueError(f'"{pnk}" 不符合 pnk 规则')
        self.__pnk = pnk
        self.source_url = source_url
        self.rank = rank
        self.top_favorite = top_favorite
        self._review_count = review_count
        self.qty = qty

    @property
    def pnk(self) -> str:
        return self.__pnk

    @property
    def rank(self) -> int:
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        if rank < 1:
            raise ValueError('rank 需为正整数')
        self._rank = rank

    @property
    def review_count(self) -> Optional[int]:
        return self._review_count

    @review_count.setter
    def review_count(self, review_count: Optional[int]) -> None:
        if review_count is not None and review_count < 0:
            raise ValueError('review 不能为负数')
        self._review_count = review_count

    @property
    def qty(self) -> Optional[int]:
        return self._qty

    @qty.setter
    def qty(self, qty: Optional[int]) -> None:
        if qty is not None and qty < 1:
            raise ValueError('qty 如不为空，则必须为正整数')
        self._qty = qty

    @property
    def url(self) -> str:
        return build_product_url(pnk=self.__pnk)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.__pnk == other.__pnk
            and self.source_url == other.source_url
        )

    def __hash__(self) -> int:
        return hash((self.__pnk, self.source_url))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pnk="{self.__pnk}", origin_url="{self.source_url}", qty={self.qty}, rank={self.rank})'

    def as_dict(self) -> _ProductTypedDict:
        return {
            'pnk': self.__pnk,
            'source_url': self.source_url,
            'rank': self.rank,
            'top_favorite': self.top_favorite,
            'review_count': self.review_count,
            'qty': self.qty,
            'url': self.url,
        }

    def __copy__(self) -> Self:
        return self.__class__(
            pnk=self.pnk,
            source_url=self.source_url,
            rank=self.rank,
            top_favorite=self.top_favorite,
            review_count=self.review_count,
            qty=self.qty,
        )
