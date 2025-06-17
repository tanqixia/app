"""全局变量"""
user_info_dict = {} # 用于保存用户信息，后期要设置字典默认值，防止后期拉取字段出错
app_info_dict = {} # 应用信息
CONFIG_FILE = 'base/config.ini'
version = "1.0.25.4.17"

user_cookies = {}

global_url_set = set()# 全局变量中存储所有链接

class_base_url = "https://www.therealreal.com/products?keywords=chrome%20hearts%20"
# https://www.therealreal.com/
# 账号：r173226793@gmail.com
# 密码：Richie123..

# 品牌名是 = chrome hearts
shop_class = ["bags","betls","jewelry"]


# 测试加购的商品
# Chrome Hearts Double Floral Cross Ring,https://www.therealreal.com/products/jewelry/rings/band/chrome-hearts-double-floral-cross-ring-q5u2t

# css_ele  = "product-card__see-similar-items js-track-click-event" 这个元素为获取可售卖的商品

tip_widget = None # 主界面用于显示通知的控件

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    "referer":"https://www.therealreal.com/",
    }



# 验证信息


def get_global_var(var_name):
    """获取全局变量的值"""
    if var_name in globals():
        # print(f"全局变量的值是'{globals()[var_name]}' ")
        return globals()[var_name]
    else:
        raise NameError(f"Variable '{var_name}' not found")
    
def set_global_var(var_name,value):
    """修改全局变量的值"""
    if var_name in globals():
        globals()[var_name] = value
        # print(f"全局变量{var_name}的值是'{globals()[var_name]}")
    else:
        raise NameError(f"Variable '{var_name}' not found")
    
def update_global_dict_value(var_name, key, value):
    """更新指定字典变量中的某个键的值"""
    if var_name in globals():
        global_dict = globals()[var_name]
        if isinstance(global_dict, dict):
            global_dict[key] = value  # 更新指定键的值
            globals()[var_name] = global_dict  # 将更新后的字典重新存回全局变量
        else:
            raise ValueError(f"{var_name} is not a dictionary.")
    else:
        raise NameError(f"Variable '{var_name}' not found")

def print_all_globals():
    """打印全局变量"""
    for key, value in globals().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    print_all_globals()