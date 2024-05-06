import os
import tempfile

import lxml.etree as ET


class RunningInfo:
    def __init__(self, udid):
        self.udid = udid

    def get_current_ui_tree(self):
        ui_tree = os.getenv(f"{self.udid}_ui_tree_path")
        if ui_tree is not None:
            if len(ui_tree)>0:
                tree = ET.parse(ui_tree)
                root = tree.getroot()
                return root
        return None

    def set_current_ui_tree(self, ui_tree_string):
        temp_folder = tempfile.gettempdir()
        temp_xml_path = os.path.join(temp_folder, f"{self.udid}_ui.xml")
        os.environ[f"{self.udid}_ui_tree_path"] = temp_xml_path
        with open(temp_xml_path, "w", encoding='utf-8') as file:
            file.write(ui_tree_string)

    def clear_current_ui_tree(self):
        os.environ[f"{self.udid}_ui_tree_path"] = ""
        temp_folder = tempfile.gettempdir()
        temp_xml_path = os.path.join(temp_folder, f"{self.udid}_ui.xml")
        if os.path.exists(temp_xml_path):
            os.remove(temp_xml_path)

    def get_current_running_port(self) -> int:
        return int(os.getenv(f"{self.udid}_running_port"))

    def set_current_running_port(self, port):
        os.environ[f"{self.udid}_running_port"] = str(port)

    def set_action_was_taken(self, action_was_taken: bool):
        os.environ[f"{self.udid}_action_was_taken"] = str(action_was_taken)

    def get_action_was_taken(self) -> bool:
        return os.getenv(f"{self.udid}_action_was_taken") == "True"


