import argparse
import multiprocessing
import os
import random
import socket

from auto_nico.adb_utils import AdbUtils
from auto_nico.nico import ADBServerError
from auto_nico.send_request import send_tcp_request
from flask import Flask, render_template
import xml.etree.ElementTree as ET

import base64
import subprocess

app = Flask(__name__)


# 递归函数，用于将XML元素及其属性转换为HTML列表项
def xml_to_html_list(element, depth=0):
    # 开始列表项
    random_number = random.randint(100000, 999999)

    html = f'<div class="node" style="text-indent: -1em; padding-left: {depth + 1}em; word-wrap: break-word;"'
    # 如果元素有属性，将它们添加到列表项中
    if element.attrib:
        html += " " + " ".join([f'{k}="{v}"' for k, v in element.attrib.items()])
        html += f'''identifier = "nico_{random_number}"'''

    html += f'><strong style="font-size: 2em;">{element.tag}</strong>'
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


@app.route('/refresh_image')
def refresh_image():
    # 发起TCP请求获取新的二进制数据
    port = int(os.environ.get('RemoteServerPort'))
    new_data = send_tcp_request(port, "get_pic")

    # 使用BytesIO来模拟一个文件对象，并将数据写入到这个对象中
    base64_data = base64.b64encode(new_data)
    return base64_data


@app.route('/refresh_ui_xml')
def refresh_ui_xml():
    port = int(os.environ.get('RemoteServerPort'))
    xml = send_tcp_request(port, "dump_true").replace("class", "class_name")
    # 重新加载XML文件
    root = ET.fromstring(xml.encode('utf-8'))

    # 构建HTML列表
    html_list = xml_to_html_list(root)

    # 渲染模板并传递构建的HTML列表
    return html_list


@app.route('/image')
def generate_image():
    port = int(os.environ.get('RemoteServerPort'))
    new_data = send_tcp_request(port, "get_pic")

    # 使用BytesIO来模拟一个文件对象，并将数据写入到这个对象中
    base64_data = base64.b64encode(new_data)
    return base64_data


@app.route('/')
def show_xml():
    port = int(os.environ.get('RemoteServerPort'))
    xml = send_tcp_request(port, "dump_true").replace("class", "class_name")
    # 重新加载XML文件
    root = ET.fromstring(xml.encode('utf-8'))

    # 构建HTML列表
    html_list = xml_to_html_list(root)

    # 渲染模板并传递构建的HTML列表
    return render_template('xml_template.html', xml_content=html_list)


def run_app(port):
    app.run(debug=False, port=port)


def check_adb_server(udid):
    rst = os.popen("adb devices").read()
    if udid in rst:
        pass
    else:
        raise ADBServerError("no devices connect")


def set_tcp_forward_port(udid, port):
    adb_utils = AdbUtils(udid)
    adb_utils.cmd(f'''forward --remove-all''')

    print(f'''forward tcp:{port} tcp:{port}''')

    adb_utils.cmd(f'''forward tcp:{port} tcp:{port}''')


def install_package(udid):
    def install(udid):
        for i in ["android_test.apk", "app.apk"]:
            print(f"{udid}'s start install {i}")
            lib_path = (os.path.dirname(__file__) + f"\package\{i}").replace("console_scripts\inspector_web", "")
            rst = adb_utils.cmd(f"install -t {lib_path}")
            if rst.find("Success") >= 0:
                print(f"{udid}'s adb install {i} successfully")
            else:
                print(rst)

    version = 1.1
    adb_utils = AdbUtils(udid)
    rst = adb_utils.qucik_shell("dumpsys package hank.dump_hierarchy | grep versionName")
    if "versionName" not in rst:
        install(udid)
    elif version > float(rst.split("=")[-1]):
        print(f"{udid}'s New version detected")
        for i in ["hank.dump_hierarchy", "hank.dump_hierarchy.test"]:
            print(f"{udid}'s start uninstall {i}")
            rst = adb_utils.cmd("uninstall {i}")
            if rst.find("Success") >= 0:
                print(f"{udid}'s adb uninstall {i} successfully")
            else:
                print(rst)
        install(udid)
    rst = adb_utils.qucik_shell("dumpsys package hank.dump_hierarchy | grep versionName")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p1', type=int, help='Remote port to connect to')
    parser.add_argument('-p2', type=int, help='Port to run on')
    parser.add_argument('-s', type=str, help='device_udid')
    udid = parser.parse_args().s
    remote_port = parser.parse_args().p1
    inspect_port = parser.parse_args().p2
    if is_port_in_use(remote_port):
        print(f"Port {remote_port} is already in use")
        return
    if is_port_in_use(inspect_port):
        print(f"Port {inspect_port} is already in use")
        return
    if udid is None:
        print("Please provide a device_udid")
        return
    check_adb_server(udid)
    install_package(udid)
    set_tcp_forward_port(udid, remote_port)
    if remote_port is None:
        print("Please provide a port to connect remote nico server!!!!")
        return
    else:
        if inspect_port is None:
            print("Please provide a port to run inspector UI!!!!")
            return
        else:
            commands = f"""adb -s {udid} shell am instrument -r -w -e port {remote_port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
            subprocess.Popen(commands, shell=True)
            os.environ['RemoteServerPort'] = str(remote_port)
            p = multiprocessing.Process(target=run_app, args=(inspect_port,))
            p.start()