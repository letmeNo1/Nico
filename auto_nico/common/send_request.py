import socket
from auto_nico.common.logger_config import logger


def send_tcp_request(port, message):
    # logger.debug(f"send_tcp_request: {port} {message}")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())

        # 接收服务器响应
        chunks = []
        while True:
            chunk = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
            if not chunk:
                break
            chunks.append(chunk)
        client_socket.close()
        response = b''.join(chunks)
        if "get_jpg_pic" in message or message == "stop_recording" or "get_png_pic" in message:
            return response
        else:
            response = response.decode()
            return response

    except ConnectionRefusedError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"
    except ConnectionResetError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"

# a = send_tcp_request(9960, "device_info:get_output_volume")
# print(a)


#     print(a)
#     print(f"done{i}")

# import cv2
# import numpy as np
# import time
#
# send_tcp_request(8200,"start_recording")
# a = send_tcp_request(9337,'''find_element_by_query:com.apple.Preferences:xpath:Window[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Other[0]/Table[0]/Cell[1]/Button[0]''')
# print(a)
# time.sleep(3)
# send_tcp_request(8200,"stop_recording")
# prin

# def display_image_continuous():
#     while True:
#         # 发送请求并获取图像数据
#         byte_data = send_tcp_request(8200, "get_pic")
#
#         # 将字节数据转换为图像
#         image = bytes_to_image(byte_data)
#
#         # 使用 OpenCV 展示图像
#         cv2.imshow('Image', image)
#
#         # 每次迭代后等待一秒
#
#         # 按下 'q' 键退出循环
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     cv2.destroyAllWindows()
#
# # 使用函数
# display_image_continuous()