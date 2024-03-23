import bpy
import mathutils
import inspect
import types
import typing
from .NodeBase import OmniNode
from .NodeSocket import OmniNodeSocketText, OmniNodeSocketScene, OmniNodeSocketAny
from bpy.types import Node
from bpy.types import NodeSocketFloat, NodeSocketVector, NodeSocketColor, NodeSocketImage, NodeSocketBool, NodeSocketInt, NodeSocketObject, NodeSocketString, NodeSocketRotation, NodeSocketCollection


# 函数变量标签类型：blenderSocket类型
cls_dic = {
    # 签名中没写类型的全是_empty类
    inspect._empty: OmniNodeSocketAny,
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
    bpy.types.Text: OmniNodeSocketText,

}


def meta(**metadata):
    '''
    META信息装饰器
    1.  对于输入参数可以传入一个字典，填入.inputs.new的参数
        a={"name":"111","type":"","identifier":"}
        目前只支持name修改,identifier不可修改
    2.  对于本身的一些设置,一般支持
        omni_description:str
        bl_label:str
        base_color:tuple[float,float,float]
        is_output_node:bool
        _OUTPUT_NAME:list[str]
    3.  由于使用了函数签名来生成，签名无法设置多输出的名字
        目前使用默认_OUTPUT+数字来生成identifier
        名称想要修改可以使用_OUTPUT_NAME这个列表,他将会顺序指定输出的名字
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
    NodeInfo["_OUTPUT_NAME"] = ["输出"]
    NodeInfo.update(func.__meta)

    # 节点输入输出接口信息
    signature = inspect.signature(func)
    params = signature.parameters
    outputs = signature.return_annotation

    # 解算输入输出信息
    # 内容类型inspect.Parameter，名字是.name，类型是.annotation
    inputParamsPair: list[inspect.Parameter] = []
    outputParamsType: list[type] = []

    inputParamsPair = list(params.values())
    if type(outputs) == types.GenericAlias:
        tup = typing.get_args(outputs)
        outputParamsType = list(tup)
    elif type(outputs) == None:
        outputParamsType = []
    else:
        outputParamsType = [outputs,]

    #   #没有meta的默认input信息
    if len(inputParamsPair) != 0:
        index = 0
        for i in inputParamsPair:
            identifier = i.name
            dic = {
                "type": cls_dic.get(i.annotation, OmniNodeSocketAny).__name__,
                "name": i.name,
                "identifier": identifier
            }
            SocketInMetaDict[identifier] = dic
            index += 1
        if hasattr(func, "__meta"):
            for i in SocketInMetaDict.keys():
                if i in func.__meta:
                    SocketInMetaDict[i].update(func.__meta[i])
    #   #没有meta的默认output信息
    if len(outputParamsType) != 0:
        index = 0
        for i in outputParamsType:
            try:
                name = NodeInfo["_OUTPUT_NAME"][index]
            except:
                name = "输出"
            identifier = "_OUTPUT"+str(index)
            dic = {
                "type": cls_dic.get(i, OmniNodeSocketAny).__name__,
                "name": name,
                "identifier": identifier
            }
            SocketOutMetaDict[identifier] = dic
            index += 1
        if hasattr(func, "__meta"):
            for i in SocketOutMetaDict.keys():
                if i in func.__meta:
                    SocketOutMetaDict[i].update(func.__meta[i])

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
                self.inputs.new(**SocketInMetaDict[i])
            # 生成输出
            for i in SocketOutMetaDict.keys():
                self.outputs.new(**SocketOutMetaDict[i])
            # 将新注册socket同步到内部变量
            self.updateSocket2PersonalProps(self)

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
