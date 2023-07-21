<<<<<<< HEAD
=======
import time
from datetime import datetime

>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
from adb_uiautomator.nico_proxy import NicoProxy
from adb_uiautomator.get_uiautomator_xml import get_root_node, remove_ui_xml, init_adb_auto
from adb_uiautomator.utils import Utils

class UIStructureError(Exception):
    pass


class AdbAutoNico(Utils):
    def __init__(self, udid,wait_idle=2000):
        super().__init__(udid)
        self.udid = udid
<<<<<<< HEAD
        self.wait_idle = wait_idle
        remove_ui_xml(self.udid)


    def __call__(self, force_reload=False,**query):
        init_adb_auto(self.udid)
        root = get_root_node(self.udid,force_reload,self.wait_idle)
=======
        remove_ui_xml()



    def __call__(self, force_reload=False,**query):
        init_adb_auto(self.udid)
        root = get_root_node(self.udid,force_reload)
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
        return NicoProxy(root, self.udid, **query)
