import os
import tempfile
import time

from nico.utils import Utils

from nico.nico_proxy import NicoProxy
from nico.get_uiautomator_xml import init_adb_auto


def remove_ui_xml(udid):
    if __check_xml_exists(udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"/{udid}_ui.xml"
        os.remove(path)


def __check_xml_exists(udid):
    temp_folder = tempfile.gettempdir()
    path = temp_folder + f"/{udid}_ui.xml"
    return os.path.exists(path)


class UIStructureError(Exception):
    pass


class AdbAutoNico:
    def __init__(self, udid, port=9000):
        self.udid = udid
        self.port = port
        init_adb_auto(self.udid, port)
        remove_ui_xml(self.udid)
        self.close_keyboard()

    def close_keyboard(self):
        utils = Utils(self.udid)
        ime_list = utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            utils.qucik_shell(f"ime disable {ime}")

    # os.popen(commands)  # 执行外部命令
    def __call__(self, **query):
        return NicoProxy(self.udid, self.port, **query)
