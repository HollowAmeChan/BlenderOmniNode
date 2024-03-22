import bpy
import types
import pprint
from bpy.types import NodeTree
from ..operator import NodeBaseOps, MultiThreadedCompilation
from bpy.app.handlers import persistent

TREE_ID = 'OMNINODE'  # 节点树系统注册进去的identifier
TREE_ID_NAME = 'OmniNodeTree'  # 节点树系统的标识符idname


class OmniNodeTree(NodeTree):  # 节点树
    bl_idname = TREE_ID_NAME
    bl_label = "Omni节点图-Omni NodesTree"  # 界面显示名
    bl_icon = 'DRIVER'
    is_auto_update: bpy.props.BoolProperty(
        description="是否实时刷新", default=False)  # type: ignore
    # late_node_number: bpy.props.IntProperty(
    #     description="延迟更新的节点总数量，为了实现拓补更新检测", default=0)  # type: ignore

    @classmethod
    def poll(self, context):
        return True

    def update(self):
        '''拓补关系变化监听,为了给新节点上监听(因为Duplicate被迫使用全体更新),装饰器为了常开,见bpy.app.handlers文档'''
        '''
        TODO:
        有屎
        本来用的bpy.app.handlers.depsgraph_update_post.append,现在改用了tree的回调
        
        监听socket更新可以使用订阅,但是复制节点不会复制订阅
        
        想到重写node父类的copy,发现根本就没有copy,或者说没有公开让我们改
        
        想到在init时就更新订阅,但是复制根本就没有调用init
        
        最后想监听深度图,监听到拓补发生变化就更新。问题是监听拿不到新增的node对象
        甚至复制节点本身这个ops都很抽象,有三种,并且还长得都不像在复制
        Duplicate这个操作的触发极其恶心,因为刚复制完后不操作,直接修改值的话，会被认为是在重新执行上一步操作
        也就是说会频繁触发Duplicate,如果把他当做拓补改变了,进行更新的话应该会很卡
        
        另一个思路是在tree的update上写,但是这个东西触发比深度图里面还要频繁,并且依旧有Duplicate这个重复操作的问题

        最终的思路是比较上一次与这一次的节点数量了,因为增减都会导致数量改变
        在tree下设置一个被动更新的变量,触发可以选(深度图要枚举比较,tree Update频繁但是没有字符比较)
        选择用tree的update,每次先比较当前数量跟上一次的数量,再赋值进去
        如果两次数量不一样，进行全体监听的更新

        可以更进一步,直接存node的集合,每次都比较集合的差集,只更新差集
        blender的自定义数据类型不能用set,以及list[Node]也不能正常的注册进去
        最后使用的list[Node.name],应该不会有重新覆盖的问题

        24.3.17我注意到另一个问题，监听只存在于当前的工程会话，重新打开后全部都掉了
        我意识到这就是不够彻底的mvc,我应该把树看做一个整体,节点的socket更新也会触发节点树的update
        所以我应该删掉所有的监听,全部都在tree更新回调里写(增删节点,改变socket默认值,改变link都会触发)
        先看改变socket默认值的情况:
        首先是必须把节点的默认值更新到内部缓存,然后再判定是否触发全体运行
        如果树拓补改变了,一定要全体更新到内部变量,因为复制不触发init,没有办法
        如果树拓补没变,说明是Duplicate或者在改默认值,一样要出发全体更新
        link没有name不好存,所以就不存了
        因此树的更新回调里面必须要出发全体更新参数到内部变量

        '''
        # if self.get("late_node_list") == None:  # node tree 没有init所以就只能在这写了
        #     self["late_node_list"] = list()  # 自定义的类型不支持集合，很恶心，只能用list了

        # newList = [node.name for node in self.nodes]
        # oldList = self.get("late_node_list")
        # change = set(newList)-set(oldList)
        # change = list(change)
        # self["late_node_list"] = newList

        # if not change == None:
        #     for nodename in change:
        #         # TODO:有点屎味儿，因为新建会触发两遍，删掉其中一个订阅会不完整
        #         self.nodes[nodename].updateSubscribe()

        for node in self.nodes:  # 总进行所有节点的接口值更新到内部变量
            node.updateSocketDefaultValue2PersonalProps()
        if self.is_auto_update:  # 如果节点树自动更新，则运行整个节点树
            MultiThreadedCompilation.LayerRun(self.nodes)


def setOutputNode(node, context):
    node.updateColor()


def setBugNode(node, context):
    node.updateColor()


def ProcessBoolSwitchUpdate(node, context):
    node.inputs["_BOOL"].hide = 1-node.process_bool_switch  # 先触发回调再更新
    return


class OmniNode:
    '''节点基类'''
    bug_color: bpy.props.FloatVectorProperty(
        name="link连接bug", size=3, subtype="COLOR", default=(1, 0, 0))  # type: ignore
    bug_text: bpy.props.StringProperty(
        name="Bug详情", default="No bug")  # type: ignore
    is_bug: bpy.props.BoolProperty(
        name="是否bug", default=False, update=setBugNode)  # type: ignore
    debug: bpy.props.BoolProperty(name="调试", default=False)  # type: ignore

    default_width: bpy.props.FloatProperty(default=180)  # type: ignore
    default_heigh: bpy.props.FloatProperty(default=100)  # type: ignore

    is_output_node: bpy.props.BoolProperty(
        name="是否是输出节点", default=False, update=setOutputNode)  # type: ignore
    output_color: bpy.props.FloatVectorProperty(
        name="作为输出节点的高亮颜色", size=3, subtype="COLOR", default=(0.4, 0, 0))  # type: ignore
    base_color: bpy.props.FloatVectorProperty(
        name="默认类型", size=3, subtype="COLOR", default=(0.191, 0.061, 0.012))  # type: ignore
    omni_description: bpy.props.StringProperty(
        name="OMNI节点描述", default="没有使用描述")  # type: ignore
    process_bool_switch: bpy.props.BoolProperty(
        name="是否公开bool逻辑接口", default=False, update=ProcessBoolSwitchUpdate)  # type: ignore


# ---------------------------------内部核心相关-------------------------------


    def updateSocket2PersonalProps(self, context):
        # 使用字典存储内部缓存变量
        # 使用identifier作为key
        for i in self.inputs:
            self.get("personalInputProps")[i.identifier] = i.default_value

        index = 0
        for i in self.outputs:
            self.get("personalOutputProps")[
                "_OUTPUT"+str(index)] = i.default_value
            index += 1

    def updateSocketDefaultValue2PersonalProps(self):
        '''没连接就更新默认值进去'''
        # 最基本的socket更新回调（同步到内部变量）

        # 只在没有socket连接的时候更新内部变量，连接时，更新靠上游节点
        for i in self.inputs:
            if i.is_linked:
                continue
            self.get("personalInputProps")[i.identifier] = i.default_value
        index = 0
        for o in self.outputs:
            if i.is_linked:
                continue
            self.get("personalOutputProps")[
                "_OUTPUT"+str(index)] = o.default_value
            index += 1

    def report_personalProps(self):
        personalInputProps = self.get("personalInputProps")
        personalOutputProps = self.get("personalOutputProps")
        if personalInputProps is not None and personalOutputProps is not None:
            return dict(personalInputProps), dict(personalOutputProps)
        else:
            return {}, {}


# --------------------------------自身基本特性相关------------------------------


    def size2default(self):
        self.width = self.default_width
        self.height = self.default_heigh

    def updateColor(self):
        if self.is_bug:
            self.color = self.bug_color
            return
        if self.is_output_node:
            self.color = self.output_color
            return
        else:
            self.color = self.base_color
# --------------------------------自身功能相关------------------------------

    def process(self):
        return
# --------------------------------原生方法重载------------------------------

    def init(self, context):
        self["personalInputProps"] = dict()  # 自定义的数据类型只能这么写，然后调用用.get()
        self["personalOutputProps"] = dict()
        self["fatherTree"] = bpy.context.space_data.node_tree
        self.use_custom_color = True
        self.updateColor()
        self.size2default()

    def draw_label(self):
        '''动态标签'''
        return f"{self.name}"

    def draw_buttons(self, context, layout):
        '''绘制节点按钮'''
        # 绘制小工具栏
        main_row = layout.row(align=False)  # 常用按钮显示

        row_L = main_row.row(align=True)  # 左侧按钮
        row_L.alignment = 'LEFT'
        if self.is_bug:
            row_L.label(icon="ERROR",)
        row_L.prop(self, "debug", text="", toggle=True, icon="FILE_SCRIPT")

        if context.space_data.node_tree.is_auto_update:
            row_L.prop(context.space_data.node_tree,
                       "is_auto_update", text="", icon="DECORATE_LINKED")
        else:
            row_L.prop(context.space_data.node_tree,
                       "is_auto_update", text="", icon="UNLINKED")

        row_C = main_row.row(align=True)  # 中心按钮
        SetDefaultSize = row_C.operator(
            NodeBaseOps.NodeSetDefaultSize.bl_idname, text="", icon="REMOVE")
        SetDefaultSize.node_name = self.name
        SetBiggerSize = row_C.operator(
            NodeBaseOps.NodeSetBiggerSize.bl_idname, text="", icon="ADD")
        SetBiggerSize.node_name = self.name

        row_R = main_row.row(align=True)  # 右侧按钮
        row_R.alignment = 'RIGHT'
        row_R.prop(self, "process_bool_switch",
                   text="", icon="OUTLINER_DATA_LIGHT")
        row_R.prop(self, "is_output_node", text="", icon="ANIM_DATA")
        row_R.operator(
            NodeBaseOps.LayerRunning.bl_idname, text="", icon="FILE_REFRESH")

        if self.debug:  # debug显示
            # bug描述
            layout.label(text=f"bug类型:{self.bug_text}")
            # 内部prop详情
            layout.label(text="<<<<<<<<<<personalInputProps<<<<<<<<<<")
            layout.label(text=str(self.get("personalInputProps").to_dict()))
            layout.label(text=">>>>>>>>>>personalOutputProps>>>>>>>>>")
            layout.label(text=str(self.get("personalOutputProps").to_dict()))
            # OMNI节点描述
            lines = self.omni_description.splitlines()
            for line in lines:
                layout.label(text=line)

    def free(self):
        # 被删除时调用
        bpy.msgbus.clear_by_owner(id(self))


cls = [OmniNodeTree]


def register():
    try:
        for i in cls:
            bpy.utils.register_class(i)
    except Exception:
        print(__file__+" register failed!!!")


def unregister():
    try:
        for i in cls:
            bpy.utils.unregister_class(i)
    except Exception:
        print(__file__+" unregister failed!!!")
