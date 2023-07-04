from adb_uiautomator.common import Common
from adb_uiautomator.find_ui_element import wait_function, find_element_by_query, scroll_to_find_element, find_element_exits
from adb_uiautomator.get_uiautomator_xml import get_root_element, remove_xml


class UIStructureError(Exception):
    pass


class AdbUiautomator(Common):
    def __init__(self, udid):
        super().__init__(udid)
        self.udid = udid
        remove_xml(self.udid)

    def find_element_by_wait(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return wait_function(root, self.udid, timeout, find_element_by_query, **query)

    def check_element_exists(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return find_element_exits(root, self.udid, timeout, find_element_by_query, **query)

    def scroll_to_find_element(self, scroll_time=10, target_area=None, **query):
        root = get_root_element(self.udid)
        return scroll_to_find_element(root, self.udid, scroll_time, target_area, **query)