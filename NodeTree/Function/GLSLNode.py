import OpenGL  # NOQA: E402
from OpenGL.GL import *  # NOQA: E402
import OpenGL.GL.shaders  # NOQA: E402

import bpy
from math import *
import numpy as np
from ..FunctionCore import meta


DEFAULT_VertexShader = """
#version 330 core
layout (location = 0) in vec3 position;
out vec2 resolution;
layout(location = 2) in vec2 inTexCoords;
out vec2 uv;
//变换相关
uniform mat4 scale;
uniform mat4 rotation;
uniform mat4 translation;


void main(){
    // 应用变换
    vec4 scaled_position = scale * vec4(position, 1.0);
    vec4 rotated_position = rotation * scaled_position;
    vec4 translated_position = translation * rotated_position;

    gl_Position = translated_position;
    uv = inTexCoords;
}
"""

DEFAULT_FragmentShader = """
    #version 330 core

    // uniform vec2 resolution;
    uniform float time;
    in vec2 uv;

    out vec4 fragColor;

    void main()
    {
        //vec2 uv = gl_FragCoord.xy / (128,128);
        fragColor = vec4(uv.x, uv.y, 0.0, 1.0);

    }
    """


@meta(enable=True,
      bl_label="GLSL测试节点",
      base_color=(0.2, 0.2, 0.2),
      Bimage={"name": "图片"},
      VertexShaderCode={"name": "顶点shader"},
      FragmentShaderCode={"name": "片段shader"},
      _OUTPUT_NAME=["图片"],)
def GLSL_test(
    Bimage: bpy.types.Image,
    VertexShaderCode: bpy.types.Text,
    FragmentShaderCode: bpy.types.Text,
    offset_xyz: bpy.types.NodeSocketVector,
    scale_xyz: bpy.types.NodeSocketVector,
    rotate_xyz: bpy.types.NodeSocketVector,
    test_width: float,
    test_height: float,
) -> bpy.types.Image:
    '''
    TODO:要做的还有很多
    1.  渲染不出来下半部分(128分辨率下大概从下往上30的范围)
    2.  z轴缩放有问题,缩放了大概0.5倍,使用备用quad与indices可以看出来
    3.  从文本text对象(blender对象)中拿字符还没有测试，看上去是.as_string()
    4.  性能问题
        这个节点类是直接生成的，所以暂时不能对销毁、新建等回调进行修改
        全部写在process里面,导致频繁调用,每次调用都会重新分析源码编译着色器
        这是不对的,应该强制手动,将编译的shader对象挂到node实例上,在销毁的时候清除缓冲区
        应该是使用glDeleteFramebuffers()以及glDeleteProgram(shader)
        更新的时候调用process,这里面只写glUniformMatrix4fv这种指定参数的函数
        以及最后的输出到图像(最好这一步也不要了,单独弄一个从buffer到图像的节点,以及传递buffer的socket)
    5.  pixels的读取写入问题
        这两部都很慢,前者最快应该是[:]拷贝,后者可能要用到ndarray/ctype,以及pixels的for_each方法
    6.  背面渲染的问题
        使用备用quad可以发现背面渲染有问题,可能跟面传入顺序,面顶点顺序有关
    7.  glVertexAttribPointer以及glsl的layout (location = 0) in vec3 position;
        这些玩意儿怎么使用的我也不好说,他是怎么读的ndarray的
    '''

    #   positions      colors       texture coords
    quad = [-1., -1., 0.,  1., 0., 0.,  0., 0.,
            1., -1., 0.,  0., 1., 0.,  1., 0.,
            1.,  1., 0.,  0., 0., 1.,  1., 1.,
            -1.,  1., 0.,  1., 1., 1.,  0., 1.]
    # quad = [-1., -1., 0.,  1., 0., 0.,  0., 0.,
    #         1., -1., 0.,  0., 1., 0.,  1., 0.,
    #         1.,  1., 0.,  0., 0., 1.,  1., 1.,
    #         1.,  -1., -1.,  1., 1., 1.,  0., 1.]
    quad = np.array(quad, dtype=np.float32)

    # 顶点索引顺序
    indices = [0, 1, 2,
               2, 3, 0]
    # indices = [0, 1, 2,
    #            2, 3, 0,
    #            1, 3, 2,
    #            0, 3, 1]
    indices = np.array(indices, dtype=np.uint32)

    # 输入shader源码
    if VertexShaderCode:
        vertex_shader = VertexShaderCode.as_string()
    else:
        vertex_shader = DEFAULT_VertexShader
    if FragmentShaderCode:
        fragment_shader = FragmentShaderCode.as_string()
    else:
        fragment_shader = DEFAULT_FragmentShader

    # 编译着色器
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    # VBO
    v_b_o = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, v_b_o)
    glBufferData(GL_ARRAY_BUFFER, quad.itemsize *
                 len(quad), quad, GL_STATIC_DRAW)
    # EBO
    e_b_o = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, e_b_o)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize *
                 len(indices), indices, GL_STATIC_DRAW)

    # 配置初始数据的位置
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          quad.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # 配置初始数据的颜色
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                          quad.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    # 配置初始数据的纹理坐标
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE,
                          quad.itemsize * 8, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    # 纹理
    texture = glGenTextures(1)
    # 绑定纹理
    glBindTexture(GL_TEXTURE_2D, texture)
    # Texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Bimage
    Bimage_pixels = Bimage.pixels[:]
    Bimage_width = Bimage.size[0]
    Bimage_height = Bimage.size[1]
    # 将float列表转换为NumPy数组
    Bimage_float_array = np.array(Bimage_pixels)
    # 将float数组四舍五入到最近的整数，并将其限制在0到255的范围内，然后转换为uint8类型
    Bimage_uint8_array = np.clip(
        np.round(Bimage_float_array), 0, 255).astype(np.uint8)
    bytes_data = Bimage_uint8_array.tobytes()  # 将NumPy数组转换为字节形式
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 Bimage_width, Bimage_height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes_data)

    # 创建渲染缓冲区
    rb_obj = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rb_obj)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA,
                          Bimage_width, Bimage_height)

    # 创建帧缓冲区
    fb_obj = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fb_obj)
    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, rb_obj)

    # 检查帧缓冲区（简单的缓冲区应该不是问题）
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        print("incomplete framebuffer object")

    # -------------------------------实验-------------------------------
    scale_matrix = np.array([
        [scale_xyz[0], 0, 0, 0],
        [0, scale_xyz[1], 0, 0],
        [0, 0, scale_xyz[2], 0],
        [0, 0, 0, 1]
    ])

    rotate_x_rad = radians(rotate_xyz[0])
    rotate_y_rad = radians(rotate_xyz[1])
    rotate_z_rad = radians(rotate_xyz[2])

    # 构建绕 X 轴的旋转矩阵
    rotation_x = np.array([
        [1, 0, 0, 0],
        [0, cos(rotate_x_rad), -sin(rotate_x_rad), 0],
        [0, sin(rotate_x_rad), cos(rotate_x_rad), 0],
        [0, 0, 0, 1]
    ])

    # Y 轴旋转矩阵
    rotation_y = np.array([
        [cos(rotate_y_rad), 0, sin(rotate_y_rad), 0],
        [0, 1, 0, 0],
        [-sin(rotate_y_rad), 0, cos(rotate_y_rad), 0],
        [0, 0, 0, 1]
    ])

    # Z 轴旋转矩阵
    rotation_z = np.array([
        [cos(rotate_z_rad), -sin(rotate_z_rad), 0, 0],
        [sin(rotate_z_rad), cos(rotate_z_rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    # 旋转矩阵
    rotation_matrix = rotation_z @ rotation_y @ rotation_x

    translation_matrix = np.array([
        [1, 0, 0, offset_xyz[0]],
        [0, 1, 0, offset_xyz[1]],
        [0, 0, 1, offset_xyz[2]],
        [0, 0, 0, 1]
    ])

    # -------------------------------实验-------------------------------
    # 安装shader!!现在才开始渲染
    glUseProgram(shader)

    glUniformMatrix4fv(glGetUniformLocation(
        shader, "scale"), 1, GL_TRUE, scale_matrix)  # 实验
    glUniformMatrix4fv(glGetUniformLocation(
        shader, "rotation"), 1, GL_TRUE, rotation_matrix)  # 实验
    glUniformMatrix4fv(glGetUniformLocation(
        shader, "translation"), 1, GL_TRUE, translation_matrix)  # 实验

    # 绑定帧缓冲区并设置视口大小
    glBindFramebuffer(GL_FRAMEBUFFER, fb_obj)
    glViewport(0, 0, Bimage_width, Bimage_height)

    # 绘制覆盖整个视口的四边形
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
    # 读取数据并创建图像
    image_buffer = glReadPixels(
        0, 0, Bimage_width, Bimage_height, GL_RGBA, GL_UNSIGNED_BYTE)
    image_out_uint8 = np.frombuffer(image_buffer, dtype=np.uint8)
    image_out_float32 = image_out_uint8.astype(np.float32) / 255.0

    # print(image_buffer)
    # print(len(image_out_uint8))
    # print(image_out_uint8[:7])
    # print(len(image_out_float32))
    # print(image_out_float32[:7])
    # print(len(Bimage.pixels))
    # print(Bimage.pixels[:7])
    Bimage.pixels = image_out_float32
