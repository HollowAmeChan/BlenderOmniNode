# BlenderOmniNode
Try to node any script (not mvc for now)
# 使用方法

找到`NodeTree\Function`文件夹，新建你的函数文件

找到`NodeTree\Nodes.py`文件，将你新建的文件import后使用`FunctionCore.loadRegisterFuncNodes`生成并添加到注册列表中

在`node_categories`中添加一个包含你新建文件内容的类，这个类会显示在新建节点的分类中

所有的规范可以参考自带的一些写法，可以使用meta信息对函数生成的节点进行一定程度的修饰

所有的节点类都是由函数自动生成的（暂时但希望一直是这样）
