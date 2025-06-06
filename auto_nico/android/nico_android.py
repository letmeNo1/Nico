import random
import sys
import time
import subprocess

from auto_nico.android.nico_android_element import NicoAndroidElement
from loguru import logger
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.common.send_request import send_http_request
from auto_nico.common.nico_basic import NicoBasic
from auto_nico.android.adb_utils import AdbUtils


class NicoAndroid(NicoBasic):
    def __init__(self, udid, port="random", debug=True,**query):
        super().__init__(udid,  **query)
        if not debug:
            logger.remove()  # 移除默认处理器
            logger.add(sys.stderr, level="INFO")  # 只显示 INFO 及以上级别
        self.udid = udid
        self.adb_utils = AdbUtils(udid)
        self.version = 1.4
        self.adb_utils.install_test_server_package(self.version)
        self.adb_utils.check_adb_server()
        self.__set_running_port(port)
        self.runtime_cache = RunningCache(udid)
        self.runtime_cache.set_initialized(True)
        response = send_http_request(RunningCache(udid).get_current_running_port(), "status")
        rst = response is not None and "server is running" in response
        response = send_http_request(RunningCache(udid).get_current_running_port(), "get_root")
        rst2 = response is not None and "[android.view.accessibility.AccessibilityNodeInfo" in response
        if rst and rst2:
            logger.debug(f"{self.udid}'s test server is ready on {RunningCache(udid).get_current_running_port()}")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto(RunningCache(udid).get_current_running_port())

        self.close_keyboard()

    def __set_running_port(self, port):
        exists_port = self.adb_utils.get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                running_port = port
            else:
                random_number = random.randint(9000, 9999)
                running_port = random_number
        else:
            running_port = int(exists_port)
        RunningCache(self.udid).set_current_running_port(running_port)\

    def __check_server_ready(self,current_port,timeout):
        time_started_sec = time.time()
        while time.time() < time_started_sec + timeout:
            response = send_http_request(current_port, "get_root")
            rst = response is not None and  "[android.view.accessibility.AccessibilityNodeInfo" in response
            logger.info(f"{self.udid}'s response is {response } ")

            if rst:

                logger.info(f"{self.udid}'s test server is ready on {current_port}")
                return True
            else:
                logger.info(f"server is no ready on {current_port}")
                time.sleep(0.5)
                continue
        return False

    def __start_test_server(self):
        current_port = RunningCache(self.udid).get_current_running_port()
        for _ in range(5):
            logger.debug(
                f"""adb -s {self.udid} shell am instrument -r -w -e port {current_port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner""")
            commands = f"""adb -s {self.udid} shell am instrument -r -w -e port {current_port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
            subprocess.Popen(commands, shell=True)
            time.sleep(3)
            if self.__check_server_ready(current_port,10):
                break
            logger.info(f"wait 3 s")
            time.sleep(3)
        logger.info(f"{self.udid}'s uiautomator was initialized successfully")

    def __init_adb_auto(self, port):
        self.adb_utils.set_tcp_forward_port(port)
        self.__start_test_server()

    def close_keyboard(self):
        adb_utils = AdbUtils(self.udid)
        ime_list = adb_utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            adb_utils.qucik_shell(f"ime disable {ime}")

    def __call__(self, **query):
        current_port = RunningCache(self.udid).get_current_running_port()
        self.adb_utils.check_adb_server()
        if self.adb_utils.is_screen_off():
            self.adb_utils.wake_up()
        response = send_http_request(current_port, "get_root")
        rst = response is not None and "[android.view.accessibility.AccessibilityNodeInfo" in response
        if not rst:
            logger.info(f"{self.udid} test server disconnect, restart ")
            self.adb_utils.install_test_server_package(self.version)
            self.__init_adb_auto(current_port)
            self.close_keyboard()
        else:
            logger.info(f"{self.udid} test server connect successful ")

        NAE = NicoAndroidElement(**query)
        NAE.set_udid(self.udid)
        NAE.set_port(current_port)
        return NAE