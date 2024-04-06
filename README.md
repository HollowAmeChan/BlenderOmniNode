# BlenderOmniNode
Try to node any script (not mvc for now)

__Please prioritize the download of the release version to get the latest version under development__ (the source code contains virtual environments as well as test functions, so it is larger)

Sorry for not being able to update the organized code in time, it may be a long interval. (I am learning while developing, there may be relatively large changes)

__Some python module dependencies may not be included__ (pyopengl,pyglfw,pyimgui,pyglm are used)

You can install them manually using pip, or use the blender plugin blender_pip to install and manage them.

URL: https://github.com/amb/blender_pip

# 使用方法

找到`NodeTree\Function`文件夹，新建你的函数文件

找到`NodeTree\Nodes.py`文件，将你新建的文件import后使用`FunctionCore.loadRegisterFuncNodes`生成并添加到注册列表中

在`node_categories`中添加一个包含你新建文件内容的类，这个类会显示在新建节点的分类中

所有的规范可以参考自带的一些写法，可以使用meta信息对函数生成的节点进行一定程度的修饰

所有的节点类都是由函数自动生成的（暂时但希望一直是这样）

__请优先下载发布版，获取正在开发的最新版本__（源码包含虚拟环境以及测试功能，所以比较大）

抱歉不能及时更新整理好的代码，可能会间隔很长时间。（本人一边学习一边开发，可能会有比较大的变动）

__一些python模块依赖可能没有包含__（使用了pyopengl,pyglfw,pyimgui,pyglm）

可以手动使用pip安装，或者使用blender插件blender_pip安装管理

网址：https://github.com/amb/blender_pip
