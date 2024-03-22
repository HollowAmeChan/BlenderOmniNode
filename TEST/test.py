import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import cv2

# 定义顶点着色器和片段着色器源代码
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0, 0.5, 0.2, 1.0);
}
"""

# 定义顶点坐标
vertices = np.array([
    -0.5, -0.5, 0.0,
    0.5, -0.5, 0.0,
    0.0,  0.5, 0.0
], dtype=np.float32)

# 初始化glfw
if not glfw.init():
    raise Exception("glfw初始化失败")

# 创建窗口
window = glfw.create_window(800, 600, "Simple OpenGL", None, None)
if not window:
    glfw.terminate()
    raise Exception("窗口创建失败")

# 设置OpenGL上下文
glfw.make_context_current(window)

# 编译顶点着色器和片段着色器
vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
shader_program = compileProgram(vertex_shader, fragment_shader)

# 创建顶点缓冲对象和顶点数组对象
VBO = glGenBuffers(1)
VAO = glGenVertexArrays(1)

# 绑定VAO和VBO
glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# 链接顶点属性
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 *
                      sizeof(GLfloat), ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

# 解绑VAO和VBO
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# 创建帧缓冲对象和渲染缓冲对象
FBO = glGenFramebuffers(1)
RBO = glGenRenderbuffers(1)

# 绑定帧缓冲对象
glBindFramebuffer(GL_FRAMEBUFFER, FBO)

# 绑定渲染缓冲对象
glBindRenderbuffer(GL_RENDERBUFFER, RBO)
glRenderbufferStorage(GL_RENDERBUFFER, GL_RGB, 800, 600)
glFramebufferRenderbuffer(
    GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, RBO)

# 检查帧缓冲对象是否完整
if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("帧缓冲对象不完整！")
    glfw.terminate()

# 解绑帧缓冲对象
glBindFramebuffer(GL_FRAMEBUFFER, 0)

# 渲染循环
while not glfw.window_should_close(window):
    glfw.poll_events()

    # 渲染指令
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # 使用着色器程序
    glUseProgram(shader_program)

    # 绘制三角形
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)

    # 将渲染结果读取到numpy数组中
    glBindFramebuffer(GL_FRAMEBUFFER, FBO)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    data = glReadPixels(0, 0, 800, 600, GL_RGB, GL_UNSIGNED_BYTE)
    print(data)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    img = np.frombuffer(data, dtype=np.uint8).reshape((600, 800, 3))

    # 显示渲染结果
    cv2.imshow('Rendered Image', cv2.cvtColor(
        np.flip(img, axis=0), cv2.COLOR_RGB2BGR))

    # 交换缓冲
    glfw.swap_buffers(window)

    # 检查退出
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

# 清理资源
glfw.terminate()
