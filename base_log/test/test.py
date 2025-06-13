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
cookie = "domain=.therealreal.com;_pxhd=ujQYRtl1lxrl5kz23n/qzR-7eIQqxTUidT/HyjDEFWptYrXe6Uz41mEGERb1us7/42v2HW94WXlYMnhB35nm4A==:2x3QpIrl9M6hEvCJsrJm-EcLxJkYENciFhXQ8xpS43aLsbDYjsJk6Pxf908EdiP/Gpp-9ICko7eG-yC5RnE9dDSLQ8zlL-BecFhdDBE-lHY=; __ssid=7790e7333368d740a6ae917f9825162; ajs_anonymous_id=2a0fe5f7-cdca-4ca7-889b-ba107da67416; __adroll_fpc=2b3ee8f03e06ade8d3de4562652f5770-1749742494232; _fbp=fb.1.1749742494418.763437766250198331; _ga=GA1.1.1923684175.1749742495; _evga_0388={%22uuid%22:%2239c8ef5bb4d363fe%22}; _sfid_d56d={%22anonymousId%22:%2239c8ef5bb4d363fe%22%2C%22consents%22:[{%22consent%22:{%22provider%22:%22Ketch%22%2C%22purpose%22:%22Personalization%22%2C%22status%22:%22Opt%20Out%22}%2C%22lastUpdateTime%22:%222025-06-12T15:34:55.194Z%22%2C%22lastSentTime%22:%222025-06-12T15:34:55.195Z%22}]}; _li_dcdm_c=.therealreal.com; _lc2_fpi=a2e7823d27c0--01jxjcf9ffd7f2w3g36rss73xe; _lc2_fpi_js=a2e7823d27c0--01jxjcf9ffd7f2w3g36rss73xe; pxcts=cfe51bb1-47a2-11f0-9ff4-6d5bbd625e23; _pxvid=c6307b80-47a2-11f0-8e8e-209c3c068e2f; _clck=17zls3l%7C2%7Cfwp%7C0%7C1989; _gcl_au=1.1.448495202.1749742494.931392795.1749742509.1749742524; last_logged_in_identifiers=39274561|2169265e-e29c-45b2-9b86-05c510f2ddfd; registered=true; nearby_stores=WzM3XQ; ajs_user_id=39274561; _ga_65FCHSL71W=GS2.1.s1749742494$o1$g1$t1749742526$j28$l0$h0; _ga_VPSCJ11BBF=GS2.1.s1749742495$o1$g1$t1749742526$j29$l0$h332106753; _pin_unauth=dWlkPU9UYzVNVGM0TTJZdE1EVmtOeTAwTWpZNUxUazNZVEF0WVRGa01URXlPVE5sTVRRMQ; _uetsid=cddf1c7047a211f0ac4d61da04e4556d; _uetvid=cddf261047a211f0864b6f2fd4ad7439; _swb=6354870e-91e8-4776-b46c-4226c425cc12; _clsk=1hrsw06%7C1749742531043%7C2%7C1%7Cn.clarity.ms%2Fcollect; _swb_consent_=eyJjb2xsZWN0ZWRBdCI6MTc0OTc0MjUzMSwiZW52aXJvbm1lbnRDb2RlIjoicHJvZHVjdGlvbiIsImlkZW50aXRpZXMiOnsiX3NlZ21lbnRBbm9ueW1vdXNJRCI6IjJhMGZlNWY3LWNkY2EtNGNhNy04ODliLWJhMTA3ZGE2NzQxNiIsIl9zZWdtZW50VXNlcklEIjoiMzkyNzQ1NjEiLCJzd2JfdGhlcmVhbHJlYWxfY29tIjoiNjM1NDg3MGUtOTFlOC00Nzc2LWI0NmMtNDIyNmM0MjVjYzEyIn0sImp1cmlzZGljdGlvbkNvZGUiOiJjcHJhIiwicHJvcGVydHlDb2RlIjoidGhlcmVhbHJlYWxfY29tIiwicHVycG9zZXMiOnsiYW5hbHl0aWNzIjp7ImFsbG93ZWQiOiJmYWxzZSIsImxlZ2FsQmFzaXNDb2RlIjoiY29uc2VudF9vcHRvdXQifSwiYmVoYXZpb3JhbF9hZHZlcnRpc2luZyI6eyJhbGxvd2VkIjoiZmFsc2UiLCJsZWdhbEJhc2lzQ29kZSI6ImNvbnNlbnRfb3B0b3V0In0sImVzc2VudGlhbF9zZXJ2aWNlcyI6eyJhbGxvd2VkIjoidHJ1ZSIsImxlZ2FsQmFzaXNDb2RlIjoiZGlzY2xvc3VyZSJ9fX0%3D; _ketch_consent_v1_=eyJhbmFseXRpY3MiOnsic3RhdHVzIjoiZGVuaWVkIiwiY2Fub25pY2FsUHVycG9zZXMiOlsiYW5hbHl0aWNzIl19LCJiZWhhdmlvcmFsX2FkdmVydGlzaW5nIjp7InN0YXR1cyI6ImRlbmllZCIsImNhbm9uaWNhbFB1cnBvc2VzIjpbImJlaGF2aW9yYWxfYWR2ZXJ0aXNpbmciXX0sImVzc2VudGlhbF9zZXJ2aWNlcyI6eyJzdGF0dXMiOiJncmFudGVkIiwiY2Fub25pY2FsUHVycG9zZXMiOlsiZXNzZW50aWFsX3NlcnZpY2VzIl19fQ%3D%3D; _dd_s=rum=0&expire=1749743610965; __ar_v4=OF3FCM4OFZG4TLJK7JEAAV%3A20250612%3A3%7CBBODAYSHJJDRLP6HI5M56H%3A20250612%3A3%7CWEGDQEKGEZBIVDDMGIEHGG%3A20250612%3A3; _session_id=c3ltZXNmNTlJTXl3UXFabEQwZHBMOFBVNGE3WTBHbEVlanJ4eHM3TE1lUks0eG5nQTVtVTQxNWZBY1pmZ243aEZEQWx0UG5kUitGNERmY1p6TU9CVjU0ZzAvMDMwU1RjWEVqRHZkMjRhM0pJT1ZLQllLZm5NNEIrY3NSM0hvTFlSUndhVzM3UFJPT2xOaVpkRE9vcTVsMjFvbWVxdGxaenJTeVFqeTJsbTRHV0dNR2QwekVRR2RmaHV4ams1eDJJODdya3JjemcvL3FuRkVnU2pqR2J4UE1PL2JFMnQ3QmhCd0VhTFArSEZFOWlaSTBSbEpsRmRQelhqVFl3Vy9nTk9EdThwRmIxclFEWm9McTRzWjFmeXlZMzIvd2czQWM1bTVPK3Rha3BrTldiZVVsR005QU1EeVd2L3pWakxCU1NxSmhmU3EzTE55blI1Z3IydGdXT0tKMkRHbDh6Uzl1bExnekdDdHZVdnFsUlFyZGtudkNUVmUxTWo4TElYT21EenFOY2hwMk9YZXhReXU5SWNka0ZpV0JUZGY2dGMxT2ZlSEtVV0JZZlk5Y21MWUcwdWZrODhDZitZYVdrUUNqRnh6N0ZERE9JS0o4UytEU1UySlVDeUY0U0pENkZ3bklwZ0YzK21MR0JqYjR1ZGVSTUxPVGlMUC9EWUFMcHpNbVdYNG1JVmRBN0NzZFFBeXU2dFdCRDhxc2tESit2bmt5eTZpOUFrT1d1ZUp1czFpYmMrQjlaZUFoZFJ1bU8reFYvVHBRODlEMTBNcGVNcDRrS3gycXhnWGJrS3cwZVVndkVBb1JaSGlHRTU3NUdEalRFN1pJdkhjTmhTQ00zZjNyUEtwSkhiN3M0K1gva2dMMUIydVA2dGNNOVgxWjI2bnBwRnU0cDdtSmVOZ3pWZFNzbzBSNXJPOWhQS2xQclJpNVJXUFFJcWNLbkVUSlNleERYT0xZeVJPZkRRM0hQcUFCQ1ZqMklNRVZMOG13YUxSSkduakxOSlZibTRBRDBHRUhJV25sdjhNVEd5TWNHRVBGejhoWVhaL1k1SldteERuMThxdDQxNTRkdDg2U2M2QXBPTnZnYkVjSXZpemlqSjJTTTU0eHhURnRaVFl4c1JzYUdoVm9YVE9oeHI4ZktDOW1SREpnMDJsTDQ4OEp4Z1FSWWxBWXViL3h6RFJiOWxFdVRBbDYxLzJwcjlmWG9CQnFNNHBHRWtvSWRDVmpGdGorQTBZT3RROE9oRk9lNVA2d2NmSkh6VkdhaVdySlZxdm1QdEJyckorU0Z2MW9IeWdmT0lvR0ovNEhBZUNlbHFiZHVvLy9tL1Iwei8wdnRKWkpjb0JJa0U2c3RaVm1lai81ZUM5SGszVWgzWUZNaDZJQmlKbmJETHVvTERZR09lalJtMDhjMSs5TmNzWXo0S1IxUVdzOGlzcjU3bUhBTjZ0MXU5MVU5M0Ryd1hhNVVyL3U2Tkt5S3IrOUx2eVh0eGNKakZmTXMvUytHMGw2c3JOK2czbkNCN1IvczBHQ0NnY0hJeFplQUh1cDQ0QmpuNEdPZ0NKVFhMRjlFaU02bm5UMHl6ZGRqUHprOS9yRFYxMGdyQXF5MXpZaFBrV1FQeXNqN0R1ZjNRZmlGdTJOZXRhdzd0dGxLN0JuMWNWM3ljS3hZK1F0SDdwaThZUUl4eGEydEt0T3FVU3dxOFpGM1F6OXA4OHRzZVlTRUtsSXdPdFFtbk5Nd3l6cjEwTzhWOGZqRlpvVDArMW8wVStsWUhKdWxPcGJ0dnRhNTVjYXp5QlRheE40aGJGNmFIRStibHpxVldQVVlzekFnZC9mQ0dzck1KbmcrUTZ2aVEraXZZY3VNVitYRzRpMHg4dktkeHdqamplODZBRDVsc3NqVVpPZlhUM1d5b0FadnUydW1UZUs2YzY5TGt0SitOM1M0cFZJdUZpZ1VyQVF1OU9rZ0tZem96MjR4NlhCT3FPZlI1UXhRNUR3ZUpYOWpRZXIraFJjNFhxZlpRVWloaXh2SG1JZjlybHgxSVVTWnVZK09keEI0WjNQdTAyenFuNEZnZGF1d0F5MndTdz09LS1HV0JWdExrbWMxTVVkMUMrQ2dTai93PT0%3D--31da583c6cf67a61ef9a20111150f3a312f3aee4; _pxde=a6215b8a201ed1af0860c45ca5a4e3ae3e75362bd06d84b5b2184f3f545e846e:eyJ0aW1lc3RhbXAiOjE3NDk3NDI3MjUyNDksImZfa2IiOjB9"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}

# jewelry



cookie_dict = parse_cookie_string(cookie)





if __name__ == '__main__':

    bags = "bags"
    co1 = ChromiumOptions().set_local_port(9222)
    page = Chromium(co1).latest_tab
    # 这里可能会出现验证
    # page.set.cookies(cookie)
    # open_url_get_shop_url(page,bags)

    # shop_list,link_list = get_shop_urls(page)

    # # 将数据写入CSV文件
    # write_lists_to_csv(urls = link_list,names = shop_list,)
    # # 读取CSV文件中连接列，并且返回集合，这里在多进程运行的时候也是这样读取的

    # # 以上为商品链接保存完毕，接下来的任务是需要再多进程中运行
    
    # url_set = read_urls_from_csv()
    # 如果新探索到的链接不在集合中，则返回链接，后期通过代码进行加购，但是有可能需要返回商品ID，所以后期再保存或者获取的时候，需要得到商品ID
    


    # 请求的网址是：https://www.therealreal.com/cart/items
    # ID = data-product-id，属性，_analytics_session_i=data-analytics-session-id属性，另外两个参数可以为空，其中query_id在data-analytics-attributes列表中的query_ID
    # 表单数据是：id=41953892&_analytics_session_id=1749787048157&return_product_id=&protection_product_id=&query_id=e17b491e5aa8a9015b1e2925d61f6ea8

    shop_list = page.ele("@@class=product-grid")
    # shop_list_ele = shop_list.eles('@@class=product-card__description product-card__link js-product-card-link') # 可以获取商品名称和连接，也就是.text和.link

    id_list_eles = shop_list.eles('@@class=product-card-wrapper js-product-card-wrapper')
    start_time = time.time()
    for i_ele in id_list_eles:

        # print(f"i是{i}")
        base_ele = i_ele.ele("@@class=product-card js-plp-product-card ") # 可以获取id，也就是.attr("id")
        # 获得ID属性
        id  = base_ele.attr("data-product-id")
        # print(f"id是{id}")
        # 获得_analytics_session_id属性
        _analytics_session_id_ele = base_ele.ele("@@class=obsession-container js-obsess-box-container").ele("t:button")
        _analytics_session_id = _analytics_session_id_ele.attr("data-analytics-session-id")
        # print(f"_analytics_session_id的值是{_analytics_session_id}")
        # 获得query_id
        dict_str = _analytics_session_id_ele.attr("data-analytics-attributes")
        query_id = json.loads(dict_str)["queryID"]
        print(f"query_id的值是{query_id},类型是{type(query_id)}")


    print(f"耗时是{time.time()-start_time}")




    import requests

    url = 'https://www.therealreal.com/cart/items'
    form_data = {
        'id': '43822113',
        '_analytics_session_id': '1749787048157',
        'return_product_id': '',
        'protection_product_id': '',
        'query_id': '85c042f65b8ff0ea3d56c3950bab43ef'
    }

    # 发送POST请求
    response = requests.post(url, data=form_data,headers=headers,cookies=cookie_dict)

    print(response.status_code)
    # print(response.text)
    # print(f"id_list_eles的长度是{len(id_list_eles)}")
    # for  id in id_list_eles:
    #     print(id)



    # for shop in zip(shop_list_ele):
    #     # i = shop.ele('@@class=product-card__status-label js-product-card__status-label')
    #     # print(f"得到的数据是{shop.text()}")
    #     print(shop.text)