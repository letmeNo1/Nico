import os
import re
import tempfile
import time
from datetime import datetime

from adb_uiautomator.utils import Utils, AdbError
from lxml import etree

from adb_uiautomator.logger_config import logger


<<<<<<< HEAD


import os
import subprocess
import tempfile
=======
def check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
    rst = utils.qucik_shell(f"ls {file_name}")
    return rst
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6

from adb_uiautomator.utils import Utils, AdbError
from lxml import etree

from adb_uiautomator.logger_config import logger



def check_file_exists_in_sdcard(udid, file_name):
    utils = Utils(udid)
    try:
        utils.shell(f"ls {file_name}")
        return True
    except:
        return False

def init_adb_auto(udid):
    utils = Utils(udid)
<<<<<<< HEAD
    start_auto_name = "sdcard/start_auto.sh"
    uiautomator_jar_name = "sdcard/bin/uiautomator.jar"
    lib_path = os.path.dirname(__file__) + "\libs"
    if not check_file_exists_in_sdcard(udid, start_auto_name):
        start_auto_file_path = lib_path + "\\start_auto.sh"
        os.popen(f"adb -s {udid} push {start_auto_file_path} sdcard")
    if not check_file_exists_in_sdcard(udid, uiautomator_jar_name):
        if not check_file_exists_in_sdcard(udid,"sdcard/bin"):
            utils.shell("mkdir sdcard/bin")
        uiautomator_jaro_file_path = lib_path + "\\uiautomator.jar"
        os.popen(f"adb -s {udid} push {uiautomator_jaro_file_path} sdcard/bin")

def dump_ui_xml(udid, reload,wait_idle):
    utils = Utils(udid)
    if check_xml_exists(udid) and reload is False:
        rst = "exists"
        logger.debug(f"A local {udid}_ui.xml file already exists, And the existing files will be read first")
    else:
        rst = os.popen(f"adb -s {udid} shell ls /data/local/tmp").read()
        if rst.find("No such file or directory")>0:
            utils.shell("mkdir /data/local/tmp")
        commands = f"""
                 su
                 cd /sdcard
                 /system/bin/sh start_auto.sh dump --waitIdle-{wait_idle} /data/local/tmp/{udid}_ui.xml
                 """
        utils.shell(commands,with_root=True)
        logger.debug("adb uiautomator was initialized successfully")
    return rst
=======
    dict = {
        "app.apk":"hank.dump_hierarchy",
        "android_test.apk": "hank.dump_hierarchy.test",

    }
    rst = utils.qucik_shell("pm list packages hank.dump_hierarchy").split("\n")

    for i in ["android_test.apk","app.apk"]:
        # print(dict.get(i))
        if f"package:{dict.get(i)}" not in rst:
            lib_path = os.path.dirname(__file__) + f"\libs\{i}"
            utils.cmd(f"install {lib_path}")
            logger.debug(f"adb install {i} successfully")

    logger.debug("adb uiautomator was initialized successfully")
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6


def dump_ui_xml(udid, reload):
    utils = Utils(udid)
    if check_xml_exists() and reload is False:
        logger.debug(f"A local file already exists, And the existing files will be read first")
    else:
        commands = f"""am instrument -w -r -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        utils.qucik_shell(commands)
        logger.debug("adb uiautomator dump successfully")


def check_xml_exists():
    temp_folder = tempfile.gettempdir()
    path = temp_folder + f"/2.xml"
    return os.path.exists(path)

<<<<<<< HEAD

def remove_ui_xml(udid):
    if check_xml_exists(udid):
=======
def remove_ui_xml():
    if check_xml_exists():
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"/2.xml"
        os.remove(path)

def pull_ui_xml_to_temp_dir(udid):
    utils = Utils(udid)
<<<<<<< HEAD
    temp_folder = tempfile.gettempdir()
    command = f'pull /data/local/tmp/{udid}_ui.xml {temp_folder}'
    utils.cmd(command)
    return temp_folder + f"\\{udid}_ui.xml"


def get_root_node(udid, reload=False,wait_idle=2000):
=======
    temp_file = tempfile.gettempdir() + f"/{udid}_ui.xml"
    command = f'pull /storage/emulated/0/Android/data/hank.dump_hierarchy/cache/2.xml {temp_file}'
    utils.cmd(command)
    return temp_file


def get_root_node(udid, reload=False):
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
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
<<<<<<< HEAD
            dump_ui_xml(udid, reload,wait_idle)
            break
        except AdbError:
            logger.debug(f"init fail, retry {i+1} times")
=======
            dump_ui_xml(udid, reload)
            break
        except AdbError:
            logger.debug(f"init fail, retry {i + 1} times")
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6

    xml_file_path = pull_ui_xml_to_temp_dir(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
<<<<<<< HEAD
    return root

# get_ui_xml("290aa9aac2a29a1e",True)
=======
    return root
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
