from flask import Flask, Response, jsonify, render_template, request
import io
import time
from scrcpy_utils import (
    frame_buffers, buffer_lock, caches, clients, starting, request_cache,
    on_frame, start_client_by_threading, is_device_connected
)

app = Flask(__name__)


@app.route("/image")
def get_image():
    device_id = "emulator-5554"  # 默认设备 ID
    # 非第一次请求设备画面，判断距离第一次请求是否超过 2 秒，没超过则等待，超过则大概率 pyscrcpy server 已经启动好了
    if device_id in request_cache:
        sequence, request_time = request_cache[device_id]
        if sequence == 1 and (time.time() - request_time) <= 2:
            return jsonify({"message": "正在初始化，请稍等几秒中！"})
        if sequence == 1 and (time.time() - request_time) > 2:
            new_sequence = sequence + 1
            request_cache[device_id] = (new_sequence, time.time())
    # 第一次请求设备画面，设置请求顺序为 1
    if device_id not in request_cache:
        request_cache[device_id] = (1, time.time())

    # 1. 当设备未连接到电脑的情况
    if not is_device_connected(device_id):
        return jsonify({"message": "设备未连接"})
    # 2. 当 pyscrcpy server 没启动的情况
    if device_id not in starting or device_id not in clients:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return jsonify({"message": "scrcpy server 尚未启动，启动", "starting": starting})
    # 3. pyscrcpy server 已启动，设备连接正常的情况
    if clients[device_id].alive:
        starting[device_id] = (False, time.time())

        with buffer_lock:
            if device_id in caches and 'image' in caches[device_id]:
                image_data = caches[device_id]['image']
                return Response(io.BytesIO(image_data), mimetype="image/jpeg")
    # 4. 利用缓存，避免拔插导致的一直 keep 在 starting 状态
    is_starting, starting_time = starting[device_id]
    if is_starting and (time.time() - starting_time) <= 2:
        return jsonify({"message": "scrcpy server 启动中", "starting": starting})
    if is_starting and (time.time() - starting_time) > 2:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return jsonify({"message": "scrcpy server 启动超时，再次启动", "starting": starting})
    # 5. 设备中途掉线、恢复的情况
    if not is_starting and not clients[device_id].alive:
        starting[device_id] = (True, time.time())
        start_client_by_threading(device_id)
        return jsonify({"message": "scrcpy server 掉线，启动中", "starting": starting})
    # 6. 画面超过缓存时间（120 秒），强制重启
    starting[device_id] = (True, time.time())
    start_client_by_threading(device_id)
    return jsonify({"message": "画面超时，强制重启 scrcpy server", "starting": starting})


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/action", methods=["POST"])
def action():
    device_id = "emulator-5554"  # 默认设备 ID
    if device_id not in clients:
        return jsonify({"message": f"设备 {device_id} 的客户端未找到"}), 400
    client = clients[device_id]
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
    elif data.get("actionType") == "touch_move":
        client.control.touch_move(x, y)

    return jsonify({"message": "Click action sent successfully"})


if __name__ == '__main__':
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=3448)