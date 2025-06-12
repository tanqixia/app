import configparser
import os
from base.global_var import get_global_var

class ConfigManager:
    def __init__(self, config_file=get_global_var("CONFIG_FILE") ):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

    def load(self, section, option=None, default=None):
        """
        从配置文件加载指定的section和option。
        如果传入option值，则返回指定option的值。
        如果没有传入option，则返回该section下的所有设置，作为字典形式返回。
        如果section或option不存在，返回默认值。
        """
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')

            # 检查section是否存在
            if self.config.has_section(section):
                # 如果option存在，则返回该option的值
                if option:
                    if self.config.has_option(section, option):
                        return self.config.get(section, option)
                    else:
                        return default
                else:
                    # 没有传入option时，返回该section下所有的键值对，作为字典返回
                    return dict(self.config.items(section))
        return default

    def save(self, section, option, value):
        """
        保存数据到配置文件的指定section和option，
        如果section不存在，则自动创建。
        如果配置设置不存在就创建并新建配置信息，返回True；
        如果配置设置存在，就检查配置项目是否存在，如果不存在就新建配置项目并返回True；
        如果配置项目也存在或者其他原因没有创建成功就返回False。
        """
        # 读取现有配置
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')

        # 检查section是否存在
        if not self.config.has_section(section):
            self.config.add_section(section)

        # 检查option是否存在
        if not self.config.has_option(section, option):
            try:
                self.config.set(section, option, value)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                return True
            except Exception as e:
                print(f"Error saving configuration: {e}")
                return False
        else:
            return False


    def delete(self, section, option):
        """
        删除指定section下的option，
        如果section或option不存在，则返回False；
        否则删除并返回True。
        """
        # 读取现有配置
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')

        # 检查section是否存在
        if not self.config.has_section(section):
            return False

        # 检查option是否存在
        if not self.config.has_option(section, option):
            return False

        # 删除option
        try:
            self.config.remove_option(section, option)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error deleting configuration: {e}")
            return False

    def get_options(self, section):
        """
        获取指定section的所有选项名称。
        如果section不存在，则返回空列表。
        """
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
            if self.config.has_section(section):
                return self.config.options(section)
        return []

    def get_options_as_dict(self, section_name):
    # 首先检查配置文件是否存在，并读取
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            print(f"配置文件 '{self.config_file}' 不存在")
            return []

        # 检查是否存在指定的 section
        if not self.config.has_section(section_name):
            print(f"Section '{section_name}' 不存在")
            return []

        options_list = []
        
        # 遍历 section 中的所有键值对
        for key, value in self.config.items(section_name):
            options_dict = {key: value}  # 将键值对组成字典
            options_list.append(options_dict)  # 添加到列表中
        
        return options_list  # 返回由字典组成的列表


    def update_options(self, section, option, value):

        """
        保存数据到配置文件的指定section和option，
        如果section不存在，则自动创建。
        无论配置项是否存在，都覆盖保存并返回True；
        如果保存失败，返回False。
        """
        # 读取现有配置
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')

        # 检查section是否存在，不存在就创建
        if not self.config.has_section(section):
            self.config.add_section(section)

        # 设置选项值，自动覆盖原值或创建新值
        try:
            self.config.set(section, option, str(value))  # 确保值为字符串
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False


if __name__ == "__main__":
    config_manager = ConfigManager("config.ini")

    # 保存选项，保存到 "Selections" 的 "options" 配置项中
    config_manager.save('Selections', 'options', '选项1,选项2')


    # 加载配置
    options = config_manager.load('Selections', 'options', default='无选项')
