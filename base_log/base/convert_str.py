"""字符串的各种转换"""
import requests
import json
from time import sleep
from base.db.db_connection import create_record
from base.db.models import Remaker_User_Login_Log


def version_control(new_version,present_version) -> int:
    """对软件版本进行对比和控制，
    params:
        new_version: str, 最新版本号
        present_version: str, 当前版本号
    return:
        int, 1: 版本为最新版本
             2: 版本有小幅更新，可选更新
             3: 版本有重大更新，必须更新
    """
    if new_version == present_version:
        return 1
    
    parts1 = new_version.split('.')
    parts2 = present_version.split('.')

    # 确保至少有两个部分，否则无法比较
    if len(parts1) < 2 or len(parts2) < 2:
        raise ValueError("版本号格式错误，必须至少包含两个点（.）")

    # 提取大版本和小版本
    major1, minor1 = int(parts1[0]), int(parts1[1])
    major2, minor2 = int(parts2[0]), int(parts2[1])

    # 比较大版本
    if major1 != major2:
        return 3
    
    # 比较小版本
    if minor1 != minor2:
        return 2



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
    'Referer': 'https://qifu.baidu.com/home',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
}

def get_city_from_ip(ip, max_retries=10):
    """通过IP得到城市等信息"""
    for _ in range(max_retries):
        try:
            res = requests.get(f"https://qifu.baidu.com/ip/geo/v1/district?ip={ip}", headers=headers) #请求头可以不穿，但是为了安全起见，加上请求头
            # print(res.request.headers)
            res.raise_for_status()  # 如果HTTP状态不是200，抛出异常
            data_dict = json.loads(res.text)
            data = data_dict['data']
            return data
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            print(f"通过IP获取地址信息报错: {e}")
            sleep(1)  # 暂停1秒后重试
    print(f"超过最大重试次数({max_retries})，仍然无法获取地址信息")
    return None


def geit_ip_and_address():
    """得到IP地址和地理位置信息"""
    ip_str = requests.get("https://checkip.amazonaws.com").text.strip() #获取IP地址
    ip_info = get_city_from_ip(ip_str)
    ip_info["ip"] = ip_str
    # print(f"ip_info{ip_info},类型是{type(ip_info)}",)

    return ip_info


def insert_log_to_db(user_data: dict, log_status: str,failure_reason=None):
    """将日志数据插入数据库
    
    params:
        user_data: dict, 用户数据，包含 id, username, company_name
        log_status: str, 登录状态（例如 'success', 'failure', 'pending'）
        failure_reason: Optional[str], 登录失败的原因（如果有）
    
    return:
        None
    """
    user_id = user_data.get("id",None)
    username = user_data.get("username",None)
    company_name = user_data.get("company_name",None)
    status = log_status
    ip_info:dict = geit_ip_and_address() # 得到IP地址和地理位置信息
    isp = ip_info.get("isp",None) # 运营商
    ip_address = ip_info.get("ip",None) # IP地址
    prov = ip_info.get("prov",None) # 省份
    city = ip_info.get("city",None) # 城市
    district = ip_info.get("district",None) # 区县

    login_dict = {
        "user_id": user_id,
        "username": username,
        "company_name": company_name,
        "status": status,
        "ip_address": ip_address,
        "isp": isp,
        "prov": prov,
        "city": city,
        "district": district,
        "failure_reason": failure_reason,
    }
    # 插入登录日志 
    create_record(Remaker_User_Login_Log,login_dict)








if __name__ == "__main__":
    geit_ip_and_address()






