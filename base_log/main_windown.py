"""这里是写主GUI界面的地方"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import base.global_var as gv 
from base.gui_method import login_and_register,set_ke_yong
import ast
from base.ConfigManagerINI import ConfigManager
from main_method import start_get_shop_save_csv
config = ConfigManager()



def main_gui():
    title = "therealreal加购软件"
    root = ttk.Window(title=title,
                    themename="superhero",
                    size=(1500, 720),
                    alpha=1
                    )
    
    root.iconbitmap('base_log/src/DevHome.ico')
    root.place_window_center()
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill=BOTH, expand=True)
    #新建标签页
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="主界面")
# region 登录注册组件
    # top1_frame = ttk.Frame(tab1)
    # top1_frame.grid(row=0, column=0, sticky=E,columnspan=2)


    # # 左边的空间占据所有可用空间
    # # spacer = ttk.Frame(top1_frame)
    # # spacer.grid(row=0, column=0, sticky=(W, E))
    
  
    # # 用户信息显示
    # user_info = ttk.Label(top1_frame, text="未登录", style=SUCCESS, font=("楷体", 14, "bold"))
    # user_info.grid(row=0, column=0, padx=10, pady=3, sticky=E)  # 注意这里改为sticky=W，因为紧挨着log_button右边

    # # 登录/注册按钮
    # log_button = ttk.Button(top1_frame, text="登录/注册", command=lambda: login_and_register(user_info, log_button, root,tab2_text_windge_dict))
    # log_button.grid(row=0, column=1, padx=10, pady=3, sticky=W)
    
# endregion
    
    # 以下为设置界面
    confei_frame = ttk.LabelFrame(tab1,text="基础设置",style=WARNING)
    confei_frame.grid(row=1, column=0, sticky=N)

    choice_model_label = ttk.Label(confei_frame, text="预登记商品：", font=("楷体", 12, "bold"))
    choice_model_label.grid(row=0, column=0, padx=10, pady=3, sticky=W)

    start_button = ttk.Button(confei_frame, text="开始采集商品", command=lambda: start_get_shop_save_csv())
    start_button.grid(row=0, column=1, padx=10, pady=3, sticky=W)
    
    
    
    
    message_frame = ttk.LabelFrame(tab1,text="通知栏",style=WARNING)
    message_frame.grid(row=2, column=0, sticky=W)
    
    message_text = ttk.Text(message_frame, width=45,font=("楷体", 12, "bold"),height=11)
    message_text.insert(1.0, "这里会显示一些软件通知或消息。\n")
    message_text.grid(row=0, column=0, padx=10, pady=3, sticky=W)
    gv.set_global_var("tip_widget",message_text)
    

    

    
    



                    
    
    
    # button_list = [enter_input_button,save_button,clear_button,open_zuhe_csv_button,strat_button,open_csv_button] # 主要按钮的列表
    # set_ke_yong(button_list,"disabled")
     # 以下是第二个标签页
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="软件说明")
    
    app_desc_frame = ttk.LabelFrame(tab2,text="软件使用说明",style=WARNING)
    app_desc_frame.grid(row=1, column=0, sticky=(N, S, E, W))
    app_desc_text = ttk.Text(app_desc_frame, font=("宋体", 11)) # 软件说明
    app_desc_text.grid(row=0, column=0, padx=10, pady=3, sticky=(N, S, E, W))
    app_desc_text.insert("1.0","请登录后查看相关信息:如无法登录请联系微信：zairuzhong002")
    app_desc_text.configure(state=DISABLED)
    
    
    version_log_frame = ttk.LabelFrame(tab2,text="版本日志",style=WARNING)
    version_log_frame.grid(row=1, column=1, sticky=(N, S, E, W))

    version_log_text = ttk.Text(version_log_frame, font=("宋体", 11),state=DISABLED)
    version_log_text.grid(row=0, column=0, padx=10, pady=3, sticky=(N, S, E, W))
    
    tab2_text_windge_dict = {"app_desc_text":app_desc_text,"version_log_text":version_log_text}
    
    
    root.grid_columnconfigure(0, weight=1)
    tab1.grid_columnconfigure(0, weight=1)
    
    root.mainloop()
    
    
    
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main_gui()