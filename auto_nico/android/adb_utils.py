import os
import re
import time
import subprocess

from loguru import logger

from auto_nico.common.error import ADBServerError, NicoError
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.common.send_request import send_tcp_request
import cv2
import numpy as np


class AdbUtils:
    def __init__(self, udid):
        self.udid = udid
        self.runtime_cache = RunningCache(udid)
        self.version = 1.3

    def get_tcp_forward_port(self):
        rst = self.cmd(f'''forward --list | findstr /v local |findstr "{self.udid}"''')
        port = None
        if rst != "":
            port = rst.split("tcp:")[-1]
        return port

    def clear_tcp_forward_port(self, port):
        logger.info(f"{self.udid}'s forward --remove tcp:{port}")
        self.cmd(f"forward --remove tcp:{port}")

    def set_tcp_forward_port(self, port):
        for _ in range(5):
            rst = self.cmd(f'''forward --list | find "{port}"''')
            if self.udid not in rst:
                self.cmd(f'''forward tcp:{port} tcp:{port}''')
            else:
                logger.info(f"{self.udid}'s tcp already forward tcp:{port} tcp:{port}")
                break

    def restart_test_server(self, port):
        runtime_cache = RunningCache(self.udid)
        def __check_server_ready(current_port, timeout):
            time_started_sec = time.time()
            while time.time() < time_started_sec + timeout:
                rst = "[android.view.accessibility.AccessibilityNodeInfo" in send_tcp_request(current_port, "get_root")
                if rst:
                    logger.info(f"{self.udid}'s test server is ready on {port}")
                    runtime_cache.set_current_running_port(port)
                    return True
                else:
                    logger.info(f"{self.udid}'s test server isn't ready on {port}")
                    time.sleep(0.5)
                    continue
            return False

        for _ in range(5):
            logger.debug(
                f"""adb -s {self.udid} shell am instrument -r -w -e port {port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner""")
            commands = f"""adb -s {self.udid} shell am instrument -r -w -e port {port} -e class nico.dump_hierarchy.HierarchyTest nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
            subprocess.Popen(commands, shell=True)
            if __check_server_ready(port, 10):
                logger.info(f"{self.udid}'s uiautomator was initialized successfully")
                return True
            logger.info(f"wait 3 s")
            time.sleep(3)
        return False

    def __install(self, udid, version):
        for i in [f"dump_hierarchy_v{version}.apk", f"dump_hierarchy_androidTest_v{version}.apk"]:
            logger.info(f"{udid}'s start install {i}")
            lib_path = (os.path.dirname(__file__) + f"\package\{i}").replace("console_scripts\inspector_web", "")
            rst = self.cmd(fr'install -t "{lib_path}"')
            if rst.find("Success") >= 0:
                logger.info(f"{udid}'s adb install {lib_path} successfully")
            else:
                logger.info(rst)

    def reinstall_test_server_package(self, version):
        for i in ["nico.dump_hierarchy", "nico.dump_hierarchy.test"]:
            logger.info(f"{self.udid}'s start uninstall {i}")
            rst = self.cmd(f"uninstall {i}")
            if rst.find("Success") >= 0:
                logger.info(f"{self.udid}'s adb uninstall {i} successfully")
        self.__install(self.udid, version)

    def install_test_server_package(self, version):
        rst = self.qucik_shell("dumpsys package nico.dump_hierarchy | grep versionName")
        if "versionName" not in rst:
            self.wait_for_boot_completed()
            self.__install(self.udid, version)
        elif version > float(rst.split("=")[-1]):
            logger.info(float(rst.split("=")[-1]))
            logger.info(f"{self.udid}'s New version detected")
            for i in ["nico.dump_hierarchy", "nico.dump_hierarchy.test"]:
                logger.debug(f"{self.udid}'s start uninstall {i}")
                rst = self.cmd(f"uninstall {i}")
                if rst.find("Success") >= 0:
                    logger.debug(f"{self.udid}'s adb uninstall {i} successfully")
                else:
                    logger.debug(rst)
            self.__install(self.udid, version)
        else:
            logger.debug(f"{self.udid}'s version is the latest")

    def is_device_boot_completed(self):
        result = self.shell("getprop sys.boot_completed").strip()
        print(result)
        return result == "1"

    def wait_for_boot_completed(self):
        while not self.is_device_boot_completed():
            print("Waiting for device to complete booting...")
            time.sleep(5)
        print("Device boot completed")

    def check_adb_server(self):
        rst = os.popen("adb devices").read()
        if self.udid in rst:
            pass
        else:
            raise ADBServerError("no devices connect")

    def is_screen_off(self):
        rst = self.shell("dumpsys display | grep 'mScreenState'")
        if "mScreenState=ON" in rst:
            # logger.info(f"{self.udid}'s screen is on")
            return False
        else:
            logger.info(f"{self.udid}'s screen is off")
            return True

    def get_screen_size(self):
        command = f'adb -s {self.udid} shell wm size'
        output = os.popen(command).read()
        size_str = output.split(': ')[-1]
        width, height = map(int, size_str.split('x'))
        return width, height

    def start_app(self, package_name):
        command = f'am start -n {package_name}'
        self.qucik_shell(command)

    def stop_app(self, package_name):
        command = f'am force-stop {package_name}'
        self.qucik_shell(command)

    def qucik_shell(self, cmds):
        udid = self.udid
        """@Brief: Execute the CMD and return value
        @return: bool
        """
        try:
            result = subprocess.run(f'''adb -s {udid} shell "{cmds}"''', shell=True, capture_output=True, text=True,
                                    check=True).stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        return result

    def shell(self, cmds, with_root=False, timeout=10):
        udid = self.udid
        """@Brief: Execute the CMD and return value
        @return: bool
        """
        commands = ""
        if type(cmds) is list:
            for cmd in cmds:
                commands = commands + cmd + "\n"
        else:
            commands = cmds
        if with_root:
            su_commands = "su\n"
            commands = su_commands + commands
        adb_process = subprocess.Popen("adb -s %s shell" % udid, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True, shell=True)
        adb_process.stdin.write(commands)
        output, error = adb_process.communicate(timeout=timeout)
        if output != "":
            return output
        else:
            return error

    def cmd(self, cmd):
        udid = self.udid
        """@Brief: Execute the CMD and return value
        @return: bool
        """
        try:
            result = subprocess.run(f'''adb -s {udid} {cmd}''', shell=True, capture_output=True, text=True,
                                    check=True, timeout=10).stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        return result

    def restart_app(self, package_name):
        self.stop_app(package_name)
        time.sleep(1)
        self.start_app(package_name)

    def is_keyboard_shown(self):
        """
        Perform `adb shell dumpsys input_method` command and search for information if keyboard is shown

        Returns:
            True or False whether the keyboard is shown or not

        """
        dim = self.shell('dumpsys input_method')
        if dim:
            return "mInputShown=true" in dim
        return False

    def is_screenon(self):
        """
        Perform `adb shell dumpsys window policy` command and search for information if screen is turned on or off

        Raises:
            AirtestError: if screen state can't be detected

        Returns:
            True or False whether the screen is turned on or off

        """
        screenOnRE = re.compile('mScreenOnFully=(true|false)')
        m = screenOnRE.search(self.qucik_shell('dumpsys window policy'))
        if m:
            return m.group(1) == 'true'
        else:
            # MIUI11
            screenOnRE = re.compile('screenState=(SCREEN_STATE_ON|SCREEN_STATE_OFF)')
            m = screenOnRE.search(self.qucik_shell('dumpsys window policy'))
            if m:
                return m.group(1) == 'SCREEN_STATE_ON'
        raise NicoError("Couldn't determine screen ON state")


    def is_locked(self):
        """
        Perform `adb shell dumpsys window policy` command and search for information if screen is locked or not

        Raises:
            AirtestError: if lock screen can't be detected

        Returns:
            True or False whether the screen is locked or not

        """
        lockScreenRE = re.compile('(?:mShowingLockscreen|isStatusBarKeyguard|showing)=(true|false)')
        m = lockScreenRE.search(self.qucik_shell('dumpsys window policy'))
        if not m:
            raise NicoError("Couldn't determine screen lock state")
        return (m.group(1) == 'true')

    def unlock(self):
        """
        Perform `adb shell input keyevent MENU` and `adb shell input keyevent BACK` commands to attempt
        to unlock the screen

        Returns:
            None

        Warnings:
            Might not work on all devices

        """
        self.qucik_shell('input keyevent MENU')
        self.qucik_shell('input keyevent BACK')

    def wake_up(self):
        self.qucik_shell('input keyevent KEYCODE_WAKEUP')

    def keyevent(self, keyname):
        self.qucik_shell(f'input keyevent {keyname}')

    def switch_app(self):
        self.keyevent("KEYCODE_APP_SWITCH")

    def back(self):
        self.keyevent("BACK")

    def menu(self):
        self.keyevent("MENU")

    def home(self):
        self.keyevent("HOME")

    def switch_app(self):
        self.keyevent("KEYCODE_APP_SWITCH")

    def get_image_object(self, quality=100,use_adb=True):
        if use_adb:
            result = subprocess.run(['adb', '-s', self.udid, 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
            screenshot_data = result.stdout
            nparr = np.frombuffer(screenshot_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        else:
            exists_port = self.runtime_cache.get_current_running_port()
            a = send_tcp_request(exists_port, f"get_png_pic:{quality}")
            nparr = np.frombuffer(a, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image

    def get_root_node(self):
        exists_port = self.runtime_cache.get_current_running_port()
        for _ in range(5):
            response = send_tcp_request(exists_port, "dump_tree:true")
            if "<hierarchy" in response and "</hierarchy>" in response:
                return response
            time.sleep(1)

    def snapshot(self, name, path):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        self.shell(f'screencap -p /sdcard/{name}.png', with_root=True)
        self.cmd(f'pull /sdcard/{name}.png {path}')
        self.qucik_shell(f'rm /sdcard/{name}.png')
        full_path = f"{path}/{name}.png"
        logger.info(full_path)
        return full_path

    def swipe(self, direction, scroll_time=1, target_area=None):
        x = int(self.get_screen_size()[0] / 2)
        y1 = int(self.get_screen_size()[1] / 4)
        y2 = int(self.get_screen_size()[1] / 2)
        if target_area is not None:
            x = int(self.get_screen_size()[0] * target_area.get_position()[0])
            y1 = int((self.get_screen_size()[1] * target_area.get_position()[1]) / 4)
            y2 = int((self.get_screen_size()[1] * target_area.get_position()[1]) / 2)
        if direction not in ["down", "up"]:
            raise TypeError("Please use up or down")
        else:
            for i in range(int(scroll_time)):
                if direction == "down":
                    self.shell(f"input swipe {x} {y1} {x} {y2}")
                elif direction == "up":
                    self.shell(f"input swipe {x} {y2} {x} {y1}")
