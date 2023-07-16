from datetime import datetime

from adb_uiautomator.nico_proxy import NicoProxy
from adb_uiautomator.get_uiautomator_xml import get_root_node, remove_ui_xml, init_adb_auto
from adb_uiautomator.utils import Utils

class UIStructureError(Exception):
    pass


class AdbAutoNico(Utils):
    def __init__(self, udid,wait_idle=2000):
        super().__init__(udid)
        self.udid = udid
        self.wait_idle = wait_idle
        remove_ui_xml(self.udid)



    def __call__(self, force_reload=False,**query):
        init_adb_auto(self.udid)
        root = get_root_node(self.udid,force_reload,self.wait_idle)
        return NicoProxy(root, self.udid, **query)
