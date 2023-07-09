from adb_uiautomator.ui_object import UiObject

from adb_uiautomator.find_ui_element import find_element_by_query
from adb_uiautomator.get_uiautomator_xml import get_root_element, remove_xml
from adb_uiautomator.utils import Utils


class UIStructureError(Exception):
    pass


class AdbAutoNico(Utils):
    def __init__(self, udid):
        super().__init__(udid)
        self.udid = udid
        remove_xml(self.udid)

    def __call__(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return UiObject(root, self.udid, find_element_by_query, **query)
