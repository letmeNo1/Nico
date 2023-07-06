import os
import re
import time


class AdbError(Exception):
    """
        This is AdbError BaseError
        When ADB have something wrong
    """

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "stdout[%s] stderr[%s]" % (self.stdout, self.stderr)


class Common:
    def __init__(self, udid):
        self.udid = udid

    def get_screen_size(self):
        command = f'adb -s {self.udid} shell wm size'
        output = os.popen(command).read()
        size_str = output.split(': ')[-1]
        width, height = map(int, size_str.split('x'))
        return width, height

    def start_app(self, package_name):
        command = f'adb -s {self.udid} shell am start -n {package_name}'
        output = os.popen(command).read()
        size_str = output.split(': ')[-1]
        width, height = map(int, size_str.split('x'))
        return width, height

    def stop_app(self, package_name):
        command = f'adb -s {self.udid} shell am force-stop {package_name}'
        output = os.popen(command).read()
        size_str = output.split(': ')[-1]
        width, height = map(int, size_str.split('x'))
        return width, height

    def shell(self, cmd):
        command = f'adb -s {self.udid} shell {cmd}'
        output = os.popen(command).read()
        return output

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
        m = screenOnRE.search(self.shell('dumpsys window policy'))
        if m:
            return m.group(1) == 'true'
        else:
            # MIUI11
            screenOnRE = re.compile('screenState=(SCREEN_STATE_ON|SCREEN_STATE_OFF)')
            m = screenOnRE.search(self.shell('dumpsys window policy'))
            if m:
                return m.group(1) == 'SCREEN_STATE_ON'
        raise AdbError("Couldn't determine screen ON state")

    def is_locked(self):
        """
        Perform `adb shell dumpsys window policy` command and search for information if screen is locked or not

        Raises:
            AirtestError: if lock screen can't be detected

        Returns:
            True or False whether the screen is locked or not

        """
        lockScreenRE = re.compile('(?:mShowingLockscreen|isStatusBarKeyguard|showing)=(true|false)')
        m = lockScreenRE.search(self.shell('dumpsys window policy'))
        if not m:
            raise AdbError("Couldn't determine screen lock state")
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
        self.shell('input keyevent MENU')
        self.shell('input keyevent BACK')

    def keyevent(self,keyname):
        self.shell(f'input keyevent {keyname}')

