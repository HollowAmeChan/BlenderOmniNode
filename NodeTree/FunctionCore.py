import bpy
import mathutils
import inspect
import typing
from .NodeBase import OmniNode
from .NodeSocket import OmniNodeSocketScene, OmniNodeSocketAny
from bpy.types import Node
from bpy.types import NodeSocketFloat, NodeSocketVector, NodeSocketColor, NodeSocketImage, NodeSocketBool, NodeSocketInt, NodeSocketObject, NodeSocketString, NodeSocketRotation, NodeSocketCollection


# 函数变量标签类型：blenderSocket类型
cls_dic = {
    # 签名中没写类型的全是_empty类
    inspect._empty: NodeSocketFloat,
    # blender类转化
    NodeSocketFloat: NodeSocketFloat,
    NodeSocketVector: NodeSocketVector,
    NodeSocketColor: NodeSocketColor,
    NodeSocketImage: NodeSocketImage,
    NodeSocketBool: NodeSocketBool,
    NodeSocketInt: NodeSocketInt,
    NodeSocketObject: NodeSocketObject,
    NodeSocketString: NodeSocketString,
    NodeSocketRotation: NodeSocketRotation,
    NodeSocketCollection: NodeSocketCollection,
    bpy.types.FloatProperty: NodeSocketFloat,
    bpy.types.BoolProperty: NodeSocketBool,
    bpy.types.StringProperty: NodeSocketString,
    bpy.types.IntProperty: NodeSocketInt,
    bpy.types.Object: NodeSocketObject,
    bpy.types.Image: NodeSocketImage,
    bpy.types.Collection: NodeSocketCollection,
    mathutils.Color: NodeSocketColor,
    # python类到blender socket类
    float: NodeSocketFloat,
    str: NodeSocketString,
    # Omni自定义接口
    bpy.types.Scene: OmniNodeSocketScene,
    typing.Any: OmniNodeSocketAny,

}


def meta(**metadata):
    '''
    META信息装饰器
    1.  对于输入参数可以传入一个字典，填入.inputs.new的参数
        a={"name":"111","type":"","identifier":"}
        目前只支持name修改,identifier不可修改
    2.  对于本身的一些设置,一般支持
        omni_description
        bl_label
        base_color
        is_output_node
    3.  由于使用了函数签名来生成，签名无法设置多输出的名字
        目前使用默认_OUTPUT+数字来生成名字，并且不可更改
    '''
    def decorator(func):
        func.__meta = metadata
        return func
    return decorator


def CheckMetaInfo(func) -> tuple[dict, dict[dict], dict[dict]]:
    NodeInfo = {}
    SocketInMetaDict = {}
    SocketOutMetaDict = {}

    # 节点属性信息生成与覆盖
    NodeInfo["bl_label"] = func.__name__
    NodeInfo["bl_idname"] = "HO_OmniNode_" + func.__name__
    NodeInfo["is_output_node"] = False
    NodeInfo["base_color"] = (0.5, 0.5, 0)
    NodeInfo["omni_description"] = ""
    NodeInfo.update(func.__meta)

    # 节点输入接口信息
    params = inspect.signature(func).parameters
    inputParamsPair = list(params.values())
    #   #没有meta的默认信息
    index = 0
    for i in inputParamsPair:
        dic = {
            "type": cls_dic.get(i.annotation, NodeSocketFloat),
            "name": i.name,
            "identifier": i.name
        }
        SocketInMetaDict[i.name] = dic
        index += 1
    if hasattr(func, "__meta"):
        for i in SocketInMetaDict.keys():
            if i in func.__meta:
                SocketInMetaDict[i].update(func.__meta[i])

    return NodeInfo, SocketInMetaDict, SocketOutMetaDict


def CreateNodeClass(func) -> OmniNode:
    NodeInfo, SocketInMetaDict, SocketOutMetaDict = CheckMetaInfo(func)

    class OmniNodeClassInstance(OmniNode, Node):
        bl_label = NodeInfo.get("bl_label")
        bl_idname = NodeInfo.get("bl_idname")

        def init(self, context):
            super().init(context)
            self.base_color = NodeInfo.get("base_color")
            self.updateColor()
            self.is_output_node = NodeInfo.get("is_output_node")
            self.omni_description = NodeInfo.get("omni_description")
            # 生成布尔总开关
            bool = self.inputs.new(type="NodeSocketBool",
                                   name="布尔控制", identifier="_BOOL")
            bool.hide = True
            bool.default_value = True  # 默认打开

            # 生成输入
            for i in SocketInMetaDict.keys():
                tmp = SocketInMetaDict[i].get("type")
                if tmp and type(tmp) != str:
                    SocketInMetaDict[i]["type"] = tmp.__name__
                self.inputs.new(**SocketInMetaDict[i])

            # 生成输出
            returns = inspect.signature(func).return_annotation
            out_params = []
            index = 0  # 生成的socket序号
            if type(returns) == typing.GenericAlias:
                # 多输出情况
                for i in returns.__args__:
                    out_params.append(i)
            else:
                out_params.append(returns)
            if len(out_params):
                for i in out_params:
                    self.outputs.new(type=cls_dic.get(i, NodeSocketFloat).__name__,
                                     name="Output",
                                     identifier="_OUTPUT"+str(index))
                    index += 1

            self.updateSocket2PersonalProps(self)  # 将新注册socket同步到内部变量

        def process(self):
            self.is_bug = False
            self.property_unset("bug_text")

            self.updateSocketDefaultValue2PersonalProps()
            personalInputProps = self.get("personalInputProps")
            personalOutputProps = self.get("personalOutputProps")
            # 布尔关跳过运行
            if not personalInputProps["_BOOL"]:
                return
            # 执行运行
            try:
                dic = dict(personalInputProps)
                del dic["_BOOL"]  # 不传入BOOL变量
                result = func(**dic)
            except Exception as error:
                return error

            if len(dict(personalOutputProps)) == 1:
                personalOutputProps["_OUTPUT0"] = result
            else:
                index = 0
                for i in result:
                    personalOutputProps["_OUTPUT"+str(index)] = i
                    index += 1

    OmniNodeClassInstance.__name__ = "HO_OmniProgramCreateNode_"+func.__name__
    return OmniNodeClassInstance


def loadRegisterFuncNodes(func_module) -> list[Node]:
    cls = []
    for func_str in dir(func_module):
        func = getattr(func_module, func_str)

        if not callable(func):
            continue  # 跳过不可调用
        if not hasattr(func, "__meta"):
            continue  # 跳过没有meta信息的函数
        if not func.__meta.get("enable"):
            continue  # 只编译手动启用的函数（防止加载import包/库）
        cls.append(CreateNodeClass(func))
    return cls
