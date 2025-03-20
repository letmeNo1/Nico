import os
import time
import subprocess
import cv2 as cv
from pyscrcpy import Client
import io
import threading
from cachetools import TTLCache
from io import BytesIO
from PIL import Image

# 存储每个设备的帧缓存
frame_buffers = {}
# 用于线程安全的锁
buffer_lock = threading.Lock()

# 缓存字典
caches = {}
clients = {}
starting = {}
request_cache = {}


def on_frame(aa, frame, device_id):
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


client_started_event = threading.Event()


def start_client(device_id):
    if device_id in clients:
        clients[device_id].stop()
        del clients[device_id]
    if device_id in caches:
        del caches[device_id]

    try:
        client = Client(device=device_id, max_fps=24, max_size=900, stay_awake=True)

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
        time.sleep(0.5)

    print("pyscrcpy server 已启动~")


def is_device_connected(device_id):
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)

        devices_output = result.stdout.strip()
        return device_id in devices_output
    except subprocess.CalledProcessError as e:
        print(f"Error executing adb command: {e}")
        return False


def get_image(device_id):
    # 非第一次请求设备画面，判断距离第一次请求是否超过 2 秒，没超过则等待，超过则大概率 pyscrcpy server 已经启动好了
    if device_id in request_cache:
        sequence, request_time = request_cache[device_id]
        if sequence == 1 and (time.time() - request_time) <= 2:
            return {"message": "正在初始化，请稍等几秒中！"}
        if sequence == 1 and (time.time() - request_time) > 2:
            new_sequence = sequence + 1
            request_cache[device_id] = (new_sequence, time.time())
    # 第一次请求设备画面，设置请求顺序为 1
    if device_id not in request_cache:
        request_cache[device_id] = (1, time.time())

    # 1. 当设备未连接到电脑的情况
    if not is_device_connected(device_id):
        return {"message": "设备未连接"}
    # 2. 当 pyscrcpy server 没启动的情况
    if device_id not in starting or device_id not in clients:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return {"message": "scrcpy server 尚未启动，启动", "starting": starting}
    # 3. pyscrcpy server 已启动，设备连接正常的情况
    if clients[device_id].alive:
        starting[device_id] = (False, time.time())

        with buffer_lock:
            if device_id in caches and 'image' in caches[device_id]:
                image_data = caches[device_id]['image']
                return image_data
    # 4. 利用缓存，避免拔插导致的一直 keep 在 starting 状态
    is_starting, starting_time = starting[device_id]
    if is_starting and (time.time() - starting_time) <= 2:
        return {"message": "scrcpy server 启动中", "starting": starting}
    if is_starting and (time.time() - starting_time) > 2:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return {"message": "scrcpy server 启动超时，再次启动", "starting": starting}
    # 5. 设备中途掉线、恢复的情况
    if not is_starting and not clients[device_id].alive:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return {"message": "scrcpy server 掉线，启动中", "starting": starting}
    # 6. 画面超过缓存时间（120 秒），强制重启
    starting[device_id] = (True, time.time())
    start_client_by_threading(device_id)
    return {"message": "画面超时，强制重启 scrcpy server", "starting": starting}


def action(data, device_id):
    client = clients.get(device_id)
    if client is None:
        return {"message": "Client not found"}
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
    elif data.get("actionType") == "touch_move":
        client.control.touch_move(x, y)

    return {"message": "Click action sent successfully"}
