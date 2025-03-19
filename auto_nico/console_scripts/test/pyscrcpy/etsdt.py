import cv2 as cv

from auto_nico.console_scripts.test.pyscrcpy import Client


def on_frame(client, frame):
    """
    帧处理回调函数，在每次接收到有效帧时被调用
    :param client: 客户端对象
    :param frame: 接收到的帧
    """
    # 模拟在屏幕坐标 (300, 500) 处点击
    # client.control.touch(300, 500)
    # 显示接收到的帧
    cv.imshow('Video', frame)
    # 等待 1 毫秒，处理按键事件
    cv.waitKey(1)

def main():
    """
    主函数，创建客户端并启动屏幕镜像
    """
    # 创建一个 Client 对象，设置最大帧率为 1，最大尺寸为 900
    client = Client(max_fps=24, max_size=900)
    # 添加帧处理回调函数
    client.on_frame(on_frame)
    # 启动客户端，开始屏幕镜像
    client.start()

if __name__ == "__main__":
    main()