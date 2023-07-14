import os
import tempfile
from datetime import datetime

from adb_uiautomator.utils import Utils, AdbError
from lxml import etree

from adb_uiautomator.logger_config import logger


def check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
<<<<<<< Updated upstream
    rst = utils.shell(f"ls {file_name}")
    if rst.find("No such file or directory") > 0:
        return False
    else:
        return True
=======
    rst = utils.qucik_shell(f"ls {file_name}")
    return rst

>>>>>>> Stashed changes

def init_adb_auto(udid):
    utils = Utils(udid)
    start_auto_name = "sdcard/start_auto.sh"
    uiautomator_jar_name = "sdcard/bin/uiautomator.jar"
    lib_path = os.path.dirname(__file__) + "\libs"
    if not check_file_exists_in_sdcard(udid, start_auto_name):
        start_auto_file_path = lib_path + "\\start_auto.sh"
        utils.cmd(f"push {start_auto_file_path} sdcard")

    if not check_file_exists_in_sdcard(udid, uiautomator_jar_name):
        if not check_file_exists_in_sdcard(udid, "sdcard/bin"):
            utils.qucik_shell("mkdir sdcard/bin")
        uiautomator_jaro_file_path = lib_path + "\\uiautomator.jar"
        utils.cmd(f"push {uiautomator_jaro_file_path} sdcard/bin")
    logger.debug("adb uiautomator was initialized successfully")


def dump_ui_xml(udid, reload, wait_idle):
    utils = Utils(udid)
    if check_xml_exists(udid) and reload is False:
        logger.debug(f"A local {udid}_ui.xml file already exists, And the existing files will be read first")
    else:
<<<<<<< Updated upstream
        rst = os.popen(f"adb -s {udid} shell ls /data/local/tmp").read()
        if rst.find("No such file or directory")>0:
            utils.shell("mkdir /data/local/tmp")
        commands = f"""
                 cd /sdcard
                 /system/bin/sh start_auto.sh dump --waitIdle-{wait_idle} /data/local/tmp/{udid}_ui.xml
                 """
        utils.shell(commands,with_root=True)
        logger.debug("adb uiautomator was initialized successfully")
    return rst
=======
        if check_file_exists_in_sdcard(udid, "/data/local/tmp"):
            utils.qucik_shell("mkdir /data/local/tmp")
        commands = f"""/system/bin/sh /sdcard/start_auto.sh dump --waitIdle-{wait_idle} /data/local/tmp/{udid}_ui.xml"""
        utils.qucik_shell(commands)
    logger.debug("adb uiautomator dump successfully")
>>>>>>> Stashed changes


def check_xml_exists(udid):
    temp_folder = tempfile.gettempdir()
    path = temp_folder + f"\\{udid}_ui.xml"
    return os.path.exists(path)

def get_root(udid):
    os.system(f"adb -s {udid} root")

def get_root(udid):
    os.system(f"adb -s {udid} root")


def remove_ui_xml(udid):
    if check_xml_exists(udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"\\{udid}_ui.xml"
        os.remove(path)


def pull_ui_xml_to_temp_dir(udid):
    utils = Utils(udid)
    temp_folder = tempfile.gettempdir()
    get_root(udid)
    command = f'pull /data/local/tmp/{udid}_ui.xml {temp_folder}'
    utils.cmd(command)
    return temp_folder + f"\\{udid}_ui.xml"


def get_root_node(udid, reload=False, wait_idle=2000):
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
            dump_ui_xml(udid, reload, wait_idle)
            break
        except AdbError:
            logger.debug(f"init fail, retry {i + 1} times")

    xml_file_path = pull_ui_xml_to_temp_dir(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root
<<<<<<< Updated upstream

pull_ui_xml_to_temp_dir("emulator-5554")
=======
>>>>>>> Stashed changes
