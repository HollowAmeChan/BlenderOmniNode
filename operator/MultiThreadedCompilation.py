import bpy


def getRunningLayer(nodes) -> tuple[set, set, list]:
    class nodeLink(bpy.types.NodeLink):
        def __str__(self) -> str:
            return self.from_node.name + "\t->\t" + self.to_node.name

    tempLinkSet = set()
    outLinkSet = set()
    visitedNode = set()

    # 搜索输出节点集合
    outNodeSet = set()
    for node in nodes:
        node.is_bug = False
        if node.is_output_node:
            outNodeSet.add(node)

    # dfs搜索出所有link
    def followLinks(node_in):
        for n_inputs in node_in.inputs:
            for node_links in n_inputs.links:
                tempLinkSet.add(nodeLink(node_links))
                outLinkSet.add(nodeLink(node_links))
                followLinks(node_links.from_node)

    # 此处控制起点，将总输出节点独立储存
    outSet = set()
    for node in nodes[:]:
        if node.is_output_node:
            outSet.add(node)
            followLinks(node)

    # 分层输出运行节点
    outLayerList = []
    while len(tempLinkSet):
        parentSet = set()
        childrenSet = set()
        # 移除visited
        to_remove = set()
        for i in tempLinkSet:
            if i.from_node in visitedNode or i.to_node in visitedNode:
                to_remove.add(i)
        tempLinkSet = tempLinkSet.difference(to_remove)

        for i in tempLinkSet:
            parentSet.add(i.from_node)
            childrenSet.add(i.to_node)
        layer = parentSet.difference(childrenSet)
        # 补充顶层
        if not layer:
            layer = outSet-visitedNode  # 防止重复运行 - 路线上有多个输出
        visitedNode = visitedNode.union(layer)
        outLayerList.append(list(layer))

    # 分层输出运行节点+link
    outRunningList = []
    total = len(outLayerList)
    for time in range(total):
        thisLayer = outLayerList[time]
        if time == total-1:
            outRunningList.append(thisLayer)
            break
        nextLayer = outLayerList[time+1]

        outRunningList.append(thisLayer)
        linkLayer = []
        for node in thisLayer:
            for link in outLinkSet:
                if link.from_node == node:
                    linkLayer.append(link)
        outRunningList.append(linkLayer)

    # 不存在link时(此逻辑找不到任何节点)，输出一层outNode
    if len(outRunningList) == 0:
        outRunningList.append(list(outNodeSet))

    return outLinkSet, visitedNode, outLayerList, outRunningList

# ---------------------------------------类型转换---------------------------------------------
# TYPE_TRANS_FUNC_DICT = {}
# TYPE_TRANS_FUNC_DICT[bpy.types.Object] = {}


# def bl_obj2str(bl_obj):
#     str = bl_obj.name
#     return str


# TYPE_TRANS_FUNC_DICT[bpy.types.Object][str] = bl_obj2str


# def typeTrans(toData, fromData):
#     if type(fromData) == type(toData):
#         return fromData
#     else:
#         func = TYPE_TRANS_FUNC_DICT[type(fromData)][type(toData)]
#         # TODO:这里type不一定拿得到类型，可能里面是个None，本来这些都是any类型的，真正需要的类型在函数签名上
#         return func(fromData)
# ----------------------------------------------------------------------------------------------------------


def runRunningLayer(runningLayers):
    for layer in runningLayers:
        if layer == []:
            break
        if hasattr(layer[0], "to_socket"):
            # 执行link
            for link in layer:
                from_node = link.from_node
                to_node = link.to_node
                from_node_personalOutputProps = from_node.get(
                    "personalOutputProps")
                to_node_personalInputProps = to_node.get(
                    "personalInputProps")

                to_data = to_node_personalInputProps[
                    link.to_socket.identifier]  # 这里是临时变量
                from_data = from_node_personalOutputProps[
                    link.from_socket.identifier]

                # TODO:这里需要处理类型转换
                # to_node_personalInputProps[link.to_socket.identifier] = typeTrans(
                #     toData=to_data, fromData=from_data)
                to_node_personalInputProps[link.to_socket.identifier] = from_data

        else:
            # 执行node
            for node in layer:
                errorlog = node.process()
                if errorlog:
                    node.is_bug = True
                    node.bug_text = errorlog.__class__.__name__ + \
                        "\n"+str(errorlog)
                    break


def LayerRun(nodes):
    linkSet = set()
    nodeSet = set()
    runningNodeLayer = []
    linkSet, nodeSet, runningNodeLayer, runningLayers = getRunningLayer(
        nodes=nodes,
    )
    runRunningLayer(runningLayers)
