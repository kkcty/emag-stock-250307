"""XPATH 表达式"""

# TODO 完善 XPATH
# TODO 按页面分类存放

########## 购物测页面 ##########


CART_PAGE_STERGE_BUTTON_XPATH = (
    'xpath=//div[@class="line-item line-item-footer d-none d-md-block"]/div/button[@data-line]'
)
"""购物车页的 Sterge 按钮"""

CART_PAGE_ADD_ITEM_BUTTON_XPATH = ''  # TODO
"""购物车页的加购按钮"""


########## 产品列表页面 ##########


LIST_PAGE_CARD_ITEM_DIV_XPATH = (
    'xpath=//div[(@class="card-item card-standard js-product-data js-card-clickable " or '
    '@class="card-item card-fashion js-product-data js-card-clickable") and @data-url!=""]'
)
"""产品列表页的产品标签（包含 Promovat 标志）"""

LIST_PAGE_CARD_ITEM_WITHOUT_PROMOVAT_DIV_XPATH = (
    'xpath=//div[(@class="card-item card-standard js-product-data js-card-clickable "'
    ' or @class="card-item card-fashion js-product-data js-card-clickable") and @data-url!=""]'
    '[not(.//span[@class="card-v2-badge-cmp badge bg-light bg-opacity-90 text-neutral-darkest"]) and .//form]'
)
"""产品列表页的产品标签（不包含 Promovat 标志）"""

LIST_PAGE_ADD_CART_BUTTON_XPATH = (
    'xpath=//button[@class="btn btn-sm btn-emag btn-block yeahIWantThisProduct"]'
)
"""产品列表页的产品标签内的加购按钮"""

LIST_PAGE_ADD_CART_DIALOG_CLOSE_BUTTON_XPATH = 'xpath=//button[@class="close gtm_6046yfqs"]'
"""产品列表页的加购弹窗的关闭按钮"""
