import os
import tempfile
import time

import lxml.etree as ET
from auto_nico.common.error import NicoError
from auto_nico.common.send_request import send_tcp_request


def set_large_env_var(var_name, var_value, max_length=30000):
    parts = [var_value[i:i + max_length] for i in range(0, len(var_value), max_length)]

    for index, part in enumerate(parts, start=1):
        env_var_name = f"{var_name}_{index}"
        os.environ[env_var_name] = part


def get_large_env_var(var_name):
    combined_value = ""
    index = 1
    while True:
        env_var_name = f"{var_name}_{index}"
        part = os.environ.get(env_var_name)
        if part is None:
            break
        combined_value += part
        index += 1
    return combined_value


def delete_large_env_var(var_name):
    index = 1
    while True:
        env_var_name = f"{var_name}_{index}"
        if env_var_name not in os.environ:
            break
        os.environ.pop(env_var_name)
        index += 1


class RunningCache:
    def __init__(self, udid):
        self.udid = udid

    def get_current_cache_ui_tree(self):
        ui_tree_part = os.getenv(f"{self.udid}_ui_tree_1")
        if ui_tree_part is not None:
            tree = ET.fromstring(get_large_env_var(f"{self.udid}_ui_tree").encode('utf-8'))
            # root = tree.getroot()
            return tree
        return None

    def set_current_cache_ui_tree(self, ui_tree_string):
        set_large_env_var(f"{self.udid}_ui_tree", ui_tree_string)

    def clear_current_cache_ui_tree(self):
        delete_large_env_var(f"{self.udid}_ui_tree")

    def get_current_running_port(self) -> int:
        return int(os.getenv(f"{self.udid}_running_port"))

    def set_current_running_port(self, port):
        os.environ[f"{self.udid}_running_port"] = str(port)

    def get_ui_change_status(self):
        if self.get_current_cache_ui_tree() is None:
            return True
        if self.is_initialized():
            self.set_initialized(False)
            return True
        else:
            exists_port = self.get_current_running_port()
            rst = send_tcp_request(exists_port, "is_ui_change")
            if "false" in rst:
                return False
            elif "true" in rst:
                return True
            else:
                return False

    def is_initialized(self):
        return os.getenv(f"{self.udid}_initialized") == "True"

    def set_initialized(self, initialized: bool):
        os.environ[f"{self.udid}_initialized"] = str(initialized)

    def set_action_was_taken(self, action_was_taken: bool):
        os.environ[f"{self.udid}_action_was_taken"] = str(action_was_taken)

    def get_action_was_taken(self) -> bool:
        return os.getenv(f"{self.udid}_action_was_taken") == "True"

    def set_current_running_package_name(self, package_name: str):
        os.environ[f"{self.udid}_running_package"] = package_name

    def get_current_running_package(self):
        return os.getenv(f"{self.udid}_running_package")
