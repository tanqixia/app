from DrissionPage.common import Settings
import csv
import os
from typing import Union, List, Set
from DrissionPage import Chromium,ChromiumOptions
import requests
import time
import base.global_var as gv



Settings.set_language('zh_cn')  # 设置为中文时，填入'zh_cn'

def ger_cookies(page,url = "https://www.therealreal.com/")->dict:
    """获取网站的COOKIES"""
    page.get(url)
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

    





def login(page,username: str, password: str) -> str:
    """以下是登录测试，后期再打包成函数"""
    start_time = time.time()
    page.listen.start('https://www.therealreal.com/sessions')
    try:
        page.eles("t:a@@text()=Member Sign In")[1].click()
    except:pass
    # 输入用户名
    page.ele("t:input@@id=user_email@@name=user[email]").input(username,clear=True)
    #  输入密码
    page.ele("#^=user_passwor@@tabindex='0'")[-1].input(password,clear=True)
    page.eles("t:input@@class=button button--primary button--featured button--capped-full-width form-field__submit js-track-click-event")[1].click()
    # 等待加载完成
    # page.wait_for_load_complete()
    # 或者可以监听https://www.therealreal.com/sessions网址的返回是否是200
    
    res = page.listen.wait()
    print(res)
    print(f"登录用时：{time.time()-start_time}秒")


def get_page_cont(page: Chromium):
    page_cont = page.ele("t:nav@@class=plp-header-controls__pagination ").text
    # print(f"得到的长度是：{page_cont.split("\n")}")
    return page_cont.split("\n")

def get_shop_save_csv():
    co1 = ChromiumOptions().set_local_port(9226).set_user_data_path('data1')
    page = Chromium(co1).latest_tab
    page.get('https://www.therealreal.com/')
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

if __name__ == '__main__':
    get_shop_save_csv()










    # url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20bags"
    # headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}
    # url_data = requests.get(url,headers=headers)
    # print(url_data.text)