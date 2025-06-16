import sys
from pathlib import Path
from DrissionPage import Chromium,ChromiumOptions
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from main_method  import write_lists_to_csv,read_urls_from_csv,open_url_get_shop_url,get_shop_urls
import time
import ast
import json

def parse_cookie_string(cookie_str):
    """
    将浏览器格式的Cookie字符串转换为字典
    支持包含domain/path等属性和复杂值的场景
    """
    cookies = {}
    for item in cookie_str.strip().split(';'):
        item = item.strip()
        if not item:
            continue
        
        # 处理键值对（包括domain=xxx这种情况）
        if '=' in item:
            key, value = item.split('=', 1)  # 只分割第一个等号
            cookies[key] = value
        else:
            # 处理只有key没有value的属性（如HttpOnly）
            cookies[item] = None
    
    return cookies

# 针对条件判断的问题，可以设置一个校验，先找到哪个就执行哪个，这样可以避免等待

# user-agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36" 
cookie = "domain=.therealreal.com;__adroll_fpc=2b3ee8f03e06ade8d3de4562652f5770-1749742494232; _fbp=fb.1.1749742494418.763437766250198331; _pin_unauth=dWlkPU9UYzVNVGM0TTJZdE1EVmtOeTAwTWpZNUxUazNZVEF0WVRGa01URXlPVE5sTVRRMQ; _ketch_consent_v1_=eyJhbmFseXRpY3MiOnsic3RhdHVzIjoiZGVuaWVkIiwiY2Fub25pY2FsUHVycG9zZXMiOlsiYW5hbHl0aWNzIl19LCJiZWhhdmlvcmFsX2FkdmVydGlzaW5nIjp7InN0YXR1cyI6ImRlbmllZCIsImNhbm9uaWNhbFB1cnBvc2VzIjpbImJlaGF2aW9yYWxfYWR2ZXJ0aXNpbmciXX0sImVzc2VudGlhbF9zZXJ2aWNlcyI6eyJzdGF0dXMiOiJncmFudGVkIiwiY2Fub25pY2FsUHVycG9zZXMiOlsiZXNzZW50aWFsX3NlcnZpY2VzIl19fQ%3D%3D; last_logged_in_identifiers=39274561|2169265e-e29c-45b2-9b86-05c510f2ddfd; enable_similar_links_on_available_plp-initial-exp=variant; registered=true; nearby_stores=W10; _pxhd=PlgLotoM3ZwVGAXCNeRk4/UU3VS/qSj5ATIaDdln6TPf95kNS55fbKcyLV143graF214yepFrqjl30DMAtHp4Q==:y7iPXk0SRs5VYEtE9jECZZaaBFBxjT5WxbcHQpq2jQDiQmFJUT0lEpE-M/hOO6NeTOw1A8hKgm-4vsCjnbLU3z5WNfMQDWY1bpNPIADdrjU=; __ssid=c8c9c028ee93af00ca64a4a7983726a; pxcts=364bf138-481b-11f0-835f-4acf90ac2806; _pxvid=c6307b80-47a2-11f0-8e8e-209c3c068e2f; _px2=eyJ1IjoiMzVkZjUxMzAtNDgxYi0xMWYwLWJmYzQtMzMyMjY4ZTAzZDBjIiwidiI6ImM2MzA3YjgwLTQ3YTItMTFmMC04ZThlLTIwOWMzYzA2OGUyZiIsInQiOjE1NjE1MDcyMDAwMDAsImgiOiJlNGYwYmU1NjA4OWM1ZjUxN2RhOTNhZGUzMTgyOTM1OTJkYjBlZjJhNDU4ODNjNTY2YzBlZWQxNjM0ZWE3NmE5In0=; checkout_continuity_service=ef5468b9-0da3-4711-a04c-9521865e14dd; tracker_device=ef5468b9-0da3-4711-a04c-9521865e14dd; ajs_user_id=39274561; ajs_anonymous_id=16393dbd-6bde-4ede-a5db-522b5bd97dce; _swb=344ee44f-f02b-45d7-b895-76bc9745b8e5; _swb_consent_=eyJjb2xsZWN0ZWRBdCI6MTc0OTc5NTA4MiwiZW52aXJvbm1lbnRDb2RlIjoicHJvZHVjdGlvbiIsImlkZW50aXRpZXMiOnsiX3NlZ21lbnRBbm9ueW1vdXNJRCI6IjE2MzkzZGJkLTZiZGUtNGVkZS1hNWRiLTUyMmI1YmQ5N2RjZSIsIl9zZWdtZW50VXNlcklEIjoiMzkyNzQ1NjEiLCJzd2JfdGhlcmVhbHJlYWxfY29tIjoiMzQ0ZWU0NGYtZjAyYi00NWQ3LWI4OTUtNzZiYzk3NDViOGU1In0sImp1cmlzZGljdGlvbkNvZGUiOiJkZWZhdWx0IiwicHJvcGVydHlDb2RlIjoidGhlcmVhbHJlYWxfY29tIiwicHVycG9zZXMiOnsiYW5hbHl0aWNzIjp7ImFsbG93ZWQiOiJmYWxzZSIsImxlZ2FsQmFzaXNDb2RlIjoiY29uc2VudF9vcHRpbiJ9LCJiZWhhdmlvcmFsX2FkdmVydGlzaW5nIjp7ImFsbG93ZWQiOiJmYWxzZSIsImxlZ2FsQmFzaXNDb2RlIjoiY29uc2VudF9vcHRpbiJ9LCJlc3NlbnRpYWxfc2VydmljZXMiOnsiYWxsb3dlZCI6InRydWUiLCJsZWdhbEJhc2lzQ29kZSI6ImRpc2Nsb3N1cmUifX19; _session_id=SUdQTTFMZnQ3WStWTmZubnNCcU43UmpYY1hWbCt0OHN6SklBSVVseHNQdEx3ckxYR3JxR2ZDVjJVVHQyVDRjb1RVQk5lZTYzMXRYRDRkc2cybXVjOUhPVjkrb2VPWFZNczdqOURPcGI4RHQ2VlZkbkg0eGpwNUNJMGo1R0hiSDlwYnJKMXc2TkRDNkwzMTJhdnNtSUFRLzZHWFIyZUp1MHdxenJUU0xRaytHL1E5TnpLZSs3N2VGNndneFl5aVZsK01xckpQS1pJUU5XZmx0Uy9mK01UUnpkUkZSd1B5dFBRN1N0ZWJ1ZDdHUGJ2Yld2dE5KR0xIcDk2L0FHWVRhZENDbGh5dUVMZ3gxZFdHRVo4Ym1LRU53T1F1dkFjTzliRFVUT2ZybUQrS1ZVQXNmajNycnM5QWpjM3RmMnVka1VSTHRsM0Fva3pjdEJNZEp2SkF5UzI1dnlTUFRqVVFtZkdVTDBpNGEweFJFYmdEbTlURFRMZXQrT2tIeUpJWTVTb0dvL3NVNjQ3cHNMZGxjdHhrQnFjNDE1Mko2YW5mMkN0SXk0THc2dnh1Wit1MkdjR3NxOE0yMmpSR0FTRjhDQWw5M1hRdzgwdnh1ZGZnZDNwZC9YK3ZBWWdibWQzc2RlU1EvOVE5NjhWTGFEc2xlQng0dit4am55L2JWcllFUjUvdFpGOEFWUlBoSjRkMkNlTHdRbjdwbjA1QnU2dDFOZHZCeW5Da3NDVkxtS0pmMXlMTzZIN0RiM3dVTkh6SWRBcXZlUjJjUDFLYUFtQVp5KzVyakMyRWFLcVhMUHBsTWFGdGtnWlkzNkVGeTMwUko5QXduVUpSZ2JLYWFYOHQzQ0RONndOWTMrOU9wUkw2ZW5GaDNqQy9tWndsUnBKcEtlVW1xTEZ0QkhxN0tDcDRNMU1SWnZQc0pnQ2QvZEwzV3ZWZ2pzVVorbUpFdGJIT1ovbU5wQWc4QisrSXZ5ZCs4SkpDVi9BbE5tZkM5TEpIaGhZZW1CL2tuZk1rQWszRGFIYllTU1dnRWpSU1M1MStuUThUSE9OZmZOd3VINHFJN3lVN0cwdDRjNWg3QVJxV29GVTVLUmdSQnVSaE1sZnFtaXE1a1dnTEJobGU4WmhIbFVHanhEdHp6V1RvUytkWTRmNExyeUQrUkloa0NlbU1tbmwrUGFhT1M2TU1URzJ0eU4wblM2Mm9KdUJXL2ZIWVlYMFVQM3VPcnB1dFNKWEszUTlNRFBDd284SGZXdXd6djZ1Q1RXcmpJa3hCdEh4bVFIK2Q1anJWYXBPaFBKREFidFlDMDVjeG93UWlVZ1JnQmgydmluRnFMNzZ0bjBrSFlFbVFsdDMyV0hVUjRYdlVtV3Y1WFVJSnBHTVZRRWs1MG0rM0NCc2dyck1SOFRLMFNrNGNNZVFHSk9vWGY0MVA0S0Fvd3hIL0VhSFBXZGc2STJzNW9oYXlGTWpJM05xS3oxZHZ2dVhUS3ZUcHA3bFQwcUc0M3FiNkE4bUc3eVhxZ2xzMWViZ2hJbHBKZktLNlIwSStBWHIyM0tOUE0xcFFyZjI5K0ViYlh1ZU5HSUd4Rk9jK1pYbUJCdi9wbG1XaVdFY2U0WUhsVVo3dkZjbnE2ZWk1ME1TNFJwRkFHMktPckNTaTFOeFZlQlpQZElyT041TE9obGNjelFVTE8rM1Uzd2I2ZVlpUzVmVDU5eVMrVGphTzlNeTFTbHkxMTJlaG5paTFRcktldXFvVWJsamoweHZ1L3orbVUxSCthVC9zSWNJWjlMY0VXNjJYRHYzWndIUmVqVzZlREg4czl0N3NzMnUxZzdxa05LU0JqeFVNeWh6M3MwT3YwUHo0N25admE0RnZ4K3dMRnBpcHQzRTkxc3Q2QUxoTXo5cUdpaVV4NDk4UmV6NmZHUWZyamlDTjVFazF2UEpHQWtJY2ZySTR5NC9SMmhaa2RoZDB0VlI2NFIzUDBFYjE2RUhZU2RFTWE2cGkxL283QXY5RDdjL0hPdDI5Y3YrK1l0ODJRVnVJemczWDlpclpnd1NSQ1hxMTdVbWJrS1JuZE01elFqZUxhbEVFakdBWmdpV1V3UStCYlg2bXg0QTRSTjgxQT0tLXlCZEJnSWhxa0tSSmxoQzV6VWVHanc9PQ%3D%3D--342eed8b7fa398f6a390f16a68877836f3a8924a; __ar_v4=OF3FCM4OFZG4TLJK7JEAAV%3A20250612%3A7%7CBBODAYSHJJDRLP6HI5M56H%3A20250612%3A7%7CWEGDQEKGEZBIVDDMGIEHGG%3A20250612%3A8; _dd_s=rum=0&expire=1749796003451; _pxde=6659092b2736bd8fbe2e78d7a5632f2e3b2f8b1b68fcfc41f4d8a3f515c56ced:eyJ0aW1lc3RhbXAiOjE3NDk3OTUxMDQ5NTcsImZfa2IiOjB9"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}

# jewelry



cookie_dict = parse_cookie_string(cookie)

def find_difference(set_a, set_b):
    """
    找出在A集合但不在B集合中的元素
    
    参数:
        set_a: 第一个集合(数据较少)
        set_b: 第二个集合(数据较多)
        
    返回:
        如果A中有元素不在B中，返回这些元素的集合
        如果A中所有元素都在B中，返回False
    """
    difference = set_a - set_b  # 计算差集
    if difference:
        return difference
    else :
        return False

def test_redirects():
    """测试重定向"""
    from DrissionPage import SessionPage

    page = SessionPage()
    page.get('http://g1879.gitee.io/drissionpage')




if __name__ == '__main__':
# 示例1: A中有元素不在B中
    A = {1, 2, 3, 4}
    B = {3, 4, 5, 6, 7, 8}
    result = find_difference(A, B)
    print(result)  # 输出: {1, 2}

    # 示例2: A中所有元素都在B中
    A = {3, 4}
    B = {1, 2, 3, 4, 5, 6}
    result = find_difference(A, B)
    print(result)  # 输出: False


    # bags = "bags"
    # co1 = ChromiumOptions().set_local_port(9222)
    # page = Chromium(co1).latest_tab
    # # 这里可能会出现验证
    # page.set.cookies(cookie)
    # open_url_get_shop_url(page,bags)

    # # shop_list,link_list = get_shop_urls(page)

    # # # 将数据写入CSV文件
    # # write_lists_to_csv(urls = link_list,names = shop_list,)
    # # # 读取CSV文件中连接列，并且返回集合，这里在多进程运行的时候也是这样读取的

    # # # 以上为商品链接保存完毕，接下来的任务是需要再多进程中运行
    
    # # url_set = read_urls_from_csv()
    # # 如果新探索到的链接不在集合中，则返回链接，后期通过代码进行加购，但是有可能需要返回商品ID，所以后期再保存或者获取的时候，需要得到商品ID
    


    # # 请求的网址是：https://www.therealreal.com/cart/items
    # # ID = data-product-id，属性，_analytics_session_i=data-analytics-session-id属性，另外两个参数可以为空，其中query_id在data-analytics-attributes列表中的query_ID
    # # 表单数据是：id=41953892&_analytics_session_id=1749787048157&return_product_id=&protection_product_id=&query_id=e17b491e5aa8a9015b1e2925d61f6ea8

    # shop_list = page.ele("@@class=product-grid")
    # # shop_list_ele = shop_list.eles('@@class=product-card__description product-card__link js-product-card-link') # 可以获取商品名称和连接，也就是.text和.link

    # id_list_eles = shop_list.eles('@@class=product-card-wrapper js-product-card-wrapper')
    # start_time = time.time()
    # id_list = []
    # session_id_list = []
    # query_id_list = []
    # for i_ele in id_list_eles:

    #     # print(f"i是{i}")
    #     base_ele = i_ele.ele("@@class=product-card js-plp-product-card ") # 可以获取id，也就是.attr("id")
    #     # 获得ID属性
    #     id  = base_ele.attr("data-product-id")
    #     id_list.append(id)
    #     # print(f"id是{id}")
    #     # 获得_analytics_session_id属性
    #     _analytics_session_id_ele = base_ele.ele("@@class=obsession-container js-obsess-box-container").ele("t:button")
    #     _analytics_session_id = _analytics_session_id_ele.attr("data-analytics-session-id")
    #     # print(f"_analytics_session_id的值是{_analytics_session_id}")
    #     session_id_list.append(_analytics_session_id)
    #     # 获得query_id
    #     dict_str = _analytics_session_id_ele.attr("data-analytics-attributes")
    #     query_id = json.loads(dict_str)["queryID"]
    #     print(f"query_id的值是{query_id},类型是{type(query_id)}")
    #     query_id_list.append(query_id)


    # print(f"耗时是{time.time()-start_time}")




    # import requests
    # good_id = id_list[0]
    # session_id = session_id_list[3]
    # query_id = query_id_list[3]

    # url = 'https://www.therealreal.com/cart/items'
    # form_data = {
    #     'id': good_id,
    #     '_analytics_session_id': session_id,
    #     'return_product_id': '',
    #     'protection_product_id': '',
    #     'query_id': query_id
    # }

    # # 发送POST请求
    # response = requests.post(url, data=form_data,headers=headers,cookies=cookie_dict)
    # print(response.status_code)
    # # TODO: 这里返回的代码如果是200，就代表架构成功，如果是403表示遇到了人机验证，需要进行人机验证

    
    # print(response.text)
    # print(f"id_list_eles的长度是{len(id_list_eles)}")
    # for  id in id_list_eles:
    #     print(id)



    # for shop in zip(shop_list_ele):
    #     # i = shop.ele('@@class=product-card__status-label js-product-card__status-label')
    #     # print(f"得到的数据是{shop.text()}")
    #     print(shop.text)


