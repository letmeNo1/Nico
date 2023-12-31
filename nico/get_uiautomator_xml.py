import hashlib
import os
import socket
import subprocess
import tempfile
import time

from nico.send_request import send_tcp_request
from nico.utils import Utils, NicoError
from lxml import etree

from nico.logger_config import logger


def __restart_nico_server(udid, port):
    utils = Utils(udid)
    commands = f"""adb -s {udid} shell am instrument -r -w -e port {exists_port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
    subprocess.Popen(commands, shell=True)
    for _ in range(10):
        response = send_tcp_request(exists_port, "print")
        if "200" in response:
            logger.debug(f"{udid}'s test server is ready")
            break
        time.sleep(1)
    logger.debug(f"{udid}'s adb uiautomator was initialized successfully")
    return exists_port


def __check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
    rst = utils.qucik_shell(f"ls {file_name}")
    return rst


def __dump_ui_xml(udid, port):
    for _ in range(5):
        response = send_tcp_request(port, "dump")
        if "xxx.xml" in response:
            logger.debug("adb uiautomator dump successfully")
            return 1
        else:
            logger.debug("adb uiautomator dump fail")
        port = __restart_nico_server(udid, port)


def __get_root_md5(port):
    response = send_tcp_request(port, "get_root")
    if "[" in response:
        logger.debug("get root successfully")
        md5_hash = hashlib.md5(response.encode()).hexdigest()
        return md5_hash
    else:
        raise NicoError("get root md5 failed")
    #


def __get_xml_file_path_in_tmp(udid):
    return tempfile.gettempdir() + f"/{udid}_ui.xml"


def __pull_ui_xml_to_temp_dir(udid, port, force_reload):
    if force_reload:
        command2 = f'adb -s {udid} shell rm /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml'
        os.popen(command2).read()
        __dump_ui_xml(udid, port)
        temp_file = tempfile.gettempdir() + f"/{udid}_ui.xml"
        command = f'adb -s {udid} pull /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml {temp_file}'
        rst = os.popen(command).read()
        if rst.find("error") > 0:
            raise NicoError(rst)


def get_root_node(udid, port, force_reload=False):
    import lxml.etree as ET
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    __pull_ui_xml_to_temp_dir(udid, port, force_reload)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root


def get_root_node_with_output(udid, port, force_reload=False):
    import lxml.etree as ET
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    __pull_ui_xml_to_temp_dir(udid, port, force_reload)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    return xml_file_path
