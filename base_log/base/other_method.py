"""用于保存一些其他方法"""
import base.global_var as gv
from ttkbootstrap import Text
def insert_text_windge(windge_dict:dict[Text:str]):
    """用于给指定的text控件插入文本
    param : windge_dict:需要插入的控件和文本的字典
    """
    for windge,text in windge_dict.items():
        windge.configure(state="normal")
        windge.delete("1.0", "end")
        windge.insert("1.0", text)
        windge.configure(state="disabled")


def update_treeview(tree, new_data: list[dict]):
    """更新指定的treeview控件的数据"""
    # 清空现有数据
    tree.delete(*tree.get_children())
    # 动态设置列名（从字典的键中提取）
    if new_data:  # 确保 new_data 不为空
        columns = list(new_data[0].keys())  # 获取字典的键作为列名
        # tree["columns"] = columns
    else:
        return
    # 插入新数据
    for row in new_data:
        values = [row.get(col, "") for col in columns]  # 按列名提取值
        tree.insert("", "end", values=values)


