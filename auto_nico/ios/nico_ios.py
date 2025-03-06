import os
import random
import tempfile
import time
import subprocess

import requests
from auto_nico.common.error import IDBServerError
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.ios.idb_utils import IdbUtils
from auto_nico.ios.nico_ios_element import NicoIOSElement
from loguru import logger
from auto_nico.common.send_request import send_tcp_request
from auto_nico.common.nico_basic import NicoBasic


class NicoIOS(NicoBasic):
    def __init__(self, udid, package_name=None, port="random", **query):
        super().__init__(udid, **query)
        self.udid = udid
        logger.debug(f"{self.udid}'s test server is being initialized, please wait")
        self.idb_utils = IdbUtils(udid)
        self.__check_idb_server(udid)
        self.idb_utils._set_running_port(port)
        self.runtime_cache = RunningCache(udid)
        rst = "200 OK" in send_tcp_request(RunningCache(udid).get_current_running_port(), "print")
        if rst:
            logger.debug(f"{self.udid}'s test server is ready")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            if self.idb_utils.get_system_info().get("ProductVersion") >= "17.0.0":
                self.idb_utils._init_wda_server()
            else:
                self.idb_utils._init_test_server()
        if package_name is None:
            self.package_name = self.__get_current_bundleIdentifier(RunningCache(udid).get_current_running_port())
        self.runtime_cache.set_action_was_taken(True)

    def __check_idb_server(self, udid):
        result = subprocess.run("tidevice list", shell=True, stdout=subprocess.PIPE).stdout
        decoded_result = result.decode('utf-8', errors='ignore')
        if udid in decoded_result:
            pass
        else:
            raise IDBServerError("no devices connect")

    def __get_current_bundleIdentifier(self, port):
        bundle_list = self.idb_utils.get_app_list()
        command = "get_current_bundleIdentifier"
        for item in bundle_list:
            if item:
                item = item.split(" ")[0]
                command = command + f":{item}"
        package_name = send_tcp_request(port, command)
        return package_name


    def __remove_ui_xml(self, udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"/{udid}_ui.xml"
        os.remove(path)


    def __call__(self, **query):
        current_port = RunningCache(self.udid).get_current_running_port()
        self.__check_idb_server(self.udid)
        rst = "200 OK" in send_tcp_request(current_port, "print")
        if not rst:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            if self.idb_utils.is_greater_than_ios_17():
                self.idb_utils._init_wda_server()
            else:
                self.idb_utils._init_test_server()
        if self.runtime_cache.get_current_running_package():
            self.package_name = self.runtime_cache.get_current_running_package()
        else:
            if self.package_name is None:
                self.package_name = self.__get_current_bundleIdentifier(current_port)
        NIE = NicoIOSElement(**query)
        NIE.set_udid(self.udid)
        NIE.set_port(current_port)
        NIE.set_package_name(self.package_name)
        return NIE