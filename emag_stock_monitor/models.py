"""数据模型"""

from typing import Iterable, Iterator, Optional, TypedDict, Self

from scraper_utils.utils.emag_util import build_product_url, validate_pnk


class _ProductTypedDict(TypedDict):
    pnk: str
    source_url: str
    rank: int
    qty: Optional[int]
    url: str


class ListPageProduct:
    """
    产品列表页上的一个产品

    ---

    * `pnk`
    * `source_url`: 该产品来自哪个产品列表页
    * `rank`: 该产品在其来源产品列表页上的序号（从 1 开始）
    * `qty`: 产品最大可加购数（`None` 或正整数）
    * `url`: 产品详情页链接

    ---

    pnk 和 source_url 都相同的会被认为是同一个产品

    <b>WARNING rank 不同的该怎么办？</b>
    """

    def __init__(self, pnk: str, source_url: str, rank: int, qty: Optional[int] = None) -> None:
        self.pnk = pnk
        self.source_url = source_url
        self.rank = rank
        self.qty = qty

    @property
    def pnk(self) -> str:
        return self._pnk

    @pnk.setter
    def pnk(self, pnk: str) -> None:
        if not validate_pnk(pnk=pnk):
            raise ValueError(f'"{pnk}" 不符合 pnk 规则')
        self._pnk = pnk

    @property
    def rank(self) -> int:
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        if rank < 1:
            raise ValueError('rank 需为正整数')
        self._rank = rank

    @property
    def qty(self) -> Optional[int]:
        return self._qty

    @qty.setter
    def qty(self, qty: Optional[int]) -> None:
        if qty is not None and qty < 1:
            raise ValueError(f'qty 如不为空，则必须为正整数')
        self._qty = qty

    @property
    def url(self) -> str:
        return build_product_url(pnk=self._pnk)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._pnk == other._pnk
            and self.source_url == other.source_url
        )

    def __hash__(self) -> int:
        return hash((self._pnk, self.source_url))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pnk="{self._pnk}", origin_url="{self.source_url}", qty={self.qty}, rank={self.rank})'

    def as_dict(self) -> _ProductTypedDict:
        return {
            'pnk': self._pnk,
            'source_url': self.source_url,
            'rank': self.rank,
            'qty': self.qty,
            'url': self.url,
        }


class Products:
    """产品集合"""

    # FIXME 需要添加一个修改 qty 的功能

    def __init__(self, products: Optional[Iterable[ListPageProduct]] = None) -> None:
        if products is None:
            products = list()
        self.__products = list(products)
        self.__modified: bool = True

    @property
    def products(self) -> list[ListPageProduct]:
        # 按照 source_url-rank 的顺序对产品进行排序，
        # 顺便对于重复的产品，取其 rank 最小的保留，其余去除

        if self.__modified is False:  # 如果 __products 没被修改那就直接返回 __products
            return self.__products

        temp = set(i for i in sorted(self.__products, key=lambda p: (p._pnk, p.source_url, p.rank)))
        result = list(sorted(temp, key=lambda p: (p.source_url, p.rank)))
        self.__products = result
        self.__modified = False
        return self.__products

    def append(self, value: ListPageProduct) -> None:
        """添加一个元素"""
        self.__products.append(value)
        self.__modified = True

    def appends(self, *values: ListPageProduct) -> None:
        """添加多个元素"""
        for v in values:
            self.append(v)

    def have_pnk(self, pnk: str) -> bool:
        """检测产品列表中有无该 pnk"""
        return validate_pnk(pnk=pnk) and any(p._pnk == pnk for p in self)

    def __add__(self, other) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = self.__class__(products=self.products + other.products)
        return result

    def __iadd__(self, other) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        sp = self.products
        op = other.products
        self.__products = sp + op
        self.__modified = True
        return self

    def __iter__(self) -> Iterator[ListPageProduct]:
        return iter(self.products)

    def __contains__(self, value: ListPageProduct) -> bool:
        return value in self.products

    def __len__(self) -> int:
        return len(self.products)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(count="{len(self)}")'
