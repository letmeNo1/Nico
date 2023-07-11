from adb_uiautomator.logger_config import logger
from adb_uiautomator.nico_proxy import NicoProxy

from adb_uiautomator.get_uiautomator_xml import get_root_element, remove_xml, init_adb_auto
from adb_uiautomator.utils import Utils

class UIStructureError(Exception):
    pass


class AdbAutoNico(Utils):
    def __init__(self, udid):
        super().__init__(udid)
        self.udid = udid
        remove_xml(self.udid)
        init_adb_auto(self.udid)

    def __call__(self, **query):
        logger.debug("no found, try again")

        root = get_root_element(self.udid)
        return NicoProxy(root, self.udid, **query)
