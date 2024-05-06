import os
import time
import subprocess

import psutil

from auto_nico.common.logger_config import logger
from auto_nico.common.running_info import RunningInfo
from auto_nico.common.send_request import send_tcp_request
from auto_nico.ios.tools.image_process import bytes_to_image, images_to_video


class NicoError(Exception):
    """
        This is NicoError BaseError
        When ADB have something wrong
    """

    pass


class IdbUtils:
    def __init__(self, udid):
        self.udid = udid
        self.running_info = RunningInfo(udid)

    def get_tcp_forward_port(self):
        for proc in psutil.process_iter(['pid', 'name', 'connections', 'cmdline']):
            # 检查进程名称是否为 'python.exe' 并且 cmdline 包含 'tidevice'
            if 'python' in proc.name().lower() and proc.info['cmdline'] is not None:
                if 'tidevice' in ' '.join(proc.info['cmdline']):
                    # 获取进程的网络连接信息
                    connections = proc.info['connections']
                    for conn in connections:
                        if conn.status == psutil.CONN_LISTEN:
                            return conn.laddr.port
        return None

    def device_list(self):
        command = f'tidevice list'
        return os.popen(command).read()

    def set_port_forward(self, port):
        commands = f"""tidevice --udid {self.udid} relay {port} {port}"""
        subprocess.Popen(commands, shell=True)

    def get_app_list(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        decoded_result = os.popen(f"tidevice --udid {self.udid} applist").read()
        result_list = decoded_result.splitlines()
        return result_list

    def get_test_server_package(self):
        app_list = self.get_app_list()
        test_server_package_list = [s for s in app_list if s.startswith('nico.')]
        test_server_package = test_server_package_list[0] if "xctrunner" in test_server_package_list[0] else \
            test_server_package_list[1]
        main_package = test_server_package_list[0] if "xctrunner" not in test_server_package_list[0] else \
            test_server_package_list[1]
        return {"test_server_package": test_server_package.split(" ")[0], "main_package": main_package.split(" ")[0]}

    def start_app(self, package_name):
        command = f'launch {package_name}'
        self.cmd(command)

    def start_recording(self):
        logger.debug("start recording")
        exists_port = self.running_info.get_current_running_port()
        if exists_port is None:
            exists_port = self.get_tcp_forward_port()
        if exists_port is None:
            raise NicoError("Start the nico service first!!!!")

        send_tcp_request(exists_port, "start_recording")

    def stop_recording(self, path='output.mp4'):
        logger.debug("stop recording, start to save video")
        time.sleep(1)
        exists_port = self.running_info.get_current_running_port()
        respo = send_tcp_request(exists_port, "stop_recording")
        images = []
        # print(respo)
        images_byte = respo.split(b'end_with')
        for image_data in images_byte:
            if not image_data:
                continue
            image = bytes_to_image(image_data)
            images.append(image)
        images_to_video(images, path)
        logger.debug("save video successfully")

    def get_output_device_name(self):
        exists_port = self.running_info.get_current_running_port()
        respo = send_tcp_request(exists_port, "device_info:get_output_device_name")
        return respo

    def stop_app(self, package_name):
        command = f'kill {package_name}'
        self.cmd(command)

    def cmd(self, cmd):
        udid = self.udid
        """@Brief: Execute the CMD and return value
        @return: bool
        """
        try:
            result = subprocess.run(f'''tidevice --udid {udid} {cmd}''', shell=True, capture_output=True, text=True,
                                    check=True, timeout=10).stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
        return result

    def restart_app(self, package_name):
        self.stop_app(package_name)
        time.sleep(1)
        self.start_app(package_name)

    def unlock(self):
        pass

    def home(self):
        exists_port = self.running_info.get_current_running_port()
        return send_tcp_request(exists_port, "device_action:home")

    def get_volume(self):
        exists_port = self.running_info.get_current_running_port()
        return send_tcp_request(exists_port, "device_info:get_volume")

    def turn_volume_up(self):
        exists_port = self.running_info.get_current_running_port()
        send_tcp_request(exists_port, "device_action:volume_up")

    def turn_volume_down(self):
        exists_port = self.running_info.get_current_running_port()
        send_tcp_request(exists_port, "device_action:volume_down")

    def snapshot(self, name, path):
        self.cmd(f'screenshot {path}/{name}.jpg')

    def get_pic(self, quality=1.0):
        exists_port = self.running_info.get_current_running_port()
        return send_tcp_request(exists_port, f"get_pic:{quality}")
