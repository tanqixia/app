import ttkbootstrap as ttk
from ttkbootstrap import Entry,Text,Label
from base import global_var as gv
import threading
from ttkbootstrap.constants import *
from playsound import playsound
from typing import List, Dict, Any
from datetime import datetime,timedelta
from base.db.models import jushuitan_Merchant,app_info
from base.db.db_connection import create_record,read_records,query_data_que_none,update_record_with_query,bulk_insert_data
from base.convert_str import (version_control,insert_log_to_db,geit_ip_and_address
                         )
from base.other_method import insert_text_windge,update_treeview
import pandas as pd
# from .sql_auth import login,register_user
# from gui.message_box import show_info
# from db.queries import sqlalchemy_res_to_dict

def set_ke_yong(button:list[ttk.Button],state_str:str):
    """设置按钮为可用"""
    print(f"设置按钮为{state_str}")
    for i in button:
        i.configure(state=state_str)

def login_and_register(user_info,log_button,root,windge_dict):
    """注册和登录函数"""
    if gv.user_info_dict:
        """如果账号已经登录，则进行退出"""
        gv.set_global_var("user_info_dict",{}) # 修改全局用户信息变量为空
        gv.set_global_var("app_info_dict",{}) # 修改全局用户信息变量为空
        show_info("退出登录","退出登录成功")
        log_button.configure(text="登录/注册")
        user_info.configure(text="未登录")
        # print(f"账号已经退出{gv.user_info_dict}类型为{type(gv.user_info_dict)}")
        return
    
    user_dict = userlogin(root) 
    if user_dict:
        log_button.configure(text="退出")
        # print(f"账号已经登录{user_dict}类型为{type(user_dict)}")
        gv.set_global_var("user_info_dict",user_dict[0])# 把返回的列表中第一个字典赋值给全局变量user_info_dict
        # print(f"账户信息是{gv.user_info_dict}")
        if gv.user_info_dict["inform"]:
            show_info("通知",gv.user_info_dict["inform"])

        expiration_date = gv.user_info_dict["expiration_date"].strftime("%Y-%m-%d")

        # print(f"到期时间是{expiration_date}")
        user_time = compare_time(gv.user_info_dict["expiration_date"])
        if user_time == "已过期":
            user_info.configure(text=f"公司：{gv.user_info_dict["company_name"]},用户：{gv.user_info_dict["username"]}，到期时间：{expiration_date}\n状态【{user_time}】请联系管理员续费微信：zairuzhong002")
            return
        else:
            # print(f"没有过期")
            if gv.user_info_dict["status"] == 0:# 看账号是否可用 0代表不可用
                
                user_info.configure(text=f"公司：{gv.user_info_dict["company_name"]},用户：{gv.user_info_dict["username"]}，到期时间：{expiration_date}\n状态【账号已停用】")
                return
            if gv.user_info_dict["accessToken"] != None:
                accessToken_status = "已授权"
                # print("账号已授权")
            else:
                accessToken_status = "未授权"
                # print("账号未授权")
                # user_access_token = gv.user_info_dict["status"] 
            user_info.configure(text=f"公司：{gv.user_info_dict["company_name"]},用户：{gv.user_info_dict["username"]}，到期时间：{expiration_date}【{accessToken_status}】")

            app_info = app_version_info(gv.user_info_dict["authorized_app_ids"])
            # print(f"app_info是{app_info}")
            # print(f"appid信息是：{gv.user_info_dict["authorized_app_ids"]}")
            if not app_info: # 正确得到了应用信息
                show_error(text="加载配置时出错: app_info为空\n可能未授权或者已过期,请联系作者授权\n微信号：zairuzhong002")
                return
            
            # print(f"app_info是{app_info}")
            gv.set_global_var("app_info_dict",app_info[0])


            # 对版本信息和软件说明进行填写
            app_desc_text = windge_dict["app_desc_text"]
            version_log_text = windge_dict["version_log_text"]

            windge_insert_text_dict = {app_desc_text:app_info[0]["app_description"],version_log_text:app_info[0]["version_log"]}
            insert_text_windge(windge_insert_text_dict)

            new_version = gv.get_global_var("app_info_dict")["version"]
            present_version = gv.get_global_var("version")
            version_status = version_control(new_version,present_version)
            # print(f"版本对比结果是{version_status}")
            if version_status == 2:
                show_error(title="版本更新",text=f"版本有小幅更新，可选更新\n更新方式:{gv.get_global_var('app_info_dict')['up_version_address']}")
            elif version_status == 3:
                show_error(title="版本更新",text=f"版本有重大更新，必须更新\n更新方式:{gv.get_global_var('app_info_dict')['up_version_address']}")
                gv.set_global_var("user_info_dict",{}) # 修改全局用户信息变量为空
                gv.set_global_var("app_info_dict",{}) # 修改全局用户信息变量为空
                user_info.configure(text="已退出登录，版本重大更新，请更新后再登录使用")
                log_button.configure(text="登录/注册")
                return

        #     # button_list = [radio_question,radio_answer,shop_config_up]
        #     set_ke_yong(button_list,"normal")
        #     print(f"获得的表名字是{user_var_dict["assigned_table_name"]}")
            return 
    else:
        
        # user_info.configure(text="未登录")
        log_button.configure(text="登录/注册")
        # print("取消登录")
        # button_list = [radio_question,radio_answer,post_button]
        # set_ke_yong(button_list,"disabled")
        return




def validate_input(char):
    return char.isascii() # 只允许 ASCII 字符（包括英文）

def validate_numeric_input(new_value):
    """验证函数：仅允许输入数字"""
    return new_value.isdigit() or new_value == ""



class Two_InputDialog:
    """创建一个带两个文本输入框的弹窗"""
    def __init__(self, master, title, message:list, width=300, height=200):
        self.master = master
        self.title = title
        self.message0 = message[0]
        self.message1 = message[1]
        self.width = width
        self.height = height
        self.input_value0 = None
        self.input_value1 = None
        self.user_dict = {}

    def show(self):
        # 创建弹窗
        dialog = ttk.Toplevel(self.master)
        dialog.title(self.title)
        dialog.geometry(f"{self.width}x{self.height}")
        dialog.resizable(False, False)

        # 计算居中位置
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        dialog.geometry(f"+{x}+{y}")
        vcmd = (dialog.register(validate_input), '%S')
        tip1_label = ttk.Label(dialog, text=self.message0)
        tip1_label.pack(pady=5, padx=10, fill="x")
        # 输入框
        self.entry = ttk.Entry(dialog, bootstyle="primary", validate='key', validatecommand=vcmd)
        self.entry.pack(pady=5, padx=10, fill="x")

        tip2_label = ttk.Label(dialog, text=self.message1)
        tip2_label.pack(pady=5, padx=10, fill="x")
        self.entry2 = ttk.Entry(dialog, bootstyle="primary",show="*", validate='key', validatecommand=vcmd)
        self.entry2.pack(pady=5, padx=10, fill="x")


        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5)

        ok_button = ttk.Button(button_frame, text="登录", command=lambda: self.on_ok(dialog))
        ok_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="注册", command=lambda: self.on_register(dialog))
        cancel_button.pack(side="right", padx=5)

        # 等待用户操作
        dialog.grab_set()  # 使新窗口成为焦点窗口
        dialog.wait_window()  # 等待新窗口关闭
        return self.user_dict
    def on_ok(self, dialog):
        self.input_value0 = self.entry.get() # 账号
        self.input_value1 = self.entry2.get() # 密码

        # 写入登录日志
        if not self.input_value0 or not self.input_value1:
            show_info("登录失败:","账号或者密码不能为空")
            return

        res_str = login(self.input_value0,self.input_value1)
        # print(f"登录结果是{res_str}")
        if res_str:
            log_thread = threading.Thread(target=insert_log_to_db, args=(res_str[0], "success","登录成功"))
            log_thread.start()
            dialog.destroy()
            self.user_dict = sqlalchemy_res_to_dict(res_str)
        else:
            res_str = {"username": self.input_value0}
            log_thread = threading.Thread(target=insert_log_to_db, args=(res_str, "failure","账号或者密码错误"))
            log_thread.start()
            show_info("登录失败:","账号或密码错误")





        # dialog.destroy()

    def on_register(self, dialog):
        UserRegistration(dialog, "注册", ["请输入公司名称：","请输入用户名：", "请输入密码：非中文字符","请重复输入密码","手机号码\n(不进行验证,但后期用于找回和重置密码，请准确填写)"]).show()


class UserRegistration:
    """用户注册"""
    def __init__(self, master, title, message:list, width=330, height=500):
        self.master = master # 父窗口
        self.title = title # 标题
        self.message0 = message[0] # 公司名称
        self.message1 = message[1] # 用户名 1
        self.message2 = message[2] # 密码 2
        self.message3 = message[3] # 确认密码 2
        self.message4 = message[4] # 手机号码 3
        self.width = width
        self.height = height
        self.input_value0 = None # 用户名
        self.input_value1 = None # 密码

    def show(self):
        
        # 创建弹窗
        dialog = ttk.Toplevel(self.master)
        dialog.title(self.title)
        dialog.geometry(f"{self.width}x{self.height}")
        dialog.resizable(False, False)

        # 计算居中位置
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        dialog.geometry(f"+{x}+{y}")


        company_label = ttk.Label(dialog, text=self.message0)
        company_label.pack(pady=5, padx=10, fill="x")
        
        self.company_name = ttk.Entry(dialog, bootstyle="primary")
        self.company_name.pack(pady=5, padx=10, fill="x")

        user = ttk.Label(dialog, text=self.message1)    
        user.pack(pady=5, padx=10, fill="x")
        # 输入框
        vcmd = (dialog.register(validate_input), '%S')
        self.user_entry = ttk.Entry(dialog, bootstyle="primary", validate='key', validatecommand=vcmd) # 用户名输入框
        self.user_entry.pack(pady=5, padx=10, fill="x")

        password = ttk.Label(dialog, text=self.message2)
        password.pack(pady=5, padx=10, fill="x")
        
        self.password_entry = ttk.Entry(dialog, bootstyle="primary", show="*", validate='key', validatecommand=vcmd)
        self.password_entry.pack(pady=5, padx=10, fill="x")

        password_comtniu = ttk.Label(dialog, text=self.message3)
        password_comtniu.pack(pady=5, padx=10, fill="x")
        self.password_comtniu_entry = ttk.Entry(dialog, bootstyle="primary", show="*", validate='key', validatecommand=vcmd)
        self.password_comtniu_entry.pack(pady=5, padx=10, fill="x")

        phone_number = ttk.Label(dialog, text=self.message4)
        phone_number.pack(pady=5, padx=10, fill="x")
        number_vcmd = (dialog.register(validate_numeric_input), "%P")
        self.phone_number_entry = ttk.Entry(dialog, bootstyle="primary", validate='key', validatecommand=number_vcmd)
        self.phone_number_entry.pack(pady=5, padx=10, fill="x")

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5)

        ok_button = ttk.Button(button_frame, text="注册", command=lambda: self.on_ok(dialog))
        ok_button.pack(side="left", padx=20)

        cancel_button = ttk.Button(button_frame, text="取消", command=lambda: self.on_cancel(dialog))
        cancel_button.pack(side="right", padx=20)

        # 等待用户操作
        dialog.grab_set()  # 使新窗口成为焦点窗口
        dialog.wait_window()  # 等待新窗口关闭

  
    def on_ok(self, dialog):
        # 获取用户输入
        company_name = self.company_name.get()
        username = self.user_entry.get()  # 用户名
        password = self.password_entry.get()  # 密码
        confirm_password = self.password_comtniu_entry.get()  # 确认密码
        phone_number = self.phone_number_entry.get()  # 手机号码
        
        if not company_name or not username or not password or not confirm_password or not phone_number:
            show_info("提示", "请填写完整信息")
            return

        # 校验两次密码是否一致
        if password != confirm_password:
            show_info("提示", "两次密码不一致")
            return

        # 校验手机号长度
        if len(phone_number) != 11:
            show_info("提示", "手机号码不正确")
            return

        # 执行注册操作
        res_st = register_user(company_name,username, password, phone_number)
        if res_st == "注册成功":
            show_info("提示", "注册成功,请进行登录")
            dialog.destroy()
        else:
            show_info("提示", res_st)



    def on_cancel(self, dialog):
        self.input_value = None
        dialog.destroy()



def userlogin(master):
    """"用于处理登录和注册的窗口"""
    # 登录窗口
    log_dict = Two_InputDialog(master,"登录", ["用户名", "密码"]).show()
    return log_dict

def center_window(window, width, height):
    """将窗口居中显示"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def show_error(title="错误",text=""):
    """错误弹窗提示"""
    root = ttk.Toplevel()
    root.title(title)
    root.geometry("800x300")
    center_window(root, 800, 300)
    label = ttk.Text(root, font=("楷体", 15, "bold"),wrap='none')
    label.insert(1.0, text)
    label.configure(state='disabled')
    label.pack(pady=10)
    play_sound()
    root.grab_set()  # 使新窗口成为焦点窗口
    root.wait_window(root)  # 等待新窗口关闭

def show_info(tip,text):
    """信息弹窗提示"""
    root = ttk.Toplevel()
    root.title(tip)
    root.geometry("400x100")
    center_window(root, 400, 100)
    label = ttk.Label(root, text=text, font=("楷体", 15, "bold"))
    label.pack(pady=20)
    play_sound()
    root.grab_set()  # 使新窗口成为焦点窗口
    root.wait_window(root)  # 等待新窗口关闭

def show_info_with_buttons(tip, text, button1_text, button2_text,button3_text=None):
    """
    信息弹窗提示，包含两个按钮。点击按钮后返回按钮对应的值，并关闭窗口。
    只允许通过按钮点击关闭窗口，不允许通过右上角关闭。

    参数：
    tip: 窗口标题
    text: 提示文本
    button1_text: 第一个按钮文本
    button2_text: 第二个按钮文本

    返回：
    用户点击的按钮文本
    """
    play_sound() # 播放提示音
    def on_button_click(value):
        root.result = value  # 先存储点击的值
        root.destroy()  # 关闭窗口

    root = ttk.Toplevel()
    root.title(tip)
    root.geometry("800x100")
    center_window(root, 800, 300)
    root.result = None  # 先给一个默认返回值

    # 提示文本
    label = ttk.Text(root, font=("楷体", 15, "bold"),wrap='none',height=10)
    label.insert(1.0, text)
    label.config(state="disabled")  # 禁止编辑
    label.pack(pady=5)
    root.columnconfigure(0, weight=1)
    # 按钮1
    button1 = ttk.Button(root, text=button1_text, command=lambda: on_button_click(button1_text))
    button1.pack(side="right", padx=20, pady=5)

    # 按钮2
    button2 = ttk.Button(root, text=button2_text, command=lambda: on_button_click(button2_text),style=WARNING)
    button2.pack(side="right", padx=20, pady=5)

    if button3_text != None:
        button3 = ttk.Button(root, text=button3_text, command=lambda: on_button_click(button3_text),style=DANGER)
        button3.pack(side="right", padx=20, pady=5)
    
    root.grab_set()  # 使新窗口成为焦点窗口
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁止右上角关闭按钮
    root.wait_window(root)  # 等待新窗口关闭

    return root.result  # 返回用户点击的按钮文本

def play_sound(sound_file='src\Sound.wav'):
    threading.Thread(target=playsound, args=(sound_file,)).start()
def compare_time(input_time: datetime) -> str:
    """
    比较当前时间与传入时间的大小。

    参数:
        input_time: 传入的时间，类型为datetime。

    返回:
        字符串，表示当前时间与传入时间的比较结果。
    """
    current_time = datetime.now()

    if current_time > input_time:
        return "已过期"
    elif current_time < input_time:
        return "使用期限中"
    else:
        return "当前时间与传入时间相等"
    
def sqlalchemy_res_to_dict(records: List[Dict]) -> List[Dict]:
    """
    将 SQLAlchemy 查询返回的记录列表转换为普通字典列表。

    参数:
        records: 包含 SQLAlchemy 实例的字典列表。

    返回:
        普通字典列表，每条记录为字典格式。
    """
    return [{k: v for k, v in record.items() if not k.startswith('_')} for record in records]


def login(username: str, password: str) -> str:
    """
    登录功能，检查用户名和密码是否匹配。

    参数:
        username: 用户名
        password: 密码

    返回:
        登录结果信息。
    """
    # 查找是否存在此用户名和密码的用户记录
    filters = {
        'username': username,
        'password_hash': password  # 假设密码直接存储，实际应用中应使用哈希
    }
    selected_columns = ['id','company_name','username', 'phone_number','accessToken','authorized_app_ids','permissions','is_admin','expiration_date','inform','status'] #查询指定的列的数据
    records = query_data_que_none(jushuitan_Merchant, filters, selected_columns) #如果查找到数据就返回，查找不到就返回0的数据
    
    if records[0]["id"] != 0:
        """返回查询到的数据"""
        return records
    else:
        return False
    



def register_user(company_name,username: str, password: str, phone_number: str) -> str:
    """
    注册新用户。
    
    参数:
        company_name: 公司名称
        username: 用户名
        password: 密码
        phone_number: 手机号码
    
    返回:
        提示信息
    """
    # 查询用户名是否已存在
    existing_user = read_records(jushuitan_Merchant, filters={'username': username})
    if existing_user:
        return "账号存在，请重新输入账号"

    expiration_date = datetime.now() + timedelta(days=15)
    # 创建新用户记录
    ip_info = geit_ip_and_address()
    new_user_data = {
        'company_name': company_name,
        'username': username,
        'password_hash': password,
        'phone_number': phone_number,
        'expiration_date': expiration_date,  # 设置到期时间
        'remarks': None,  # 根据需要可以添加备注
        "ip_address":ip_info.get("ip",None)
    }
    
    result = create_record(jushuitan_Merchant, new_user_data)
    
    if result:
        return "注册成功"
    else:
        return "注册失败，请稍后重试"
    


def app_version_info(app_id: str):
    """
    获取通过APPID获取APP相关信息
    """
    # 查找是否存在此用户名和密码的用户记录
    # print(f"app_id: {app_id}")
    if not app_id:
        return False  # 如果 app_id 为 None 或空值，返回 False
    filters = {
        'app_id': app_id
    }
    selected_columns = ['id','app_id','app_name', 'app_key','app_secret','update_time','status','version','version_log','app_description','up_version_address'] #查询指定的列的数据
    records = query_data_que_none(app_info, filters, selected_columns) #如果查找到数据就返回，查找不到就返回0的数据
    
    if records[0]["id"] != 0:
        """返回查询到的数据"""
        return records
    else:
        return False




def count_visible_lines(text_widget: Text) -> int:
    """获取 Text 控件中的可见行数（忽略纯空行）。"""
    return sum(1 for line in text_widget.get("1.0", "end-1c").splitlines() if line.strip())


def reset_progress_label(status_label:Label,count_munber:int,set_count_munber:int):
    """设置进度条文本
    param:
    status_label:进度条文本控件
    count_munber:总数量
    set_count_munber:当前进度
    """
    status_label.config(text=f"[{set_count_munber}/{count_munber}]")


def query_company_user():
    """显示公司用户
    params:
        company_name: str, 公司名称
    return:
        None
    """
    company_name = gv.get_global_var("user_info_dict").get("company_name",None)
    if not company_name:
        show_info("提示","请先登录")
        return
    if gv.get_global_var("user_info_dict").get("is_admin",None) != "1":
        show_info("提示","非公司管理员不能执行此操作")
        return

    query_dict = {"company_name":company_name}
    selected_columns = ["id","company_name","username","accessToken"]
    user_list_dict:list[dict] = query_data_que_none(jushuitan_Merchant,query_dict,selected_columns)
    # print(f"公司用户列表：{user_list_dict}")
    return user_list_dict

def show_company_user(windge: ttk.Treeview):
    user_list_dict = query_company_user()
    if not user_list_dict: return # 如果没有数据，则返回
    for user_dict in user_list_dict:
        if user_dict.get("accessToken",None):
            user_dict["accessToken"] = "已授权"
        else:
            user_dict["accessToken"] = "未授权"
    update_treeview(windge,user_list_dict)

def on_select(event, treeview: ttk.Treeview):
    """获取选中的行数据，并将表头和值组合成字典"""
    # 获取选中的行
    selected_item = treeview.selection()
    if selected_item:  # 确保有选中行
        # 获取表头（列名）
        columns = treeview["columns"]
        
        # 获取选中行的值
        item_values = treeview.item(selected_item, "values")
        
        # 将表头和值组合成字典
        selected_dict = dict(zip(columns, item_values))
        gv.set_global_var("user_slelect_dict",selected_dict)

def config_user_permissions(windge: ttk.Treeview, accredit: str):
    """配置用户权限
    params:
        windge: ttk.Treeview, 用于显示用户信息的树形控件
        accredit: str, 状态（例如 'accredit', 'unaccredit'）
    return:
        None
    """
    # 获取用户信息
    user_data = gv.get_global_var("user_slelect_dict")
    id = user_data.get("ID", None)
    company_name = user_data.get("公司名称", None)
    username = user_data.get("用户名", None)

    # 如果没有选择用户，提示并返回
    if not all([id, company_name, username]):
        show_info("提示", "请先选择用户")
        return

    # 生成查询条件
    data_before = {"id": int(id), "company_name": company_name, "username": username}

    # 根据不同的授权状态执行操作
    if accredit == "accredit":
        # 对用户进行授权
        authorized_app_ids = gv.get_global_var("user_info_dict").get("authorized_app_ids", None)
        accessToken = gv.get_global_var("user_info_dict").get("accessToken", None)
        data_after = {"authorized_app_ids": authorized_app_ids, "accessToken": accessToken}

    elif accredit == "unaccredit":
        # 对用户进行取消授权
        data_after = {"authorized_app_ids": None, "accessToken": None}

    else:
        # 如果操作状态不合法
        show_info("提示", "操作失败")
        return

    # 更新记录

    update_record_with_query(jushuitan_Merchant, data_before, data_after)

    # 刷新界面显示
    show_company_user(windge)



def get_user_info(info: list):
    """
    从全局变量 user_info_dict 中提取指定字段，并返回 Pandas DataFrame。

    :param info: 需要提取的键列表
    :return: Pandas DataFrame 或 None（如果用户未登录）
    """
    # 获取用户信息字典
    user_info_dict = gv.get_global_var("user_info_dict")
    
    if not user_info_dict:
        show_info("提示", "请先登录")
        return None
    
    # 提取所需字段并构造新字典
    extracted_data = {key: user_info_dict.get(key, None) for key in info}

    # 转换为 DataFrame
    df = pd.DataFrame([extracted_data])

    return df



if __name__ == "__main__":

    print("请在主界面运行")