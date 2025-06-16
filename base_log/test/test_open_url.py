import threading
import time
def fetch_data(page, url, results, idx):
    """每个标签中获取数据后保存到results中。"""
    try:
        tab = page.new_tab(url)
        # 获取需要的数据



        data = tab.ele('xxxxx').text
        results[idx] = data
    except Exception as e:
        print(f'{url} 失败: {e}')

def fetch_all(page, urls):
    """并发获取每个页面的数据。"""
    threads = []
    results = [None] * len(urls)
    for i, url in enumerate(urls):
        t = threading.Thread(target=fetch_data, args=(page, url, results, i))
        t.start()
        threads.append(t)
        time.sleep(0.1)

    for t in threads:
        t.join()

    return results




if __name__ == '__main__':
    co = ChromiumOptions().set_local_port(9226).set_user_data_path('data1')
    page = ChromiumPage(co)

    url_list = [
        "http://www.baidu.com",
        "http://www.taobao.com",
        "http://www.jd.com",
        "http://www.qq.com",
        "http://www.sina.com.cn"
    ]

    results = fetch_all(page, url_list)
    print("获取到的数据为:")
    for url, data in zip(url_list, results):
        print(url, "->", data)

    input("按回车退出")
    page.quit()
