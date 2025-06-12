from main_windown import main_gui

if __name__ == '__main__':
    # 如果软件中使用了多线程，那么就必须导入下面两个模块
    import multiprocessing 
    multiprocessing.freeze_support()
    main_gui()