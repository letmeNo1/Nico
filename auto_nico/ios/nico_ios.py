import os
import random
import tempfile
import time
import subprocess

from auto_nico.common.error import IDBServerError
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.ios.idb_utils import IdbUtils
from auto_nico.ios.nico_ios_element import NicoIOSElement
from auto_nico.common.logger_config import logger
from auto_nico.common.send_request import send_tcp_request
from auto_nico.common.nico_basic import NicoBasic





class NicoIOS(NicoBasic):
    def __init__(self, udid, package_name=None, port="random", **query):
        super().__init__(udid, **query)
        self.udid = udid
        logger.debug(f"{self.udid}'s test server is being initialized, plaese wait")
        self.idb_utils = IdbUtils(udid)
        self.__check_idb_server(udid)
        self.__set_running_port(port)
        self.runtime_cache = RunningCache(udid)
        rst = "200 OK" in send_tcp_request(self.port, "print")
        if rst:
            logger.debug(f"{self.udid}'s test server is ready")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto()
        if package_name is None:
            self.package_name = self.__get_current_bundleIdentifier(self.port)
        self.runtime_cache.set_action_was_taken(True)

    def __check_idb_server(self, udid):
        result = subprocess.run("tidevice list", shell=True, stdout=subprocess.PIPE).stdout
        decoded_result = result.decode('utf-8', errors='ignore')
        if udid in decoded_result:
            pass
        else:
            raise IDBServerError("no devices connect")


    def __set_running_port(self, port):
        exists_port,pid= self.idb_utils.get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                self.port = port
            else:
                random_number = random.randint(9000, 9999)
                self.port = random_number
            RunningCache(self.udid).set_current_running_port(self.port)
            return None
        else:
            logger.debug(f"{self.udid} exists port {exists_port}")

            self.port = int(exists_port)
            self.ports_pid = int(pid)
        RunningCache(self.udid).set_current_running_port(exists_port)


    def __get_current_bundleIdentifier(self,port):
        bundle_list = self.idb_utils.get_app_list()
        command = "get_current_bundleIdentifier"
        for item in bundle_list:
            if item:
                item = item.split(" ")[0]
                command = command + f":{item}"
        package_name = send_tcp_request(port, command)
        return package_name

    def __set_tcp_forward_port(self):
        logger.debug(
            f"""tidevice --udid {self.udid} relay {self.port} {self.port}""")
        commands = f"""tidevice --udid {self.udid} relay {self.port} {self.port}"""
        try:

            subprocess.Popen(commands, shell=True)
            print("sss")
            print("start ss")

        except OSError:
            print("start fail")
            subprocess.Popen(commands, shell=True)


    def __start_test_server(self):
        test_server_package_dict = self.idb_utils.get_test_server_package()
        logger.debug(f"""tidevice  --udid {self.udid} xcuitest --bundle-id {test_server_package_dict.get("test_server_package")} --target-bundle-id {test_server_package_dict.get("main_package")} -e USE_PORT:{self.port}""")

        commands = f"""tidevice  --udid {self.udid} xcuitest --bundle-id {test_server_package_dict.get("test_server_package")} --target-bundle-id {test_server_package_dict.get("main_package")} -e USE_PORT:{self.port}"""
        subprocess.Popen(commands, shell=True)
        for _ in range(10):
            response = send_tcp_request(self.port, "print")
            if "200 OK" in response:
                logger.debug(f"{self.udid}'s test server is ready")
                break
            time.sleep(1)
        logger.debug(f"{self.udid}'s uiautomator was initialized successfully")

    def __remove_ui_xml(self, udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"/{udid}_ui.xml"
        os.remove(path)

    def __init_adb_auto(self):
        self.__set_tcp_forward_port()
        self.__start_test_server()


    def __call__(self, **query):
        self.__check_idb_server(self.udid)
        rst = "200 OK" in send_tcp_request(self.port, "print")
        if not rst:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto()
        if self.runtime_cache.get_current_running_package():
            self.package_name = self.runtime_cache.get_current_running_package()
        else:
            if self.package_name is None:
                self.package_name = self.__get_current_bundleIdentifier(self.port)
        NIE = NicoIOSElement(**query)
        NIE.set_udid(self.udid)
        NIE.set_port(self.port)
        NIE.set_package_name(self.package_name)
        return NIE
