bl_info = {
    "name": "Omni NodeTree-by HollowAme",
    "author": "HollowAme",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Hollow",
    "description": "Node What You Want",
    "warning": "",
    "wiki_url": "",
    "category": "HollowAme",
}


def register():
    print("==========HOLLOW ADDONS LOADING==========")
    print("==========   OMNI NodeTree    ==========")
    import os  # NOQA: E402
    import sys  # NOQA: E402
    import bpy  # NOQA: E402
    # 将本地的第三方库导入
    plugin_dir = os.path.dirname(__file__)
    lib_dir = os.path.abspath(os.path.join(
        plugin_dir, ".", "lib"))
    sys.path.append(lib_dir)
    # 检查库存不存在
    import importlib.util  # NOQA: E402

    def module_exists(module_name):
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    # if not module_exists("glm"):
    #     print(
    #         "模块:\t"+"glm" + "\t没有安装\n"
    #         "请使用belnder_pip插件安装\n" +
    #         "或者手动使用pip安装\n" +
    #         "注意glm模块库名为PyGLM")
    #     print("==========         END         ==========")
    #     return
    # 注册
    from .NodeTree import Nodes, NodeSocket, NodeTree  # NOQA: E402
    from .operator import NodeBaseOps  # NOQA: E402
    from .panel import panel    # NOQA: E402
    NodeBaseOps.register()
    NodeTree.register()
    NodeSocket.register()
    Nodes.register()
    panel.register()
    print("==========         END         ==========")


def unregister():
    from .NodeTree import Nodes, NodeSocket, NodeTree  # NOQA: E402
    from .operator import NodeBaseOps  # NOQA: E402
    from .panel import panel    # NOQA: E402
    NodeBaseOps.unregister()
    NodeTree.unregister()
    NodeSocket.unregister()
    Nodes.unregister()
    panel.unregister()
