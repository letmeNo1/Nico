import hashlib
import os
import socket
import subprocess
import tempfile
import time

from nico.send_request import send_tcp_request
from nico.utils import Utils, AdbError
from lxml import etree

from nico.logger_config import logger




def __check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
    rst = utils.qucik_shell(f"ls {file_name}")
    return rst


def __dump_ui_xml(port):
    response = send_tcp_request(port, "dump")
    if "xxx.xml" in response:
        logger.debug("adb uiautomator dump successfully")
    else:
        raise AdbError("adb uiautomator dump failed")


def __get_root_md5(port):
    response = send_tcp_request(port, "get_root")
    if "[" in response:
        logger.debug("get root successfully")
        md5_hash = hashlib.md5(response.encode()).hexdigest()
        return md5_hash
    else:
        raise AdbError("get root md5 failed")
    #


def __get_xml_file_path_in_tmp(udid):
    return tempfile.gettempdir() + f"/{udid}_ui.xml"


def __pull_ui_xml_to_temp_dir(udid, port, force_reload):
    if force_reload:
        command2 = f'adb -s {udid} shell rm /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml'
        os.popen(command2).read()
        __dump_ui_xml(port)
        temp_file = tempfile.gettempdir() + f"/{udid}_ui.xml"
        command = f'adb -s {udid} pull /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/xxx.xml {temp_file}'
        rst = os.popen(command).read()
        if rst.find("error") > 0:
            raise AdbError(rst)

    # print(rst)
    # return temp_file


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
    __pull_ui_xml_to_temp_dir(udid, port,force_reload)
    xml_file_path = __get_xml_file_path_in_tmp(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root
