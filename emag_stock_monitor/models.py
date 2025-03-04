"""数据模型"""

from typing import Any, Iterable, Iterator, Optional, Self

from scraper_utils.utils.emag_util import build_product_url, validate_pnk


class CartProduct:
    """购物车内的产品"""

    def __init__(self, pnk: str, qty: int = 0):
        if not validate_pnk(pnk=pnk):
            raise ValueError(f'"{pnk}" 不符合 pnk 规则')
        self.pnk = pnk
        self.qty = qty

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pnk="{self.pnk}", url="{self.url}")'

    def __hash__(self) -> int:
        return hash(self.pnk)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.pnk == other.pnk

    @property
    def url(self) -> str:
        """产品详情页链接"""
        return build_product_url(pnk=self.pnk)


class CartProducts:
    """购物车内的产品列表"""

    def __init__(self, products: Optional[Iterable[CartProduct]] = None) -> None:
        self.products: set[CartProduct] = set()

        if products is None:
            return

        for np in products:
            op = next((_ for _ in self.products if _ == np), None)
            if op is not None and np.qty > op.qty:
                self.products.remove(op)
                self.products.add(np)

    def __contains__(self, x: Any) -> bool:
        return isinstance(x, CartProduct) and x in self.products

    def __iter__(self) -> Iterator[CartProduct]:
        return iter(self.products)

    def get(self, p: str | CartProduct) -> Optional[CartProduct]:
        match p:
            case str():
                p = CartProduct(p)
            case CartProduct():
                pass
            case _:
                raise TypeError
        return next((_ for _ in self if _ == p), None)

    def add(self, x: CartProduct) -> None:
        if not isinstance(x, CartProduct):
            raise TypeError

        old = self.get(x)
        if old is not None and x.qty > old.qty:
            self.products.remove(old)
            self.products.add(x)

    def __add__(self, other: Any) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = CartProducts(_ for _ in self)
        for x in other:
            result.add(x)
        return result  # type: ignore

    def __radd__(self, other: Any) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = CartProducts(_ for _ in self)
        for x in other:
            result.add(x)
        return result  # type: ignore

    def __iadd__(self, other: Any) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        for x in other:
            self.add(x)
        return self
