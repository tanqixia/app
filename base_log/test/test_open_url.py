import threading
import time
import requests
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



def test_quests():
    url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20bags"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    "referer":"https://www.therealreal.com/",
    }
    request = requests.get(url,headers=headers)
    print(request.status_code)



if __name__ == '__main__':
    test_quests()