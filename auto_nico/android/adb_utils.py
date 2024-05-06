import os
import re
import time
import subprocess

from auto_nico.common.logger_config import logger

from auto_nico.common.error import ADBServerError


class AdbUtils:
    def __init__(self, udid):
        self.udid = udid

    def get_tcp_forward_port(self):
        rst = self.cmd(f'''forward --list | find "{self.udid}"''')
        port = None
        if rst != "":
            port = rst.split("tcp:")[-1]
        return port

    def clear_tcp_forward_port(self, port):
        self.cmd(f"forward --remove tcp:{port}")

    def set_tcp_forward_port(self,port):
        for _ in range(5):
            rst = self.cmd(f'''forward --list | find "{port}"''')
            if self.udid not in rst:
                self.cmd(f'''forward tcp:{port} tcp:{port}''')
            else:
                logger.debug(f"{self.udid}'s tcp already forward tcp:{port} tcp:{port}")
                break

    def install_test_server_package(self,version):
        def install(udid):
            for i in ["dump_hierarchy.apk", "dump_hierarchy_androidTest.apk"]:
                logger.debug(f"{udid}'s start install {i}")
                lib_path = (os.path.dirname(__file__) + f"\package\{i}").replace("console_scripts\inspector_web", "")
                rst = self.cmd(f"install -t {lib_path}")
                if rst.find("Success") >= 0:
                    logger.debug(f"{udid}'s adb install {i} successfully")
                else:
                    logger.debug(rst)

        rst = self.qucik_shell("dumpsys package nico.dump_hierarchy | grep versionName")
        if "versionName" not in rst:
            install(self.udid)
        elif version > float(rst.split("=")[-1]):
            logger.debug(float(rst.split("=")[-1]))

            logger.debug(f"{self.udid}'s New version detected")
            for i in ["nico.dump_hierarchy", "nico.dump_hierarchy.test"]:
                logger.debug(f"{self.udid}'s start uninstall {i}")
                rst = self.cmd(f"uninstall {i}")
                if rst.find("Success") >= 0:
                    logger.debug(f"{self.udid}'s adb uninstall {i} successfully")
                else:
                    logger.debug(rst)
            install(self.udid)

    def check_adb_server(self):
        rst = os.popen("adb devices").read()
        if self.udid in rst:
            pass
        else:
            raise ADBServerError("no devices connect")

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

    def keyevent(self, keyname):
        self.qucik_shell(f'input keyevent {keyname}')

    def back(self):
        self.keyevent("BACK")

    def menu(self):
        self.keyevent("MENU")

    def home(self):
        self.keyevent("HOME")

    def snapshot(self, name, path):
        self.shell(f'screencap -p /sdcard/{name}.png', with_root=True)
        self.cmd(f'pull /sdcard/{name}.png {path}')
        self.qucik_shell(f'rm /sdcard/{name}.png')

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
