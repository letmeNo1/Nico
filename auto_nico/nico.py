import os
import random
import tempfile
import time
import subprocess
from auto_nico.nico_proxy import NicoProxy

from auto_nico.nico_element import NicoElement
from auto_nico.send_request import send_tcp_request
from auto_nico.adb_utils import AdbUtils, NicoError

from auto_nico.logger_config import logger


class UIStructureError(Exception):
    pass


class ADBServerError(Exception):
    pass


class AdbAutoNico(NicoProxy):
    def __init__(self, udid, port="random", **query):
        super().__init__(udid, port, **query)
        self.udid = udid
        self.adb_utils = AdbUtils(udid)
        self.__install_package()
        self.__check_adb_server(udid)
        self.__set_running_port(port)
        rst = "200" in send_tcp_request(self.port, "print")
        if rst:
            logger.debug(f"{self.udid}'s test server is ready")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto()
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        self.close_keyboard()

    def __del__(self):
        self.__clear_all_port_forward()
        send_tcp_request(self.port, "close")

    def __check_adb_server(self, udid):
        rst = os.popen("adb devices").read()
        if udid in rst:
            pass
        else:
            raise ADBServerError("no devices connect")

    def __set_running_port(self, port):
        exists_port = self.__get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                self.port = port
            else:
                random_number = random.randint(9000, 9999)
                self.port = random_number
        else:
            self.port = int(exists_port)

    def __clear_all_port_forward(self):
        self.adb_utils.cmd(f"forward --remove-all")

    def __install_package(self):
        dict = {
            "app.apk": "hank.dump_hierarchy",
            "android_test.apk": "hank.dump_hierarchy.test",
        }
        rst = self.adb_utils.qucik_shell("pm list packages hank.dump_hierarchy")
        # print(rst)
        for i in ["android_test.apk", "app.apk"]:
            if f"package:{dict.get(i)}" not in rst:
                logger.debug(f"{self.udid}'s start install {i}")
                lib_path = os.path.dirname(__file__) + f"\package\{i}"
                rst = self.adb_utils.cmd(f"install -t {lib_path}")
                if rst.find("Success") >= 0:
                    logger.debug(f"{self.udid}'s adb install {i} successfully")
                else:
                    logger.error(rst)
            else:
                logger.debug(f"{self.udid}'s {i} already install")

    def __get_tcp_forward_port(self):
        rst = self.adb_utils.cmd(f'''forward --list | find "{self.udid}"''')
        port = None
        if rst != "":
            port = rst.split("tcp:")[-1]
        return port

    def __set_tcp_forward_port(self):
        for _ in range(5):
            rst = self.adb_utils.cmd(f'''forward --list | find "{self.port}"''')
            if self.udid not in rst:
                self.adb_utils.cmd(f'''forward tcp:{self.port} tcp:{self.port}''')
            else:
                logger.debug(f"{self.udid}'s tcp already forward tcp:{self.port} tcp:{self.port}")
                break

    def __start_test_server(self):
        logger.debug(
            f"""adb -s {self.udid} shell am instrument -r -w -e port {self.port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner""")
        commands = f"""adb -s {self.udid} shell am instrument -r -w -e port {self.port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        subprocess.Popen(commands, shell=True)
        for _ in range(10):
            response = send_tcp_request(self.port, "print")
            if "200" in response:
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

    def close_keyboard(self):
        adb_utils = AdbUtils(self.udid)
        ime_list = adb_utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            adb_utils.qucik_shell(f"ime disable {ime}")

    def __call__(self, **query):
        self.__check_adb_server(self.udid)
        rst = "200" in send_tcp_request(self.port, "print")
        if not rst:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__install_package()
            self.__init_adb_auto()
        return NicoElement(self.udid, self.port, **query)
