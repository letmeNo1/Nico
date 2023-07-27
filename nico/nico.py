import time

from nico.nico_proxy import NicoProxy
from nico.get_uiautomator_xml import remove_ui_xml, init_adb_auto


class UIStructureError(Exception):
    pass


class AdbAutoNico:
    def __init__(self, udid):
        self.udid = udid
        init_adb_auto(self.udid)
        remove_ui_xml(self.udid)

    def __call__(self, force_reload=False, **query):
        return NicoProxy(self.udid, force_reload,**query)
