"""数据模型"""

from typing import Any, Generator, Iterable, Iterator, Optional, Self, TypedDict

from scraper_utils.utils.emag_util import build_product_url, validate_pnk


_CartProductTypedDict = TypedDict(
    '_CartProductTypedDict',
    {
        'pnk': str,
        'url': str,
        'qty': int,
    },
)


class CartProduct:
    """购物车内的产品"""

    def __init__(self, pnk: str, qty: int = 0):
        if not validate_pnk(pnk=pnk):
            raise ValueError(f'"{pnk}" 不符合 pnk 规则')
        self.pnk = pnk
        self.qty = qty

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pnk="{self.pnk}", qty={self.qty})'

    def __hash__(self) -> int:
        return hash(self.pnk)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.pnk == other.pnk

    @property
    def url(self) -> str:
        """产品详情页链接"""
        return build_product_url(pnk=self.pnk)

    def as_dict(self) -> _CartProductTypedDict:
        "转为字典"
        return {
            'pnk': self.pnk,
            'url': self.url,
            'qty': self.qty,
        }


class CartProducts:
    """购物车内的产品列表"""

    def __init__(self, products: Optional[Iterable[CartProduct]] = None):
        self.__products: dict[str, CartProduct] = dict()
        if products is not None:
            for p in products:
                self.add(p)

    @property
    def products(self) -> Generator[CartProduct]:
        return (_ for _ in self.__products.values())

    def add(self, np: CartProduct) -> None:
        op = self.get(np.pnk)
        if op is None or np.qty > op.qty:
            self.__products[np.pnk] = np

    def __add__(self, other: Self) -> Self:
        result = self.__class__(self.__products.values())
        for i in other.products:
            result.add(i)
        return result

    def __iadd__(self, other: Self) -> Self:
        for i in other.products:
            self.add(i)
        return self

    def get(self, p: str | CartProduct) -> Optional[CartProduct]:
        p = p.pnk if isinstance(p, CartProduct) else p
        return self.__products.get(p)

    def __contains__(self, p: str | CartProduct) -> bool:
        p = p.pnk if isinstance(p, CartProduct) else p
        return p in self.__products

    def remove(self, p: str | CartProduct) -> None:
        p = p.pnk if isinstance(p, CartProduct) else p
        self.__products.pop(p, None)

    def __iter__(self) -> Iterator[CartProduct]:
        return self.products

    def __len__(self) -> int:
        return len(self.__products)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(count={len(self)})'
