from DrissionPage.common import Settings



Settings.set_language('zh_cn')  # 设置为中文时，填入'zh_cn'

def open_url():
    pass




if __name__ == '__main__':
    open_url()

    from DrissionPage import Chromium

    tab = Chromium().latest_tab
    tab.get('http://DrissionPage.cn')