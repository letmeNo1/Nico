import os
import random
import time
import subprocess

from auto_nico.android.nico_android_element import NicoAndroidElement
from auto_nico.common.logger_config import logger
from auto_nico.common.running_info import RunningInfo
from auto_nico.common.send_request import send_tcp_request
from auto_nico.common.nico_proxy import NicoProxy
from auto_nico.android.adb_utils import AdbUtils


class NicoAndroid(NicoProxy):
    def __init__(self, udid, port="random", **query):
        super().__init__(udid, port, **query)
        self.udid = udid
        self.adb_utils = AdbUtils(udid)
        self.version = 1.0
        self.adb_utils.install_test_server_package(self.version)
        self.adb_utils.check_adb_server()
        self.__set_running_port(port)
        rst = "200" in send_tcp_request(self.port, "print")
        if rst:
            logger.debug(f"{self.udid}'s test server is ready")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto(self.port)
        self.running_info = RunningInfo(udid)
        self.running_info.set_action_was_taken(True)
        self.close_keyboard()

    def __set_running_port(self, port):
        exists_port = self.adb_utils.get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                self.port = port
            else:
                random_number = random.randint(9000, 9999)
                self.port = random_number
        else:
            self.port = int(exists_port)


    def __start_test_server(self):
        logger.debug(
            f"""adb -s {self.udid} shell am instrument -r -w -e port {self.port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner""")
        commands = f"""adb -s {self.udid} shell am instrument -r -w -e port {self.port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        subprocess.Popen(commands, shell=True)
        for _ in range(10):
            response = send_tcp_request(self.port, "print")
            if "200" in response:
                logger.debug(f"{self.udid}'s test server is ready")
                break
            time.sleep(1)
        logger.debug(f"{self.udid}'s uiautomator was initialized successfully")

    def __init_adb_auto(self, port):
        self.adb_utils.set_tcp_forward_port(port)
        self.__start_test_server()

    def close_keyboard(self):
        adb_utils = AdbUtils(self.udid)
        ime_list = adb_utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            adb_utils.qucik_shell(f"ime disable {ime}")

    def __call__(self, **query):
        self.adb_utils.check_adb_server()
        rst = "200" in send_tcp_request(self.port, "print")
        if not rst:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.adb_utils.install_test_server_package(self.version)
            self.__init_adb_auto(self.port)
        NAE = NicoAndroidElement(**query)
        NAE.set_udid(self.udid)
        NAE.set_port(self.port)
        return NAE
