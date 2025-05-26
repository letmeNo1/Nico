import argparse
import base64
import os
import socket
import subprocess

from auto_nico.console_scripts.inspector_web.nico_inspector import xml_to_html_list,dump_ui_tree
from auto_nico.android.adb_utils import AdbUtils
from auto_nico.common.send_request import send_http_request
from auto_nico.ios.idb_utils import IdbUtils
from flask import Flask, Response, jsonify, render_template, request
import io
import time
from scrcpy_utils import (
    frame_buffers, buffer_lock, caches, clients, starting, request_cache,
    on_frame, start_client_by_threading, is_device_connected
)

app = Flask(__name__)

def find_available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


@app.route("/dynamic_image")
def get_image():
    device_id = os.getenv("nico_ui_udid")  # 从请求参数中获取 device_id
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


@app.route('/static_image')
def generate_image():
    port = int(os.environ.get('RemoteServerPort'))
    platform = os.environ.get('nico_ui_platform')
    if platform == "android":
        new_data = send_http_request(port, "screenshot", {"quality": 80})
    else:
        new_data = send_http_request(port, "get_jpg_pic", {"compression_quality": 1.0})
    if new_data is None:
        return jsonify({"error": "Failed to get image data"}), 500
    base64_data = base64.b64encode(new_data).decode('utf-8')
    return jsonify({"image": base64_data})

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/refresh_ui_xml')
def refresh_ui_xml():
    root = dump_ui_tree()

    # 构建HTML列表
    html_list = xml_to_html_list(root)

    # 渲染模板并传递构建的HTML列表
    return html_list


@app.route("/action", methods=["POST"])
def action():
    device_id = os.getenv("nico_ui_udid")
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

    return jsonify({"message": f"{data.get('actionType')} sent successfully"})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='设备控制服务')
    parser.add_argument('-s', '--udid', required=True, help='设备 UDID')
    parser.add_argument('-plat', type=str, help='platform "i","iOS","a","android"')

    args = parser.parse_args()
    udid = args.udid
    platform = parser.parse_args().plat
    if platform is None:
        if len(args.udid) > 20:
            platform = "iOS"
        else:
            platform = "android"
    elif platform in ["i", "iOS", "a", "android"]:
        if platform == "i":
            platform = "iOS"
        elif platform == "a":
            platform = "android"
        else:
            pass
    else:
        print('Please enter the correct platform "i","iOS","a","android"')
    os.environ['nico_ui_udid'] = udid
    remote_port = find_available_port()
    os.environ['RemoteServerPort'] = str(remote_port)
    os.environ['nico_ui_platform'] = platform

    if platform == "android":
        adb_utils = AdbUtils(udid)
        adb_utils.clear_tcp_forward_port(remote_port)
        adb_utils.cmd(f'''forward tcp:{remote_port} tcp:8000''')
        adb_utils.check_adb_server()
        adb_utils.install_test_server_package(1.4)
        ime_list = adb_utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            adb_utils.qucik_shell(f"ime disable {ime}")
        commands = f"""adb -s {udid} shell am instrument -r -w -e port {remote_port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        subprocess.Popen(commands, shell=True)
    else:
        idb_utils = IdbUtils(udid)
        port, pid = idb_utils.get_tcp_forward_port()
        if port:
            remote_port = port
            idb_utils.runtime_cache.set_current_running_port(port)
        else:
            idb_utils.set_port_forward(remote_port)
        idb_utils._init_test_server()
    # 启动服务
    port = find_available_port()

    # 启动服务
    app.run(host="0.0.0.0", port=port, threaded=True)