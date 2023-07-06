from adb_uiautomator.find_ui_element import wait_function, find_element_by_query
from adb_uiautomator.get_uiautomator_xml import get_root_element, remove_xml
from adb_uiautomator.common import Common

class UIStructureError(Exception):
    pass


class AdbAutoNico(Common):
    def __init__(self, udid):
        super().__init__(udid)
        self.udid = udid
        remove_xml(self.udid)

    def __call__(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return wait_function(root, self.udid, timeout, find_element_by_query, **query)