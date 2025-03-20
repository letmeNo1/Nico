import time
import subprocess
import cv2 as cv
from pyscrcpy import Client
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
client: Client


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
            caches[device_id] = TTLCache(maxsize=24, ttl=120)
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
        global client
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
