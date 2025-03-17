itv = null;

// 自动隐藏 eMAG 的 cookie 提示
function hideCookieBanner() {
    const xpath = '//div[starts-with(@class, "gdpr-cookie-banner")]';
    const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);

    if (result.singleNodeValue) {
        result.singleNodeValue.style.visibility = 'hidden';
        clearInterval(itv);
    }
}

// 在DOM加载完成后立即执行
document.addEventListener('DOMContentLoaded', hideCookieBanner);

// 每500ms检查一次（应对动态加载内容）
itv = setInterval(hideCookieBanner, 500);
