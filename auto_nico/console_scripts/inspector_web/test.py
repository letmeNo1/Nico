import cv2
from auto_nico.console_scripts.inspector_web.pyscrcpy import Client  # 修正模块路径
from flask import Flask, Response, render_template
import threading

app = Flask(__name__)
client = None
frame_buffer = None
frame_lock = threading.Lock()


def on_frame(client, frame):
    """
    帧处理回调函数
    """
    with frame_lock:
        global frame_buffer
        frame_buffer = frame


def start_client():
    """
    启动设备连接
    """
    global client
    try:
        client = Client(max_fps=24, max_size=900)  # 可根据需求调整参数
        client.on_frame = on_frame  # 注册回调函数（正确方式）
        client.start()
    except Exception as e:
        print(f"客户端启动出错: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/get_image")
def get_image():
    with frame_lock:
        if frame_buffer is not None:
            try:
                ret, buffer = cv2.imencode('.jpg', frame_buffer)
                if ret:
                    return Response(buffer.tobytes(), mimetype="image/jpeg")
                else:
                    print("图像编码失败")
            except Exception as e:
                print(f"图像编码出错: {e}")
    return Response('{"message": "No frame available yet"}', mimetype='application/json')


if __name__ == "__main__":
    # 启动客户端线程
    client_thread = threading.Thread(target=start_client)
    client_thread.daemon = True
    client_thread.start()

    # 启动 Flask 服务
    app.run(host="0.0.0.0", port=5000)