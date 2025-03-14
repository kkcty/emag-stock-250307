// 自动关闭加购弹窗
const observer = new MutationObserver(() => {
    const closeBtn = document.evaluate(
        '//button[@class="close gtm_6046yfqs"]',
        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null

    ).singleNodeValue;

    if (closeBtn) {
        closeBtn.style.opacity = '0';
        setTimeout(() => closeBtn.remove(), 200);
    }
});

observer.observe(
    document.body,
    {
        childList: true,
        subtree: true
    }
);

window.addEventListener('beforeunload', () => {
    observer.disconnect();
});