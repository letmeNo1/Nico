import json
import os
import platform
import random
import re
import time
import subprocess
import requests

import cv2
import numpy as np
import psutil

from loguru import logger
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.common.send_request import send_http_request
from auto_nico.common.error import NicoError


class IdbUtils:
    def __init__(self, udid):
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        self.ios_path = os.path.join(current_dir, "lib", "ios.exe")
        self.load_developer_image_path = os.path.join(current_dir, "lib", "load_developer_image.exe")
        self.udid = udid
        self.runtime_cache = RunningCache(udid)
        self.tunnel_agent_port = "55105"

    def get_actual_wh(self):
        exists_port = self.runtime_cache.get_current_running_port()
        rst = send_http_request(exists_port, "get_actual_wh")
        matches = rst.split(",")
        target_w = int(float(matches[0]))
        target_h = int(float(matches[1]))
        return target_w, target_h

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

    def get_app_list(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(f"tidevice --udid {self.udid} applist", capture_output=True, text=True,
                                encoding='utf-8')
        result_list = result.stdout.splitlines()
        return result_list

    def get_test_server_package(self):
        app_list = self.get_app_list()
        xctrunner_package_name = [s for s in app_list if "nico.dump-hierarchyUITests.hank.xctrunner " in s][0].split(" ")[0]
        return {"test_server_package": xctrunner_package_name}

    def get_wda_server_package(self):
        app_list = self.get_app_list()
        test_server_package = [s for s in app_list if s.startswith('com.facebook')]
        return test_server_package[0].split(" ")[0]

    def start_app(self, package_name):
        exists_port = self.runtime_cache.get_current_running_port()
        self.runtime_cache.set_current_running_package_name(package_name)
        return send_http_request(exists_port, "activate_app", {"bundle_id": package_name})

    def stop_test_server(self):
        exists_port = self.runtime_cache.get_current_running_port()
        send_http_request(exists_port, "stop_test")

    def _init_test_server(self):
        self.load_developer_image()
        self.__start_tunnel()
        self._set_running_port("random")
        self.__start_server()

    def __start_tunnel(self):
        subprocess.run(["taskkill", "/F", "/IM", "ios.exe"], shell=True, capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "go-ios.exe"], shell=True, capture_output=True)
        time.sleep(0.5)

        tunnel_url = f"http://127.0.0.1:{self.tunnel_agent_port}/tunnels"

        tunnel_ready = False
        try:
            resp = requests.get(tunnel_url, timeout=3)
            logger.debug(f"Check existing tunnel response: {resp.text}")
            if resp.status_code == 200 and self.udid in resp.text:
                logger.debug(f"tunnel for {self.udid} already started on port {self.tunnel_agent_port}")
                return
        except Exception as e:
            logger.debug(f"No existing tunnel: {str(e)}")

        logger.debug(f"{self.ios_path} tunnel start --udid={self.udid}")
        command = f"{self.ios_path} tunnel start --udid={self.udid} --userspace"

        env = os.environ.copy()
        env["ENABLE_GO_IOS_AGENT"] = "user"
        env["GO_IOS_AGENT_PORT"] = self.tunnel_agent_port

        subprocess.Popen(command, shell=True, env=env)

        for idx in range(20):
            try:
                resp = requests.get(tunnel_url, timeout=3)
                logger.debug(f"Poll {idx+1} resp code:{resp.status_code}, body:{resp.text}")
                if resp.status_code == 200 and self.udid in resp.text:
                    logger.debug(f"tunnel for {self.udid} is started on port {self.tunnel_agent_port}")
                    tunnel_ready = True
                    break
            except Exception as e:
                logger.debug(f"Poll {idx+1} connect fail: {str(e)}")
            time.sleep(1)

        if not tunnel_ready:
            raise NicoError(f"tunnel for {self.udid} is not started")

    def __start_server(self):
        current_port = self.runtime_cache.get_current_running_port()
        test_server_package = self.get_test_server_package().get('test_server_package')
        logger.debug(
            f"{self.ios_path} runwda --bundleid {test_server_package} --testrunnerbundleid {test_server_package} --xctestconfig=dump_hierarchyUITests.xctest --udid={self.udid}")

        commands = f"{self.ios_path} runwda --bundleid {test_server_package} --testrunnerbundleid {test_server_package} --xctestconfig=dump_hierarchyUITests.xctest --udid={self.udid}"
        env = os.environ.copy()
        env["ENABLE_GO_IOS_AGENT"] = "user"
        env["GO_IOS_AGENT_PORT"] = self.tunnel_agent_port
        subprocess.Popen(commands, shell=True, env=env)

        for _ in range(10):
            try:
                response = send_http_request(current_port, "check_status")
                if response is not None:
                    logger.debug(f"{self.udid}'s test server is ready")
                    logger.debug(f"{self.udid}'s uiautomator was initialized successfully")
                    return
            except Exception as e:
                logger.debug(f"Waiting WDA ready: {e}")
            time.sleep(1)
        raise Exception(f"{self.udid}'s uiautomator was initialized faild")

    def _set_tcp_forward_port(self, current_port):
        logger.debug(
            f"""tidevice --udid {self.udid} relay {current_port} 8200""")
        commands = f"""tidevice --udid {self.udid} relay {current_port} 8200"""
        try:
            subprocess.Popen(commands, shell=True)
        except OSError:
            logger.error("start fail")
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
            self._set_tcp_forward_port(running_port)
        else:
            running_port = int(exists_port)
        logger.debug(f"{self.udid}'s running port is {running_port}")

        RunningCache(self.udid).set_current_running_port(running_port)

    def _send_http_request_with_check_server_ready(self, method, params=None):
        exists_port = self.runtime_cache.get_current_running_port()
        rst = False
        try:
            rst = send_http_request(exists_port, "check_status") is not None
        except Exception:
            pass
        if not rst:
            logger.debug(f"{self.udid} test server disconnect, restart ")
            self._init_test_server()
        return send_http_request(exists_port, method, params, timeout=10)

    def activate_app(self, package_name):
        self._send_http_request_with_check_server_ready("activate_app", {"bundle_id": package_name})

    def terminate_app(self, package_name):
        self._send_http_request_with_check_server_ready("terminate_app", {"bundle_id": package_name})

    def get_output_device_name(self):
        respo = self._send_http_request_with_check_server_ready("device_info",
                                                                {"value": "get_output_device_name"})
        return respo

    def stop_app(self, package_name):
        exists_port = self.runtime_cache.get_current_running_port()
        respo = self._send_http_request_with_check_server_ready("terminate_app",
                                                                {"bundle_id": package_name})
        return respo

    def dump_app(self, package_name):
        exists_port = self.runtime_cache.get_current_running_port()
        respo = self._send_http_request_with_check_server_ready("dump_tree", {"bundle_id": package_name})
        return respo

    def get_system_info(self):
        data_string = os.popen(f"tidevice --udid {self.udid} info").read()
        data_dict = {}
        for line in data_string.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data_dict[key.strip()] = value.strip()
        return data_dict

    def cmd(self, cmd):
        udid = self.udid
        try:
            if self.is_greater_than_ios_17():
                result = subprocess.run(f'''ios {cmd} --udid={udid}''', shell=True, capture_output=True, text=True,
                                        check=True, timeout=10).stdout
            else:
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
        return self._send_http_request_with_check_server_ready("device_action", {"action": "home"})

    def get_volume(self):
        return self._send_http_request_with_check_server_ready("device_info",
                                                               {"value": "get_output_volume"})

    def turn_volume_up(self):
        self._send_http_request_with_check_server_ready("device_action", {"action": "volume_up"})

    def turn_volume_down(self):
        self._send_http_request_with_check_server_ready("device_action", {"action": "volume_down"})

    def snapshot(self, name, path):
        self.cmd(f'screenshot {path}/{name}.jpg')

    def get_pic(self, quality=1.0):
        return self._send_http_request_with_check_server_ready(f"get_jpg_pic",
                                                               {"compression_quality": quality})

    def get_image_object(self, quality=100):
        a = self._send_http_request_with_check_server_ready(f"get_jpg_pic",
                                                            {"compression_quality": quality})
        nparr = np.frombuffer(a, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image

    def click(self, x, y, bundleIdentifier=None):
        current_bundleIdentifier = bundleIdentifier if bundleIdentifier is not None else self.runtime_cache.get_current_running_package()
        if current_bundleIdentifier is None:
            current_bundleIdentifier = self.get_current_bundleIdentifier(
                self.runtime_cache.get_current_running_port())

        self._send_http_request_with_check_server_ready(f"coordinate_action",
                                                        {"bundle_id": current_bundleIdentifier, "action": "click",
                                                         "xPixel": x, "yPixel": y,
                                                         "action_parms": "none"})
        self.runtime_cache.clear_current_cache_ui_tree()

    def get_current_bundleIdentifier(self, port):
        bundle_list = self.get_app_list()
        method = "get_current_bundleIdentifier"
        params = {
            "bundle_ids": ""
        }
        command = []
        for item in bundle_list:
            if item:
                item = item.split(" ")[0]
                command.append(item)
        params["bundle_ids"] = ",".join(command)

        return self._send_http_request_with_check_server_ready(method, params)

    def get_xpaths(self, id, xpath):
        return self._send_http_request_with_check_server_ready(f"find_element_by_query",
                                                               {"bundle_id": id, "query_method": "predicate",
                                                                "query_value": xpath})

    def stop_test(self, ):
        return self._send_http_request_with_check_server_ready(f"stop_test")

    def reboot(self):
        os.popen(f"{self.ios_path} reboot --udid={self.udid}").read()

    def wait_device_ready(self, timeout=120):
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.device_list()
            if self.udid in result:
                logger.debug(f"{self.udid} is ready")
                return True
            time.sleep(5)
        raise NicoError(f"{self.udid} is not ready after waiting for {timeout} seconds")

    def load_developer_image(self):
        exe_path = self.load_developer_image_path

        TEMP_DIR = os.environ.get("TEMP")
        RESULT_FILE = os.path.join(TEMP_DIR, "ios_mount_result.txt")

        if os.path.exists(RESULT_FILE):
            os.remove(RESULT_FILE)
            logger.debug(f"Pre-cleared temp result file: {RESULT_FILE}")

        cmd = [exe_path, self.udid]
        logger.debug(f"Running mount tool at: {exe_path} with UDID: {self.udid}")

        try:
            subprocess.run(cmd, check=False, capture_output=True, text=True)
        except Exception as e:
            logger.debug(f"Failed to run mount tool: {str(e)}")
            return

        wait_timeout = 30
        wait_interval = 0.2
        start_time = time.time()
        file_ready = False

        while time.time() - start_time < wait_timeout:
            if os.path.exists(RESULT_FILE):
                if os.path.getsize(RESULT_FILE) > 0:
                    file_ready = True
                    break
            time.sleep(wait_interval)

        if not file_ready:
            logger.debug(f"Timeout: Result file is empty or not created after {wait_timeout}s")

        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            status = "UNKNOWN"
            log = "NO LOG"
            for line in lines:
                line = line.strip()
                if line.startswith("STATUS="):
                    status = line.replace("STATUS=", "")
                if line.startswith("LOG="):
                    log = line.replace("LOG=", "")

            logger.debug("=" * 50)
            logger.debug("Execution Result")
            logger.debug("=" * 50)
            logger.debug(f"Status: {status}")
            logger.debug(f"Log: {log}")

        except Exception as e:
            logger.debug(f"Read result failed: {e}")

        finally:
            if os.path.exists(RESULT_FILE):
                os.remove(RESULT_FILE)
                logger.debug("\nTemp file cleared successfully!")


# if __name__ == "__main__":
#     aa = IdbUtils("00008140-000809141E02801C")
#     aa._init_test_server()
#     print(aa.get_volume())