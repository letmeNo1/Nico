import hashlib
import os
import socket
import subprocess
import tempfile
import time

from nico.utils import Utils, AdbError
from lxml import etree

from nico.logger_config import logger


def __check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
    rst = utils.qucik_shell(f"ls {file_name}")
    return rst


def __send_tcp_request(port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", port))
    client_socket.sendall(message.encode())
    client_socket.sendall('\n'.encode())

    # 接收服务器响应
    response = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
    client_socket.close()
    return response.decode()


def init_adb_auto(udid, port):
    utils = Utils(udid)
    dict = {
        "app.apk": "hank.dump_hierarchy",
        "android_test.apk": "hank.dump_hierarchy.test",
    }
    rst = utils.qucik_shell("pm list packages hank.dump_hierarchy")
    if rst.find("not found") > 0:
        raise AdbError(rst)

    for i in ["android_test.apk", "app.apk"]:
        if f"package:{dict.get(i)}" not in rst:
            lib_path = os.path.dirname(__file__) + f"\libs\{i}"
            rst = utils.cmd(f"install {lib_path}")
            if rst.find("Success") >= 0:
                logger.debug(f"adb install {i} successfully")
            else:
                logger.error(rst)
        else:
            logger.debug(f"{i} already install")

    for _ in range(10):
        rst = utils.cmd(f'''forward --list | find "{port}"''')
        if udid not in rst:
            utils.cmd(f'''forward tcp:{port} tcp:{port}''')
        else:
            logger.debug(f"tcp already forward")
            break

    try:
        response = __send_tcp_request(port, "content=print")
    except ConnectionResetError:
        response = None
    commands = f"""adb -s {udid} shell am instrument -r -w -e port 9000 -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
    if response is None:
        subprocess.Popen(commands, shell=True)
        time.sleep(1)
    else:
        logger.debug(f"Server is ready")

    logger.debug("adb uiautomator was initialized successfully")


def __dump_ui_xml(port):
    response = __send_tcp_request(port, "dump")
    if "xxx.xml" in response:
        logger.debug("adb uiautomator dump successfully")
    else:
        raise AdbError("adb uiautomator dump failed")


def __get_root_md5(port):
    response = __send_tcp_request(port, "get_root")
    if "[" in response:
        logger.debug("get root successfully")
        md5_hash = hashlib.md5(response.encode()).hexdigest()
        return md5_hash
    else:
        raise AdbError("get root md5 failed")
    #


def __get_xml_file_path_in_tmp(udid):
    return tempfile.gettempdir() + f"/{udid}_ui.xml"


def __pull_ui_xml_to_temp_dir(udid, port):
    pre_root = os.getenv("current_root")
    cur_root = __get_root_md5(port)
    if pre_root is None or pre_root != cur_root:
        command2 = f'adb -s {udid} shell rm /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml'
        os.popen(command2).read()
        __dump_ui_xml(port)
        temp_file = tempfile.gettempdir() + f"/{udid}_ui.xml"
        command = f'adb -s {udid} pull /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml {temp_file}'
        rst = os.popen(command).read()
        if rst.find("error") > 0:
            raise AdbError(rst)
    os.environ["current_root"] = cur_root

    # print(rst)
    # return temp_file


def get_root_node(udid, port):
    import lxml.etree as ET
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    __pull_ui_xml_to_temp_dir(udid, port)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root
