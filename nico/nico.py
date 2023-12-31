import os
import random
import tempfile
import time
import subprocess
import socket

from nico import utils
from nico.nico_element import NicoElement
from nico.send_request import send_tcp_request
from nico.utils import Utils, NicoError

from nico.logger_config import logger


class UIStructureError(Exception):
    pass


class AdbAutoNico:
    def __init__(self, udid, port="random"):
        self.udid = udid
        # 先判断是否有已存在的端口
        self.__set_running_port(port)

        # 如果有已存在的端口则判断服务是正常开启
        rst = "WinError" not in send_tcp_request(self.port, "print")
        if rst:
            logger.debug(f"{self.udid}'s test server is ready")
        else:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self.__init_adb_auto(self.udid, self.port)
            self.__remove_ui_xml(self.udid)
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        self.close_keyboard()

    def __set_running_port(self,port):
        exists_port = self.__get_tcp_forward_port(self.udid)
        if exists_port is None:

            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                self.port = port
            else:
                random_number = random.randint(9000, 9999)
                self.port = random_number
            os.popen(f"adb -s {self.udid} forward tcp:{self.port} tcp:{self.port}").read()

            self.__init_adb_auto(self.udid, self.port)
            self.__remove_ui_xml(self.udid)
        else:
            self.port = int(exists_port)

    def __check_xml_exists(self, udid):
        temp_folder = tempfile.gettempdir()
        path = temp_folder + f"/{udid}_ui.xml"
        return os.path.exists(path)

    def __get_tcp_forward_port(self, udid):
        utils = Utils(udid)
        rst = utils.cmd(f'''forward --list | find "{udid}"''')
        port = None
        if rst != "":
            port = rst.split("tcp:")[-1]
        return port

    def __remove_ui_xml(self, udid):
        if self.__check_xml_exists(udid):
            temp_folder = tempfile.gettempdir()
            path = temp_folder + f"/{udid}_ui.xml"
            os.remove(path)

    def __init_adb_auto(self, udid, port):
        utils = Utils(udid)
        # utils.cmd(f'''forward --remove-all''')
        # utils.qucik_shell("am force-stop hank.dump_hierarchy")
        dict = {
            "app.apk": "hank.dump_hierarchy",
            "android_test.apk": "hank.dump_hierarchy.test",
        }
        rst = utils.qucik_shell("pm list packages hank.dump_hierarchy")
        for _ in range(5):
            rst = utils.cmd(f'''forward --list | find "{port}"''')
            if udid not in rst:
                utils.cmd(f'''forward tcp:{port} tcp:{port}''')
            else:
                logger.debug(f"{udid}'s tcp already forward tcp:{port} tcp:{port}")
                break
        if rst.find("not found") > 0:
            raise NicoError(rst)

        for i in ["android_test.apk", "app.apk"]:
            if f"package:{dict.get(i)}" not in rst:
                logger.debug(f"{udid}'s start install {i}")
                lib_path = os.path.dirname(__file__) + f"\libs\{i}"
                rst = utils.cmd(f"install {lib_path}")
                if rst.find("Success") >= 0:
                    logger.debug(f"{udid}'s adb install {i} successfully")
                else:
                    logger.error(rst)
            else:
                logger.debug(f"{udid}'s {i} already install")


        logger.debug(f"""adb -s {udid} shell am instrument -r -w -e port {port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner""")

        commands = f"""adb -s {udid} shell am instrument -r -w -e port {port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        subprocess.Popen(commands, shell=True)
        for _ in range(10):
            response = send_tcp_request(port, "print")
            if "200" in response:
                logger.debug(f"{udid}'s test server is ready")
                break
            time.sleep(1)
        logger.debug(f"{udid}'s uiautomator was initialized successfully")

    def close_keyboard(self):
        utils = Utils(self.udid)
        ime_list = utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            utils.qucik_shell(f"ime disable {ime}")

    # os.popen(commands)  # 执行外部命令
    def __call__(self, **query):
        self.__set_running_port(self.port)
        return NicoElement(self.udid, self.port, **query)



