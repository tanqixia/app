import subprocess

if __name__ == '__main__':
    choice = input("导出依赖请按:1, 安装依赖请按:2: ")
    if choice == "1":
        subprocess.run(["pip", "freeze", ">", "requirements.txt"], shell=True)
    elif choice == "2":
        subprocess.run(["pip", "install", "-r", "requirements.txt"], shell=True)
    else:
        print("输入错误！")