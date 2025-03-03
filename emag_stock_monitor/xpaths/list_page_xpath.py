"""产品列表页面所用 XPath"""

CARD_ITEM_DIV = 'xpath=//div[starts-with(@class, "card-item")]'
"""产品卡片所在的 div 标签"""

CARD_ITEM_DIV_WITHOUT_PROMOVAT = (
    'xpath='
    '//div[starts-with(@class, "card-item")]'
    '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
    '/span[starts-with(@class, "card-v2-badge-cmp")])]'
)
"""产品卡片所在的 div 标签（跳过 Promovat）"""

ADD_CART_BUTTON = (
    'xpath='  # WARNING 是不是没有 "Vezi detalii" 了？
    '//div[starts-with(@class, "card-item")]'
    '[not(.//div[starts-with(@class, "card-v2-badge-cmp-holder")]/span[starts-with(@class, "card-v2-badge-cmp")])]'
    '//form/button'
)
"""加购按钮（跳过 Promovat）"""

CART_DIALOG_CLOSE_BUTTON = (
    'xpath=//div[starts-with(@class, "modal-header")]/button[starts-with(@class, "close")]'
)
"""加购弹窗的关闭按钮"""

PROMOVAT_SPAN = (
    'xpath='
    '//div[starts-with(@class, "card-v2-badge-cmp-holder")]'
    '/span[starts-with(@class, "card-v2-badge-cmp")]'
)
"""Promovat 标志"""
