import cv2
import numpy as np


def bytes_to_image(byte_data):
    # 将字节数据转换为 NumPy 数组
    nparr = np.frombuffer(byte_data, np.uint8)

    # 使用 OpenCV 解码图像
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return img_np
def images_to_video(images, output_file, fps=10):
    # 获取图像的大小
    height, width, _ = images[0].shape

    # 创建 VideoWriter 对象
    video = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # 将每个图像写入视频
    for image in images:
        video.write(image)

    # 释放 VideoWriter
    video.release()