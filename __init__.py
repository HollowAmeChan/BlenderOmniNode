import bpy
from bpy.types import Context, Operator
from bpy.types import Panel

from .NodeTree import NodeBase, Nodes, NodeSocket
from .operator import NodeBaseOps

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
    NodeBaseOps.register()
    NodeBase.register()
    NodeSocket.register()
    Nodes.register()
    print("==========         END         ==========")


def unregister():
    NodeBaseOps.unregister()
    NodeBase.unregister()
    NodeSocket.unregister()
    Nodes.unregister()
