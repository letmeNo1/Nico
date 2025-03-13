import time
import subprocess
import cv2 as cv
from pyscrcpy import Client
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import io
import threading
from cachetools import TTLCache
from io import BytesIO
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app)

# 存储每个设备的帧缓存
frame_buffers = {}
# 用于线程安全的锁
buffer_lock = threading.Lock()

# 缓存字典
caches = {}
clients = {}
starting = {}
request_cache = {}
client: Client


def on_frame(client, frame, device_id):
    global frame_buffers

    # 将帧保存到内存中
    _, buffer = cv.imencode('.jpg', frame)
    with buffer_lock:
        # 降低图片质量为 50%
        output_stream = BytesIO()
        img = Image.open(BytesIO(buffer))
        img.convert("RGB").save(output_stream, format='JPEG', quality=50)
        output_stream.seek(0)

        frame_buffer = output_stream
        # 更新设备的帧缓存
        frame_buffers[device_id] = frame_buffer.getvalue()
        # 更新设备的缓存
        if device_id not in caches:
            # 设置缓存画面最多 120 秒
            caches[device_id] = TTLCache(maxsize=1, ttl=120)
        # 缓存图像数据
        caches[device_id]['image'] = frame_buffers[device_id]
        # 通过WebSocket发送图像数据
        socketio.emit('image_update', {'device_id': device_id, 'image': frame_buffers[device_id].hex()},
                      namespace='/device')


@app.route('/')
def index():
    return render_template('index2.html')


@socketio.on('connect', namespace='/device')
def handle_connect():
    print('Client connected')


@app.route("/action", methods=["POST"])
def action():
    global client
    data = request.get_json()
    x_percent = data.get('xPercent')
    y_percent = data.get('yPercent')
    x_percent = float(x_percent) / 100
    y_percent = float(y_percent) / 100
    x = int(x_percent * int(client.resolution[0]))
    y = int(y_percent * int(client.resolution[1]))
    if data.get('actionType') == 'touch_down':
        client.control.touch_down(x, y)
    elif data.get('actionType') == 'touch_up':
        client.control.touch_up(x, y)
    elif data.get('actionType') == 'touch_move':
        client.control.touch_move(x, y)

    return jsonify({"message": "Click action sent successfully"})


@app.route('/event', methods=['POST'])
def handle_event():
    # 从请求中获取 JSON 数据
    data = request.get_json()

    # 提取事件类型和坐标百分比
    event_type = data.get('eventType')
    x_percent = data.get('xPercent')
    y_percent = data.get('yPercent')

    # 处理接收到的事件数据
    print(f"Received event: {event_type}, x: {x_percent}%, y: {y_percent}%")

    # 返回响应
    return jsonify(
        {"message": "事件已处理", "eventType": event_type, "xPercent": x_percent, "yPercent": y_percent}), 200


@socketio.on('request_image', namespace='/device')
def handle_request_image(data):
    device_id = data.get('device_id', "514f465834593398")
    # 非第一次请求设备画面，判断距离第一次请求是否超过 2 秒，没超过则等待，超过则大概率 pyscrcpy server 已经启动好了
    if device_id in request_cache:
        sequence, request_time = request_cache[device_id]
        if sequence == 1 and (time.time() - request_time) <= 2:
            socketio.emit('status_update', {'message': '正在初始化，请稍等几秒中！'}, namespace='/device')
            return
        if sequence == 1 and (time.time() - request_time) > 2:
            new_sequence = sequence + 1
            request_cache[device_id] = (new_sequence, time.time())
    # 第一次请求设备画面，设置请求顺序为 1
    if device_id not in request_cache:
        request_cache[device_id] = (1, time.time())

    # 1. 当设备未连接到电脑的情况
    if not is_device_connected(device_id):
        socketio.emit('status_update', {'message': '设备未连接'}, namespace='/device')
        return
    # 2. 当 pyscrcpy server 没启动的情况
    if device_id not in starting or device_id not in clients:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        socketio.emit('status_update', {'message': 'scrcpy server 尚未启动，启动', 'starting': starting},
                      namespace='/device')
        return

    is_starting, starting_time = starting[device_id]
    if is_starting and (time.time() - starting_time) <= 2:
        socketio.emit('status_update', {'message': 'scrcpy server 启动中', 'starting': starting}, namespace='/device')
        return
    if is_starting and (time.time() - starting_time) > 2:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        socketio.emit('status_update', {'message': 'scrcpy server 启动超时，再次启动', 'starting': starting},
                      namespace='/device')
        return
    # 5. 设备中途掉线、恢复的情况
    if not is_starting and not clients[device_id].alive:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        socketio.emit('status_update', {'message': 'scrcpy server 掉线，启动中', 'starting': starting},
                      namespace='/device')
        return
    # 6. 画面超过缓存时间（120 秒），强制重启
    starting[device_id] = (True, time.time())
    start_client_by_threading(device_id)
    socketio.emit('status_update', {'message': '画面超时，强制重启 scrcpy server', 'starting': starting},
                  namespace='/device')


client_started_event = threading.Event()


def start_client(device_id):
    if device_id in clients:
        clients[device_id].stop()
        del clients[device_id]
    if device_id in caches:
        del caches[device_id]

    try:
        global client
        client = Client(device=device_id, max_fps=25, max_size=900, stay_awake=True)
        client.on_frame(lambda c, f: on_frame(c, f, device_id))  # 传递设备 ID
        clients[device_id] = client
        client.start()

        # 通知主线程客户端已启动
        client_started_event.set()
    except Exception as e:
        print(e)
        client_started_event.clear()


def start_client_by_threading(device_id):
    client_thread = threading.Thread(target=start_client, args=(device_id,))
    client_thread.daemon = True
    client_thread.start()

    while device_id not in clients:
        time.sleep(0.03)
    print("pyscrcpy server 已启动~")


def is_device_connected(device_id):
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        print(result)
        devices_output = result.stdout.strip()
        return device_id in devices_output
    except subprocess.CalledProcessError as e:
        print(f"Error executing adb command: {e}")
        return False


if __name__ == '__main__':
    # 启动Flask-SocketIO应用
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
