# import Math
# import inspect

# funcList = [(getattr(Math, func))
#             for func in dir(Math) if callable(getattr(Math, func))]
# parametersList = [inspect.signature(func).parameters for func in funcList]

# params = inspect.signature(funcList[0]).parameters
# # params = list(params.values())
# inputParamsPair = list(params.values())
# # print(inputParamsPair[0].name)
# print(type(Math))
# import os
# import FUNC

# # 获取当前脚本所在目录
# current_dir = os.path.dirname(__file__)

# # 构建文件夹路径
# folder_path = os.path.join(current_dir, FUNC.__name__)

# # 获取文件夹下的所有文件
# files = os.listdir(folder_path)
# print(type(files[0]))
import inspect
import FUNC
import os
import importlib.util
import types


# def get_module_list(folder: types.ModuleType):
#     folder_path = os.path.dirname(__file__)
#     folder_path = os.path.join(folder_path, folder.__name__)
#     print(folder.__name__)
#     abs_folder_path = os.path.abspath(folder_path)
#     module_list = []
#     for file_name in os.listdir(abs_folder_path):
#         if file_name.endswith('.py') and not file_name.startswith('__'):
#             module_name = os.path.splitext(file_name)[0]
#             module_spec = importlib.util.spec_from_file_location(
#                 module_name, os.path.join(abs_folder_path, file_name))
#             module = importlib.util.module_from_spec(module_spec)
#             module_spec.loader.exec_module(module)
#             module_list.append(module)
#     return module_list


# # 指定相对路径的文件夹路径

# # folder_path = 'NodeTree\\TEST\\FUNC'
# # 获取模块列表

# modules = get_module_list(FUNC)
# module = importlib.import_module('FUNC')
# members = inspect.getmembers(module)
# functions_and_variables = [member[0] for member in members if inspect.isfunction(
#     member[1]) or not inspect.isroutine(member[1])]
# # 打印模块列表
# print(inspect.getmembers(FUNC))
# # print(FUNC.__name__)


import os


function_folder = "./FUNC"

# 获取 Function 文件夹下所有文件的路径
file_names = [file_name[:-3]
              for file_name in os.listdir(function_folder) if file_name.endswith(".py")]

# 导入每个文件并运行 loadRegisterFuncNodes 函数
for file_name in file_names:
    module = __import__(f"Function.{file_name}", fromlist=["Math"])
    math_func = getattr(module, "Math", None)  # 获取 Math 函数
    if math_func:
        # node_cls_math = FunctionCore.loadRegisterFuncNodes(math_func)
        print(math_func)
