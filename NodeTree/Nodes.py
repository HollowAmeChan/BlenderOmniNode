from . import FunctionCore
import bpy
from bpy.types import Node
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from .NodeBase import TREE_ID
from .Function import DynamicBoneRig, Base, Math, GLSLNode


class OmniNodeCategory(NodeCategory):  # 定义一个节点集合类
    @classmethod
    def poll(cls, context):
        return True


cls = []
node_cls_math = FunctionCore.loadRegisterFuncNodes(Math)
node_cls_base = FunctionCore.loadRegisterFuncNodes(Base)
node_cls_glslNode = FunctionCore.loadRegisterFuncNodes(GLSLNode)
node_cls_DynamicBoneRig = FunctionCore.loadRegisterFuncNodes(DynamicBoneRig)
cls.extend(node_cls_math)
cls.extend(node_cls_base)
cls.extend(node_cls_glslNode)
cls.extend(node_cls_DynamicBoneRig)

node_categories = [
    OmniNodeCategory("MATH", "Math", items=[
        NodeItem(i.bl_idname) for i in node_cls_math
    ]),
    OmniNodeCategory("BASE", "Base", items=[
        NodeItem(i.bl_idname) for i in node_cls_base
    ]),
    OmniNodeCategory("GLSLNODE", "GLSL_Node", items=[
        NodeItem(i.bl_idname) for i in node_cls_glslNode
    ]),
    OmniNodeCategory("DYNAMICBONERIG", "DynamicBoneRig", items=[
        NodeItem(i.bl_idname) for i in node_cls_DynamicBoneRig
    ])
]


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
