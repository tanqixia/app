from datetime import datetime
import os
current_date = datetime.now().date().strftime('%Y-%m-%d')
filename = f"{current_date}.txt"
directory = "./logs"  # 假设你希望在./logs目录下创建文件
os.makedirs(directory, exist_ok=True) 
file_path = os.path.join("./logs", filename)

def log_to_text(text):
    with open(file_path, 'a',encoding='utf-8') as logfile:
        logfile.write(f"【{datetime.now().replace(microsecond=0)}记录内容为：{text}】\n")
        print(text)
