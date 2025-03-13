import json
import os
import platform
import random
import re
import time
import subprocess

import cv2
import numpy as np
import psutil

from loguru import logger
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.common.send_request import send_tcp_request, send_http_request
from auto_nico.ios.tools.image_process import bytes_to_image, images_to_video
from auto_nico.common.error import NicoError


class IdbUtils:
    def __init__(self, udid):
        self.udid = udid
        self.runtime_cache = RunningCache(udid)

    def get_tcp_forward_port(self):
        if platform.system() == "Windows":
            result = subprocess.run(f'netstat -ano | findstr "LISTENING"', capture_output=True, text=True, shell=True)
            output = result.stdout
            lines = output.split('\n')
            pids = [line.split()[4] for line in lines if line.strip()]

        elif platform.system() == "Darwin" or platform.system() == "Linux":
            result = subprocess.run(f'lsof -i | grep LISTEN', capture_output=True, text=True, shell=True)
            output = result.stdout
            lines = output.split('\n')
            pids = [line.split()[1] for line in lines if line.strip()]
        else:
            raise Exception("Unsupported platform")
        for index, pid in enumerate(pids):
            try:
                if "tidevice" in psutil.Process(int(pid)).cmdline()[1]:
                    if platform.system() == "Windows":
                        return lines[index].split()[1].split("->")[0].split(":")[-1], pid
                    else:
                        result = subprocess.run(f"lsof -Pan -p {pid} -i", capture_output=True, text=True, shell=True)
                        output = result.stdout
                        ports = re.findall(r':(\d+)', output)
                        return ports[0], pid
            except:
                continue
        return None, None

    def is_greater_than_ios_17(self):
        from packaging.version import Version
        return Version(self.get_system_info().get("ProductVersion")) >= Version("17.0.0")

    def device_list(self):
        command = f'tidevice list'
        return os.popen(command).read()

    def set_port_forward(self, port):

        commands = f"""tidevice --udid {self.udid} relay {port} {port}"""
        subprocess.Popen(commands, shell=True)
        self.runtime_cache.set_current_running_port(port)

    def get_app_list(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(f"tidevice --udid {self.udid} applist", capture_output=True, text=True,
                                encoding='utf-8')
        result_list = result.stdout.splitlines()
        return result_list

    def get_test_server_package(self):
        app_list = self.get_app_list()
        xctrunner_package_name = [s for s in app_list if "dump_hierarchyUITests-Runner" in s][0].split(" ")[0]
        main_package_name = [s for s in app_list if "nico_dump" in s][0].split(" ")[0]
        return {"test_server_package": xctrunner_package_name, "main_package": main_package_name}

    def get_wda_server_package(self):
        app_list = self.get_app_list()
        test_server_package = [s for s in app_list if s.startswith('com.facebook')]
        return test_server_package[0].split(" ")[0]

    def start_app(self, package_name):
        command = f'launch {package_name}'
        self.cmd(command)
        self.runtime_cache.set_current_running_package_name(package_name)

    def _init_test_server(self):
        self._set_tcp_forward_port()
        if self.get_system_info().get("ProductVersion") >= "17.0.0":
            self._start_tunnel()
        self.__start_test_server()

    def __start_test_server(self):
        current_port = RunningCache(self.udid).get_current_running_port()
        test_server_package_dict = self.get_test_server_package()
        logger.debug(
            f"ios runwda --bundleid {test_server_package_dict.get('main_package')} --testrunnerbundleid {test_server_package_dict.get('test_server_package')} --xctestconfig=dump_hierarchyUITests.xctest --udid={self.udid} --env=USE_PORT={current_port}")

        commands = f"ios runwda --bundleid {test_server_package_dict.get('main_package')} --testrunnerbundleid {test_server_package_dict.get('test_server_package')} --xctestconfig=dump_hierarchyUITests.xctest --udid={self.udid} --env=USE_PORT={current_port}"
        subprocess.Popen(commands, shell=True)
        for _ in range(10):
            response = send_http_request(current_port, "check_status")
            if response is not None:
                logger.debug(f"{self.udid}'s test server is ready")
                break
            time.sleep(1)
        logger.debug(f"{self.udid}'s uiautomator was initialized successfully")

    def _start_tunnel(self):
        rst = os.popen("ios tunnel ls").read()
        logger.debug(f"{self.udid}'s uiautomator rst is {rst}")
        if self.udid in rst:
            logger.debug(f"tunnel for {self.udid} is started")
        else:
            logger.debug(f"ios tunnel start --udid={self.udid}")

            command = f"ios tunnel start --udid={self.udid}"
            subprocess.Popen(command, shell=True)
            for _ in range(10):
                rst = os.popen("ios tunnel ls").read()
                if self.udid in rst:
                    logger.debug(f"tunnel for {self.udid} is started")
                    return
                time.sleep(1)
            raise NicoError(f"tunnel for {self.udid} is not started")

    def _set_tcp_forward_port(self):
        current_port = RunningCache(self.udid).get_current_running_port()
        logger.debug(
            f"""tidevice --udid {self.udid} relay {current_port} {current_port}""")
        commands = f"""tidevice --udid {self.udid} relay {current_port} {current_port}"""
        try:
            subprocess.Popen(commands, shell=True)
        except OSError:
            print("start fail")
            subprocess.Popen(commands, shell=True)

    def _set_running_port(self, port):
        exists_port, pid = self.get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                running_port = port
            else:
                random_number = random.randint(9000, 9999)
                running_port = random_number
        else:
            running_port = int(exists_port)
        RunningCache(self.udid).set_current_running_port(running_port)

    def activate_app(self, package_name):
        exists_port = self.runtime_cache.get_current_running_port()
        send_http_request(exists_port, "activate_app", {"bundle_id": package_name})

    def terminate_app(self, package_name):
        exists_port = self.runtime_cache.get_current_running_port()
        send_http_request(exists_port, "terminate_app", {"bundle_id": package_name})

    def start_recording(self):
        logger.debug("start recording")
        exists_port = self.runtime_cache.get_current_running_port()
        if exists_port is None:
            exists_port, _ = self.get_tcp_forward_port()
        if exists_port is None:
            raise NicoError("Start the nico service first!!!!")

        send_tcp_request(exists_port, "start_recording")

    def stop_recording(self, path='output.mp4'):
        logger.debug("stop recording, start to save video")
        time.sleep(1)
        exists_port = self.runtime_cache.get_current_running_port()
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
        exists_port = self.runtime_cache.get_current_running_port()
        respo = send_http_request(exists_port, "device_info", {"value": "get_output_device_name"})
        return respo

    def stop_app(self, package_name):
        command = f'kill {package_name}'
        self.cmd(command)

    def get_system_info(self):
        data_string = self.cmd("info")
        data_dict = {}
        for line in data_string.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data_dict[key.strip()] = value.strip()
        return data_dict

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
        exists_port = self.runtime_cache.get_current_running_port()
        return send_http_request(exists_port, "device_action", {"action": "home"})

    def get_volume(self):
        exists_port = self.runtime_cache.get_current_running_port()
        return send_http_request(exists_port, "device_info", {"value": "get_output_volume"})

    def turn_volume_up(self):
        exists_port = self.runtime_cache.get_current_running_port()
        send_http_request(exists_port, "device_action", {"action": "volume_up"})

    def turn_volume_down(self):
        exists_port = self.runtime_cache.get_current_running_port()
        send_http_request(exists_port, "device_action", {"action": "volume_down"})

    def snapshot(self, name, path):
        self.cmd(f'screenshot {path}/{name}.jpg')

    def get_pic(self, quality=1.0):
        exists_port = self.runtime_cache.get_current_running_port()
        return send_http_request(exists_port, f"get_jpg_pic", {"compression_quality": quality})

    def get_image_object(self, quality=100):
        exists_port = self.runtime_cache.get_current_running_port()
        a = send_http_request(exists_port, f"get_jpg_pic", {"compression_quality": quality})
        nparr = np.frombuffer(a, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image

    def click(self, x, y):
        current_bundleIdentifier = self.runtime_cache.get_current_running_package()
        if current_bundleIdentifier is None:
            current_bundleIdentifier = self.get_current_bundleIdentifier(
                self.runtime_cache.get_current_running_port())

        send_http_request(self.runtime_cache.get_current_running_port(),
                          f"coordinate_action",
                          {"bundle_id": current_bundleIdentifier, "action": "click", "xPixel": x, "yPixel": y,
                           "action_parms": "none"})
        self.runtime_cache.clear_current_cache_ui_tree()

    def get_current_bundleIdentifier(self, port):
        bundle_list = self.get_app_list()
        method = "get_current_bundleIdentifier"
        params = {
            "bundle_ids": ""
        }
        command = []  # Use a list to collect bundle IDs
        for item in bundle_list:
            if item:
                item = item.split(" ")[0]
                command.append(item)  # Append item to the list
        params["bundle_ids"] = ",".join(command)  # Join list items with commas

        return send_http_request(port, method, params)
