import time
from datetime import datetime

from adb_uiautomator.nico_proxy import NicoProxy
from adb_uiautomator.get_uiautomator_xml import get_root_node, remove_ui_xml, init_adb_auto
from adb_uiautomator.utils import Utils

class UIStructureError(Exception):
    pass


class AdbAutoNico(Utils):
    def __init__(self, udid):
        super().__init__(udid)
        self.udid = udid
        remove_ui_xml()



    def __call__(self, force_reload=False,**query):
        init_adb_auto(self.udid)
        root = get_root_node(self.udid,force_reload)
        return NicoProxy(root, self.udid, **query)
