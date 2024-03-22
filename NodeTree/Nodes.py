from . import FunctionCore
import bpy
from bpy.types import Node
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from .NodeBase import TREE_ID
from .Function import DynamicBoneRig, Base, Math


class OmniNodeCategory(NodeCategory):  # 定义一个节点集合类
    @classmethod
    def poll(cls, context):
        return True


cls = []
node_cls_math = FunctionCore.loadRegisterFuncNodes(Math)
node_cls_base = FunctionCore.loadRegisterFuncNodes(Base)
node_cls_DynamicBoneRig = FunctionCore.loadRegisterFuncNodes(DynamicBoneRig)
cls.extend(node_cls_math)
cls.extend(node_cls_base)
cls.extend(node_cls_DynamicBoneRig)

node_categories = [
    OmniNodeCategory("MATH", "Math", items=[
        NodeItem(i.bl_idname) for i in node_cls_math
    ]),
    OmniNodeCategory("BASE", "Base", items=[
        NodeItem(i.bl_idname) for i in node_cls_base
    ]),
    OmniNodeCategory("DYNAMICBONERIG", "DynamicBoneRig", items=[
        NodeItem(i.bl_idname) for i in node_cls_DynamicBoneRig
    ])
]


# def get_module_list(folder: types.ModuleType):
#     folder_path = os.path.dirname(__file__)
#     folder_path = os.path.join(folder_path, folder.__name__.split(".")[-1])
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


# funcModules = get_module_list(Function)


# cls = []
# node_categories = []
# for i in funcModules:
#     node_cls = FunctionCore.loadRegisterFuncNodes(i)
#     node_cat = DriversNodeCategory(
#         i.__name__.upper(),
#         i.__name__,
#         items=[
#             NodeItem(i.bl_idname) for i in node_cls
#         ])
#     cls.append(node_cls)
#     node_categories.append(node_cat)
# print(cls)


def register():
    try:
        for i in cls:
            bpy.utils.register_class(i)
        nodeitems_utils.register_node_categories(TREE_ID, node_categories)
    except Exception:
        print(__file__+" register failed!!!")


def unregister():
    try:
        for i in cls:
            bpy.utils.unregister_class(i)
        nodeitems_utils.unregister_node_categories(TREE_ID)
    except Exception:
        print(__file__+" unregister failed!!!")
