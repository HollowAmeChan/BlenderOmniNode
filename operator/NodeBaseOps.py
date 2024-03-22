import bpy
from . import MultiThreadedCompilation


class NodeSetDefaultSize(bpy.types.Operator):
    bl_idname = "ho.nodesetdefaultsize"  # 注册到bpy.ops下
    bl_label = "恢复node默认大小"

    node_name: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            node = bpy.context.space_data.node_tree.nodes[self.node_name]
            node.size2default()
            node.preview_scale = node.preview_scale_default

            return {'FINISHED'}
        except:
            return {'FINISHED'}


class NodeSetBiggerSize(bpy.types.Operator):
    bl_idname = "ho.nodesetbiggersize"  # 注册到bpy.ops下
    bl_label = "加宽node"

    node_name: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            node = bpy.context.space_data.node_tree.nodes[self.node_name]
            node.width *= 2

            return {'FINISHED'}
        except:
            return {'FINISHED'}


class LayerRunning(bpy.types.Operator):
    bl_idname = "ho.layerrunning"
    bl_label = "节点分层运行"

    def execute(self, context):
        MultiThreadedCompilation.LayerRun(
            context.space_data.node_tree.nodes)
        # print("==========    REPORT    ==========")
        # for i in runningNodeLayer:
        #     print([j.name for j in i], end="\t")
        #     print("")
        # print("==========    LAYERS    ==========")
        # for i in runningLayer:
        #     for j in i:
        #         if hasattr(j, "name"):
        #             print(j.name, end="\t")
        #         else:
        #             print(j, end="\t,\t")
        #     print("")
        # print("==========    LINKS     ==========")
        # for i in linkSet:
        #     print(i.from_node.name, ":", i.from_socket.identifier,
        #           "\t->\t",
        #           i.to_node.name, ":", i.to_socket.identifier,)
        # print("==========PERSONAL_PROPS==========")
        # for i in nodeSet:
        #     personalInputProps, personalOutputProps = i.report_personalProps()
        #     print("NAME:    ", i.name)
        #     print("inputs:  ", personalInputProps)
        #     print("outputs: ", personalOutputProps)
        # print("==========     OVER     ==========")
        return {'FINISHED'}


clss = [NodeSetDefaultSize, NodeSetBiggerSize, LayerRunning]


def register():
    try:
        for i in clss:
            bpy.utils.register_class(i)
    except Exception:
        print(__file__+" register failed!!!")


def unregister():
    try:
        for i in clss:
            bpy.utils.unregister_class(i)
    except Exception:
        print(__file__+" unregister failed!!!")
