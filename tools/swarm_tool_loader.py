import os
import logging
from importlib.util import spec_from_file_location, module_from_spec

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def dynamic_import(tool_file, module_name):
    """根据路径动态导入模块"""
    spec = spec_from_file_location(module_name, tool_file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SwarmToolLoader:
    def __init__(self):
        """初始化工具加载器"""
        self.tools_directory = os.path.join(os.path.dirname(__file__), "agent_tool")
        self.tools = []  # 存储已加载的工具函数
        self.tool_data = {}  # 存储工具描述信息

    def load_tools(self):
        """遍历工具目录并加载每个工具模块"""
        for folder_name in os.listdir(self.tools_directory):
            folder_path = os.path.join(self.tools_directory, folder_name)

            if os.path.isdir(folder_path):
                tool_file = os.path.join(folder_path, "tool.py")
                if os.path.exists(tool_file):
                    try:
                        # 动态导入模块
                        module_name = f"agent_tool.{folder_name}.tool"
                        tool_module = dynamic_import(tool_file, module_name)

                        # 获取 register_tool 函数
                        tool_function = getattr(tool_module, 'register_tool', None)

                        if tool_function:
                            # 调用 register_tool 获取工具字典
                            tool_info = tool_function()

                            # 提取工具的函数和描述信息
                            tool_func = tool_info["agent_tool"]  # 确保工具的执行函数
                            tool_name = tool_info["name"]  # 工具名称
                            tool_description = tool_info["description"]  # 工具描述

                            # 添加工具到工具列表
                            structured_tool = {
                                'name': tool_name,
                                'func': tool_func,
                                'description': tool_description
                            }
                            self.tools.append(structured_tool)

                            logging.info(f"成功加载工具: {tool_name}，描述信息: {tool_description}")
                        else:
                            logging.warning(f"未找到 register_tool 函数：{folder_name}")

                    except Exception as e:
                        logging.error(f"加载工具 {folder_name} 时发生错误: {e}")

    def get_tools(self) -> list:
        """返回已加载的工具函数列表"""
        # 直接返回工具的实际函数，而不是 StructuredTool 对象
        return [tool['func'].func for tool in self.tools]  # 提取实际的可调用函数

    def get_tool_data(self) -> dict:
        """返回工具描述信息"""
        return {tool['name']: tool['description'] for tool in self.tools}
