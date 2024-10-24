import argparse
import json
import multiprocessing
import os
import random
import time

import lxml.etree as ET

import base64
import subprocess

from flask import Flask, render_template, request

from auto_nico.common.common_utils import is_port_in_use
from auto_nico.common.send_request import send_tcp_request
from auto_nico.ios.XCUIElementType import get_element_type_by_value
from auto_nico.ios.tools.format_converter import converter

from auto_nico.android.adb_utils import AdbUtils
from auto_nico.ios.idb_utils import IdbUtils

from auto_nico.android.tools.format_converter import add_xpath_att

app = Flask(__name__)


# 递归函数，用于将XML元素及其属性转换为HTML列表项
def xml_to_html_list(element, depth=0):
    # 开始列表项
    random_number = random.randint(100000, 999999)
    html = f'<div class="node" style="text-indent: -1em; padding-left: {depth + 1}em; word-wrap: break-word;"'
    # 如果元素有属性，将它们添加到列表项中
    if element.attrib:
        html += " " + " ".join([f'{k}="{v}"' for k, v in element.attrib.items()])
        html += f'''identifier_number = "nico_{random_number}"'''
    if depth != 0:
        content = element.tag
    else:
        html += f'''id = "Title" '''
        html += f'''current_package_name = {os.environ.get("current_package_name")} '''
        html += f'''nico_ui_platform = {os.environ.get('nico_ui_platform')}'''
        content = f"{element.tag} for {os.environ.get('nico_ui_platform')}"

    html += f'><strong style="font-size: 2em;">{content}</strong>'
    # 如果元素有属性，将它们作为文本添加
    if element.attrib:
        html += " (Attributes: "
        html += ", ".join([f'{k}="{v}"' for k, v in element.attrib.items()])
        html += ")"
    # 如果元素有文本内容，将其添加到列表项中
    if element.text and element.text.strip():
        html += f" - Text: {element.text.strip()}"

    html += "</div>"
    # 处理子元素
    children = list(element)
    if children:
        for child in children:
            html += xml_to_html_list(child, depth + 1)
    return html


def dump_ui_tree():
    platform = os.environ.get('nico_ui_platform')
    udid = os.environ.get("nico_ui_udid")
    idb_utils = IdbUtils(udid)

    port = int(os.environ.get('RemoteServerPort'))
    if platform == "android":
        xml = send_tcp_request(port, "dump_tree:true").replace("class", "class_name").replace("resource-id=",
                                                                                              "id=").replace(
            "content-desc=", "content_desc=")
        root = add_xpath_att(ET.fromstring(xml.encode('utf-8')))

    else:
        bundle_list = idb_utils.get_app_list()
        command = "get_current_bundleIdentifier"
        for item in bundle_list:
            if item:
                item = item.split(" ")[0]
                command = command + f":{item}"
        package_name = send_tcp_request(port, command)
        os.environ['current_package_name'] = package_name

        xml = send_tcp_request(port, f"dump_tree:{package_name}")
        xml = converter(xml)
        root = ET.fromstring(xml.encode('utf-8'))
    return root


@app.route('/refresh_image')
def refresh_image():
    port = int(os.environ.get('RemoteServerPort'))
    platform = os.environ.get('nico_ui_platform')
    if platform == "android":
        new_data = send_tcp_request(port, "get_png_pic:1")
    else:
        new_data = send_tcp_request(port, "get_jpg_pic:1.0")
    base64_data = base64.b64encode(new_data)
    return base64_data


@app.route('/refresh_ui_xml')
def refresh_ui_xml():
    root = dump_ui_tree()

    # 构建HTML列表
    html_list = xml_to_html_list(root)

    # 渲染模板并传递构建的HTML列表
    return html_list


@app.route('/image')
def generate_image():
    port = int(os.environ.get('RemoteServerPort'))
    platform = os.environ.get('nico_ui_platform')
    if platform == "android":
        new_data = send_tcp_request(port, "get_png_pic:100")
    else:
        new_data = send_tcp_request(port, "get_jpg_pic:1.0")

    # 使用BytesIO来模拟一个文件对象，并将数据写入到这个对象中
    base64_data = base64.b64encode(new_data)
    return base64_data


@app.route('/get_element_attribute')
def get_element_attribute():
    id = request.args.get('id')
    xpath = request.args.get("xpath")
    port = int(os.environ.get('RemoteServerPort'))
    if xpath is None or xpath == "null":
        return ""
    new_data = send_tcp_request(port, f"find_element_by_query:{id}:xpath:{xpath}")
    if new_data == "":
        return ""
    new_data_dict = dict(json.loads(new_data))
    new_data_dict.pop('children', None)
    for att in ["title", "label"]:
        value = new_data_dict.pop(att)
        text = value if value != "" else ""
    frame = new_data_dict.pop("frame")
    new_data_dict.update({"text": text})
    new_data_dict.update({"class_name": get_element_type_by_value(new_data_dict.pop("elementType"))})
    new_data_dict.update({"bounds": f'[{frame.get("X")},{frame.get("Y")}][{frame.get("Width")},{frame.get("Height")}]'})

    return new_data_dict


@app.route("/android_excute_action")
def android_excute_action():
    action = request.args.get('action')
    if action == "click":
        x = request.args.get("x")
        y = request.args.get("y")
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input tap {x} {y}''')
        return "excute sucessful"
    elif action == "input":
        inputValue = request.args.get("inputValue")
        inputValue = inputValue.replace("&", "\&").replace("\"", "")
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input text {inputValue}''')
        return "excute sucessful"

    elif action == "home":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_HOME''')
        return "excute sucessful"

    elif action == "back":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_BACK''')
        return "excute sucessful"

    elif action == "menu":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_MENU''')
        return "excute sucessful"

    elif action == "switch_app":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_APP_SWITCH''')
        return "excute sucessful"

    elif action == "switch_app":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_APP_SWITCH''')
        return "excute sucessful"

    elif action == "volume_up":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_VOLUME_UP''')
        return "excute sucessful"

    elif action == "volume_down":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_VOLUME_DOWN''')
        return "excute sucessful"

    elif action == "power":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_POWER''')
        return "excute sucessful"

    elif action == "delete_text":
        udid = os.environ.get("nico_ui_udid")
        adb_utils = AdbUtils(udid)
        adb_utils.shell(f'''input keyevent KEYCODE_DEL''')
        return "excute sucessful"


@app.route('/')
def show_xml():
    root = dump_ui_tree()
    # 构建HTML列表
    html_list = xml_to_html_list(root)

    # 渲染模板并传递构建的HTML列表
    return render_template('xml_template.html', xml_content=html_list)


def run_app(port):
    app.run(debug=False, port=port)


def set_tcp_forward_port(udid, port):
    platform = os.environ.get('nico_ui_platform')
    if platform == "android":
        adb_utils = AdbUtils(udid)
        adb_utils.cmd(f'''forward tcp:{port} tcp:{port}''')
    else:
        commands = f"""tidevice --udid {udid} relay {port} {port}"""
        subprocess.Popen(commands, shell=True)
    print(f'''forward tcp:{port} tcp:{port}''')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p1', type=int, help='Remote port to connect to')
    parser.add_argument('-p2', type=int, help='Port to run on')
    parser.add_argument('-s', type=str, help='device_udid')
    parser.add_argument('-plat', type=str, help='platform "i","iOS","a","android"')

    udid = parser.parse_args().s
    # udid = "dbde29f994e7ed382a592d6504eb9a4e9e4eb660"

    platform = parser.parse_args().plat
    if platform is None:
        if len(udid) > 20:
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

    os.environ['nico_ui_platform'] = platform

    remote_port = parser.parse_args().p1
    inspect_port = parser.parse_args().p2
    if remote_port is None:
        random_number = random.randint(9000, 9999)
        remote_port = random_number

    if inspect_port is None:
        random_number = random.randint(9000, 9999)
        inspect_port = random_number

    if udid is None:
        print("Please provide a device_udid")
        return
    if remote_port is None:
        print("Please provide a port to connect remote nico server!!!!")
        return
    if inspect_port is None:
        print("Please provide a port to run inspector UI!!!!")
        return
    if is_port_in_use(remote_port):
        print(f"Port {remote_port} is already in use")
        return
    if is_port_in_use(inspect_port):
        print(f"Port {inspect_port} is already in use")
        return

    if platform == "android":
        adb_utils = AdbUtils(udid)
        adb_utils.clear_tcp_forward_port(remote_port)
        adb_utils.cmd(f'''forward tcp:{remote_port} tcp:{remote_port}''')
        adb_utils.check_adb_server()
        adb_utils.install_test_server_package(1.3)
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
        else:
            idb_utils.set_port_forward(remote_port)
        test_server_package_dict = idb_utils.get_test_server_package()

        commands = f"""tidevice  --udid {udid} xcuitest --bundle-id {test_server_package_dict.get("test_server_package")} --target-bundle-id {test_server_package_dict.get("main_package")} -e USE_PORT:{remote_port}"""
        subprocess.Popen(commands, shell=True)
    os.environ['RemoteServerPort'] = str(remote_port)
    os.environ['nico_ui_udid'] = udid
    time.sleep(5)

    p = multiprocessing.Process(target=run_app, args=(inspect_port,))
    p.start()
