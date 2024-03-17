import hashlib
import os
import subprocess
import tempfile
import time

from auto_nico.send_request import send_tcp_request
from auto_nico.adb_utils import AdbUtils, NicoError
from lxml import etree

from auto_nico.logger_config import logger


def __restart_nico_server(udid, port):
    adb_utils = AdbUtils(udid)
    for _ in range(5):
        rst = adb_utils.cmd(f'''forward --list | find "{port}"''')
        if udid not in rst:
            adb_utils.cmd(f'''forward tcp:{port} tcp:{port}''')
        else:
            logger.debug(f"{udid}'s tcp already forward tcp:{port} tcp:{port}")
            break
    if rst.find("not found") > 0:
        raise NicoError(rst)
    commands = f"""adb -s {udid} shell am instrument -r -w -e port {port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
    nico_server = subprocess.Popen(commands, shell=True)
    for _ in range(10):
        response = send_tcp_request(port, "print")
        if "200" in response:
            logger.debug(f"{udid}'s test server is ready")
            break
        time.sleep(1)
    logger.debug(f"{udid}'s adb uiautomator was initialized successfully")
    return port, nico_server


def __check_file_exists_in_sdcard(udid, file_name):
    adb_utils = AdbUtils(udid)
    rst = adb_utils.qucik_shell(f"ls {file_name}")
    return rst


def __dump_ui_xml(udid, port, compressed):
    for _ in range(5):
        response = send_tcp_request(port, f"dump_{str(compressed).lower()}")
        if "xxx.xml" in response:
            return 1
        else:
            logger.debug("uiautomator dump fail")
        port = __restart_nico_server(udid, port)


def __get_root_md5(port):
    response = send_tcp_request(port, "get_root")
    if "[" in response:
        md5_hash = hashlib.md5(response.encode()).hexdigest()
        return md5_hash
    else:
        raise NicoError("get root md5 failed")
    #


def __get_xml_file_path_in_tmp(udid):
    return tempfile.gettempdir() + f"/{udid}_ui.xml"


def __pull_ui_xml_to_temp_dir(udid, port, compressed, force_reload):
    if force_reload:
        command2 = f'adb -s {udid} shell rm /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml'
        os.popen(command2).read()
        __dump_ui_xml(udid, port, compressed)
        temp_file = tempfile.gettempdir() + f"/{udid}_ui.xml"
        command = f'adb -s {udid} pull /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml {temp_file}'
        rst = os.popen(command).read()
        if rst.find("error") > 0:
            raise NicoError(rst)


def get_root_node(udid, port, compress, force_reload=False):
    import lxml.etree as ET
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    __pull_ui_xml_to_temp_dir(udid, port, compress, force_reload)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root


def get_root_node_with_output(udid, port, compressed, force_reload=False):
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    __pull_ui_xml_to_temp_dir(udid, port, compressed, force_reload)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    return xml_file_path
