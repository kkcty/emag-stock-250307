"""购物车页面所用 Xpath"""

# BUG 卡片标签不对，定位不到捆绑产品
LINE_ITEM_DETAILS_DIV = 'xpath=//div[@class="line-item-details"]'
"""单个产品卡片"""

STERGE_BUTTON = (
    'xpath='
    '//div[@class="line-item-details"]/div/div[@class="mb-1"]'
    '/button[contains(@class, "remove-product")]'
)
"""移出购物车 Sterge 按钮"""

INCREASE_QUANTITY_BUTTON = (
    'xpath='
    '//div[@class="line-item-details"]//div[@class="line-qty-container"]/div'
    '/button[@data-test="increaseQtyBtn"]'
)
"""往购物车内追加产品的按钮"""

QUANTITY_SPAN = (
    'xpath='
    '//div[@class="line-item-details"]//div[@class="line-qty-container"]/div'
    '/span[@data-test="qtyValue"]'
)
"""购物车内的当前数量"""
