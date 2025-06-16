from DrissionPage.common import Settings
import csv
import os
from typing import Union, List, Set
from DrissionPage import Chromium,ChromiumOptions
import requests
import time
import base.global_var as gv
import threading
from typing import Optional, Union,Tuple, Literal
import json



Settings.set_language('zh_cn')  # 设置为中文时，填入'zh_cn'

def ger_cookies(page,url = "https://www.therealreal.com/")->dict:
    """获取网站的COOKIES"""
    # page.get(url)
    cookies_dict:dict = page.cookies(all_domains=False).as_dict()
    return cookies_dict

def set_cookies(page,cookies_dict:dict,domain= ".therealreal.com"):
    """设置COOKIES"""
    cookies_dict["domain"] = domain
    page.set.cookies(cookies_dict)

def write_lists_to_csv(urls: Union[List[str], Set[str]], names: List[str] = None, filename: str = 'link_data.csv',model = "a") -> None:
    """
    将数据写入CSV文件，支持两种模式：
    1. 同时写入商品名称和URL（当names参数提供时）
    2. 仅写入URL（当names参数为None时）
    
    参数:
        urls (List[str] or Set[str]): URL列表或集合
        names (List[str], optional): 商品名称列表，默认为None
        filename (str): CSV文件名，默认为'link_data.csv'
        model(str):  模式选择，默认为'a'追加模式
    """
    # 检查输入有效性
    if names is not None and len(names) != len(urls):
        raise ValueError("当提供names参数时，两个列表的长度必须相同")

    # 确定是否需要写表头
    write_header = not os.path.exists(filename)

    # 打开文件并写入数据
    with open(filename, model, newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # 写入表头（如果需要）
        if write_header:
            header = ['连接'] if names is None else ['商品名称', '连接']
            writer.writerow(header)
        
        # 写入数据行
        if names is not None:
            for name, url in zip(names, urls):
                writer.writerow([name, url])
        else:
            for url in urls:
                writer.writerow([url])



def read_urls_from_csv(filename='link_data.csv'):
    """
    从CSV文件中读取'连接'列并返回为集合
    
    参数:
        filename (str): CSV文件名，默认为'link_data.csv'
        
    返回:
        set: 包含所有唯一URL的集合
    """
    urls = set()
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # 检查表头是否存在
            if '连接' not in reader.fieldnames:
                raise ValueError("CSV文件中缺少'连接'列")
            
            # 读取URL列
            for row in reader:
                url = row['连接'].strip()  # 去除前后空格
                if url:  # 跳过空值
                    urls.add(url)
                    
    except FileNotFoundError:
        print(f"警告: 文件 {filename} 不存在")
        return set()
    
    return urls



def open_url_get_shop_url(page:Chromium,url_class: str,page_num = None) -> list:
    """打开指定商品类目的URL链接"""
    if page_num is  None:
        url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20"+url_class
    else:
        url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20"+url_class+"&page="+str(page_num)
    page.get(url)

def get_shop_urls(page:Chromium): # 后期可以改成直接传入页面ID，通过页面ID去获取，这样可以同时获取多个页面的链接
    """获取页面中的商品链接，记得先要打开商品类目页面，也就是open_url_get_shop_url函数"""
    # TODO 网页是静态的，后期可以考虑直接用requests获取
    shop_list_ele = page.ele("@@class=product-grid").eles('@@class=product-card__description product-card__link js-product-card-link')
    # TODO:这里可能涉及到多个网页的处理，后期修改代码
    print(f"列表有{len(shop_list_ele)}个商品")
    shop_list = []
    link_list = []
    for shop in shop_list_ele:
        # i = shop.ele('@@class=product-card__status-label js-product-card__status-label')
        # print(f"得到的数据是{shop.text()}")
        shop_list.append(shop.text)
        link_list.append(shop.link)
    return shop_list,link_list

    
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




def login(page,username: str, password: str) -> str:
    """以下是登录测试，后期再打包成函数"""
    start_time = time.time()
    # 或者可以监听https://www.therealreal.com/sessions网址的返回是否是200
    first_ele = "@@class=info-link underlined-link js-track-click-event@@tabindex=0@@text()=Member Sign In"#登录
    second_ele = "@@class=info-link underlined-link js-track-click-event@@tabindex=0@@text()=Member Sign Up" #注册
    status,idex_ele = fast_find_ele(page,first_ele,second_ele)
    if status is False:
        print("两个元素都未找到")
        return idex_ele # 这里返回的是空，表示未找到
    
    if idex_ele == "first":
        # 找到登录元素，点击进行登录
        print("找到登录元素，进行点击切换到登录页面")
        page.eles("t:a@@text()=Member Sign In")[1].click()
    else:
        # 找到注册元素，直接进行登录
        print("找到注册元素，直接进行登录")

    page.listen.start('https://www.therealreal.com/sessions')
    # 输入用户名
    page.ele("t:input@@id=user_email@@name=user[email]").input(username,clear=True)
    #  输入密码
    page.ele("@@placeholder=Password@@tabindex=0").input(password,clear=True)
    page.ele("t:input@@name=user[remember_me]@@tabindex=0").click() # 点击记住我

    page.eles("t:input@@class=button button--primary button--featured button--capped-full-width form-field__submit js-track-click-event")[1].click()
    # 等待加载完成
    # page.wait_for_load_complete()
    res = page.listen.wait()

    print(f"登录用时：{time.time()-start_time}秒")


def get_page_cont(page: Chromium):
    page_cont = page.ele("t:nav@@class=plp-header-controls__pagination ").text
    # print(f"得到的长度是：{page_cont.split("\n")}")
    return page_cont.split("\n")

def get_shop_save_csv():
    co1 = ChromiumOptions().set_local_port(9226).set_user_data_path('data1')
    page = Chromium(co1).latest_tab
    page.get('https://www.therealreal.com/')

    log_status = is_login(page) 
    if log_status is False:
        username = "vintedfr1@163.com"
        password = "Chen1122@"
        # 登录
        login(page,username,password)
        # 获取网站COOKIE
    cookies_dict = ger_cookies(page)
    # 设置网站COOKIE
    set_cookies(page,cookies_dict)
    # 打开商品搜索页面
    shop_list = ["betls","bags","jewelry"]
    for shop_class in shop_list:
        # 遍历每个页面
        open_url_get_shop_url(page,shop_class)
        shop_list,link_list = get_shop_urls(page)
        write_lists_to_csv(urls = link_list,names = shop_list,model="w")
        page_list = get_page_cont(page) # 得到页码列表
        # 如果分页大于1，则循环遍历其他页面，进行保存数据
        if len(page_list)  > 1:
            for page_num in page_list[1:]:
                open_url_get_shop_url(page,shop_class,page_num)
                shop_list,link_list = get_shop_urls(page)
                write_lists_to_csv(urls = link_list,names = shop_list)
    print("保存完成")


def start_get_shop_save_csv():
    t = threading.Thread(target=get_shop_save_csv,daemon=True)
    t.start()
    
def add_shop_car(good_id:str,session_id:str,query_id:str,cookie_dict:dict):
    """将商品加入购物车"""
    if not good_id:
        raise ValueError("good_id不能为空")
    if not session_id:
        raise ValueError("session_id不能为空")
    if not query_id:
        raise ValueError("query_id不能为空")
    if not cookie_dict:
        raise ValueError("cookie_dict不能为空")
    headers = gv.get_global_var("headers") #  获取请求头

    url = 'https://www.therealreal.com/cart/items'
    form_data = {
        'id': good_id,
        '_analytics_session_id': session_id,
        'return_product_id': '',
        'protection_product_id': '',
        'query_id': query_id
    }

    # 发送POST请求
    response = requests.post(url, data=form_data,headers=headers,cookies=cookie_dict)
    if response.status_code == 200:
        print("添加成功")

    elif response.status_code == 403:
        print("遇到人机验证")
    print(response.status_code)


def is_login(page: Chromium)->None|bool:
    """判断是否已经登录
    None:判断失败
    True:已经登录
    False:未登录
    """
    start_time = time.time()
    first_ele = "@class=js-header-first-look" #已经登录
    second_ele = "@class=head-utility-row__sign-up js-sign-up-link underlined-link" # 未登录
    status,idex_ele = fast_find_ele(page,first_ele,second_ele)
    print(f"判断登录用时：{time.time()-start_time}秒")
    if status is False:
        print("两个元素都未找到")
        return idex_ele # 这里返回的是空，表示未找到
    
    if idex_ele == "first":
        print("已经登录")
        return True
    else:
        print("未登录")
        return False





def fast_find_ele(page: Chromium,first_ele: str,second_ele: str,timeout: float = 200.0,interval: float = 0.1) -> Tuple[bool, Literal["first", "second"] | None] :
    """
    快速循环检测两个元素，返回最先找到的元素
    
    Args:
        page: Chromium页面对象
        first_ele: 第一个元素表达式，如 't:a@@text()=Member Sign In'
        second_ele: 第二个元素表达式，如 't:input@@id=user_email'
        timeout: 超时时间(秒)，默认20秒
        interval: 检查间隔(秒)，默认0.1秒
    
    Returns:
        str: 返回找到的元素表达式
        False: 超时未找到任何元素
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 检查第一个元素
        if page.ele(first_ele, timeout=0):
            return True,"first"
        
        # 检查第二个元素
        if page.ele(second_ele, timeout=0):
            return True,"second"
        
        time.sleep(interval)
    
    return False,None  # 超时未找到任何元素

def test_account():
    """测试过验证"""
    co1 = ChromiumOptions().set_local_port(9226).set_user_data_path('data1')
    page = Chromium(co1).latest_tab
    account_eles = page.eles("t:p@@text()=CLICK AND HOLD")[0]
    # page.actions.hold(account_eles)
    print(account_eles)
    
    

def open_url_in_tab(page, url):
    """在新标签页中打开URL"""
    global_url_set = gv.get_global_var('global_url_set')
    try:
        tab = page.new_tab(url)
        print(f'成功打开 URL: {tab}')
        # 可以在这里添加页面操作代码
    except Exception as e:
        print(f'打开 {url} 失败: {e}')


    while True:
        """循环刷新和获取页面商品链接"""
        try:
            _,link_list = get_shop_urls(page) # 得到页面中的商品链接
            url_set = set(link_list)
            add_url_set = find_difference(url_set,global_url_set) # 找出新增的url
            if add_url_set:
                """获取商品详细信息，并进行加购,这里需要进行多线程处理，需要创建等于add_url_set长度的线程池，然后进行批量处理"""
                return
            time.sleep(0.5) # 这里是页面刷新时间，后期可以通过UI界面进行配置，或者全局变量进行配置
            tab.refresh()
        except Exception as e:
            print(f'添加 URL: {url} 到全局变量失败: {e}')

def open_urls_concurrently(page, urls: list):
    """并发打开多个URL"""
    threads = []
    for url in urls:
        t = threading.Thread(target=open_url_in_tab, args=(page, url))
        t.start()
        threads.append(t)
        time.sleep(0.1)  # 稍微延迟一下，避免同时创建太多标签页



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
    
def find_url_add_car_ele(page,url):
    """
    功能：
    从链接中获取添加购物车信息
    
    参数：
        url: 链接
        
    返回：
        返回购物车的定位元素信息
    """
    url_ele = page.ele(f"@href={url}").parent(2)
    return url_ele


def car_ele_to_add_car_info(base_ele)->dict:
    """
    功能：
    从定位元素中获取添加购物车信息
    
    参数：
        url_ele: 定位元素
        
    返回：
        返回购物车的信息,打包成字典后进行返回
    """
    info_str = base_ele.ele("@class=obsess-box product-card__obsess js-obsess-box").attr("data-analytics-attributes")
    info_dict = json.loads(info_str)

    good_id  = str(info_dict["product_id"])
    queryID = info_dict["queryID"]

    _analytics_session_id_ele = base_ele.ele("@@class=obsession-container js-obsess-box-container").ele("t:button")
    session_id = _analytics_session_id_ele.attr("data-analytics-session-id")

    if  not session_id:
        print("session_id为空")
    if not good_id:
        print("good_id为空")
    if not queryID:
        print("queryID为空")

    return good_id,queryID,session_id


def find_url_add_car_info(page,url):
    """通过传入URL，获取商品ID，queryID，sessionID"""
    url_ele = find_url_add_car_ele(page,url)
    good_id,queryID,session_id = car_ele_to_add_car_info(url_ele) # 获取商品信息
    return good_id,queryID,session_id


if __name__ == '__main__':
    # test_account()
    co1 = ChromiumOptions().set_local_port(9226).set_user_data_path('data1')
    page = Chromium(co1).latest_tab

    cookie = ger_cookies(page)
    set_cookies(page,cookie)
    cookie = ger_cookies(page)

    url = "/products/men/bags/weekenders/chrome-hearts-leather-big-fleur-q38zg"
    css_ele  = "product-card__see-similar-items js-track-click-event"
    
    good_id,queryID,session_id = find_url_add_car_info(page,url)
    print(f"得到的加购信息是good_id：{good_id}，queryID：{queryID}，session_id:{session_id}")
    add_shop_car(good_id,queryID,session_id,cookie)











    # url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20bags"
    # headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}
    # url_data = requests.get(url,headers=headers)
    # print(url_data.text)