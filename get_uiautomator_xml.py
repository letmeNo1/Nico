import os
import subprocess
import tempfile

from lxml import etree


class UIStructureError(Exception):
    pass


def get_ui_xml(udid, reload):
    if check_xml_exists(udid) and reload is False:
        rst = "exists"
    else:
        commands = """
                 su
                 cd /data/local/
                 mkdir tmp
                 uiautomator dump --compressed /data/local/tmp/%s_ui.xml
                 """ % udid

        adb_process = subprocess.Popen("adb -s %s shell" % udid, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
        adb_process.stdin.write(commands)
        adb_process.stdin.flush()
        rst, error = adb_process.communicate()
        if rst == "":
            raise UIStructureError("Failed to obtain UI structure")
    print("adb uiautomator was initialized successfully")
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
    rst = os.popen(get_root_cmd).read()
    print(rst)
    command = f'adb -s {udid} pull /data/local/tmp/{udid}_ui.xml {temp_folder}'
    rst = os.popen(command).read()
    print(rst)
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
            print(f"init fail, retry {i} times")

    xml_file_path = pull_ui_xml_to_temp_dir(udid)
    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    return root
