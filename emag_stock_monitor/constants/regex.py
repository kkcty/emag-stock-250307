"""正则表达式"""

from re import compile

########## 购物车页面：加载购物车页面会触发的请求 ##########

FAVORITES_LISTS_TYPE_EMAG_PRODUCT_IDS_API = compile(r'.*?emag\.ro/favorites/lists/type/emag/product_ids.*')

CART_PRODUCTS_API = compile(r'.*?emag\.ro/cart/products.*')
"""购物车页面：获取购物车的产品列表的 API"""

########## 购物车页面：点击 sterge 按钮会触发的请求 ##########

CART_REMOVE_API = compile(r'.*?emag\.ro/cart/remove.*')
"""将产品移出购物车"""

CART_GET_TOTALS_API = compile(r'.*?emag\.ro/cart/get-totals.*')

CART_REFRESH_VOUCHERS_API = compile(r'.*?emag\.ro/cart/refresh-vouchers.*')

CART_RENDER_VENDORS_API = compile(r'.*?emag\.ro/cart/render-vendors.*')

CART_GET_NOTIFICATIONS_API = compile(r'.*?emag\.ro/cart/get-notifications.*')
"""购物车页面：获取提醒的 API"""

########## 其它 ##########

SHOPPING_HEADER_CART_API = compile(r'.*?emag\.ro/shopping/header-cart.*')

LOGGER_JSON_API = compile(r'.*?emag\.ro/logger\.json.*')
"""eMAG 埋点日志 API"""

BY_ZONE_POSITION_API = compile(r'.*?sapi\.emag\.ro/recommendations/by-zone-position.*')
