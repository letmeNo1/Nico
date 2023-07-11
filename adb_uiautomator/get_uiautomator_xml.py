import os
import subprocess
import tempfile

from lxml import etree

from adb_uiautomator import logger_config
from adb_uiautomator.logger_config import logger


class UIStructureError(Exception):
    pass


def check_file_exists_in_sdcard(udid, file_name):
    rst = os.popen(f"adb -s {udid} shell ls {file_name}")
    return True if rst.read().find("No such file or directory") > 0 else False


def init_adb_auto(udid):
    start_auto_name = "sdcard/start_auto"
    uiautomator_jar_name = "sdcard/bin/uiautomator.jar"
    lib_path = os.path.dirname(__file__) + "\lib"
    if not check_file_exists_in_sdcard(udid, start_auto_name):
        start_auto_file_path = lib_path + "\\start_auto"
        os.popen(f"adb -s {udid} push {start_auto_file_path} sdcard")
    if not check_file_exists_in_sdcard(udid, uiautomator_jar_name):
        uiautomator_jaro_file_path = lib_path + "\\uiautomator.jar"
        os.popen(f"adb -s {udid} push {uiautomator_jaro_file_path} sdcard/bin")


def get_ui_xml(udid, reload):
    if check_xml_exists(udid) and reload is False:
        rst = "exists"
        logger.debug("already exit")
    else:
        commands = f"""
                 su
                 cd /data/local/
                 mkdir tmp
                 cd ..
                 cd ..
                 cd /sdcard
                 /system/bin/sh start_auto dump --compressed /data/local/tmp/{udid}_ui.xml
                 """
        adb_process = subprocess.Popen("adb -s %s shell" % udid, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
        adb_process.stdin.write(commands)
        adb_process.stdin.flush()
        rst, error = adb_process.communicate()
        if rst == "":
            raise UIStructureError("Failed to obtain UI structure")
    logger.debug("adb uiautomator was initialized successfully")
    return rst


def check_xml_exists(udid):
    temp_folder = tempfile.gettempdir()
    path = temp_folder + f"\\{udid}_ui.xml"
    return os.path.exists(path)


def remove_xml(udid):
    if check_xml_exists(udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"\\{udid}_ui.xml"
        os.remove(path)


def pull_ui_xml_to_temp_dir(udid):
    temp_folder = tempfile.gettempdir()
    get_root_cmd = f"adb -s {udid} root"
    os.popen(get_root_cmd).read()
    command = f'adb -s {udid} pull /data/local/tmp/{udid}_ui.xml {temp_folder}'
    os.popen(command).read()
    return temp_folder + f"\\{udid}_ui.xml"


def get_root_element(udid, reload=False):
    import lxml.etree as ET
    def custom_matches(_, text, pattern):
        import re
        text = str(text)
        return re.search(pattern, text) is not None

    # 创建自定义函数注册器
    custom_functions = etree.FunctionNamespace(None)

    # 注册自定义函数
    custom_functions['matches'] = custom_matches
    for i in range(5):
        try:
            get_ui_xml(udid, reload)
            break
        except UIStructureError:
            logger.debug(f"init fail, retry {i+1} times")

    xml_file_path = pull_ui_xml_to_temp_dir(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root
