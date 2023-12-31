import os
import re

from nico.nico_proxy import NicoProxy

from nico.logger_config import logger


class UIStructureError(Exception):
    pass


class NicoElement(NicoProxy):
    def __init__(self, udid, port=None, found_node=None, **query):
        super().__init__(udid, port, found_node, **query)
        self.udid = udid
        self.found_node = found_node

    def set_seek_bar(self, percentage):
        x = self.get_bounds()[0] + self.get_bounds()[2] * percentage
        y = self.center_coordinate()[1]
        logger.debug(f"click {x} {y}")
        self.click(x, y)

    def get_attribute_value(self, attribute_name):
        if self.found_node is None:
            self.found_node = self.find_function(self.query)
            if self.found_node is None:
                raise UIStructureError(
                    f"Can't found element by {list(self.query.keys())[0]} = {list(self.query.values())[0]}")
            elif type(self.found_node) is list:
                raise UIStructureError(
                    "More than one element has been retrieved, use the 'get' method to specify the number you want")
            os.environ[f"{self.udid}_action_was_taken"] = "False"
        return self.found_node.attrib[attribute_name]

    def get(self, index):
        found_node = self.find_function(self.query, True, index)
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        return NicoElement(self.udid, found_node=found_node)

    def get_index(self):
        return self.get_attribute_value("index")

    def get_text(self):
        return self.get_attribute_value("text")

    def get_id(self):
        return self.get_attribute_value("resource-id")

    def get_class_name(self):
        return self.get_attribute_value("class")

    def get_package(self):
        return self.get_attribute_value("package")

    def get_content_desc(self):
        return self.get_attribute_value("content-desc")

    def get_checkable(self):
        return self.get_attribute_value("checkable")

    def get_checked(self):
        return self.get_attribute_value("checked")

    def get_clickable(self):
        return self.get_attribute_value("clickable")

    def get_enabled(self):
        return self.get_attribute_value("enabled")

    def get_focusable(self):
        return self.get_attribute_value("focusable")

    def get_focused(self):
        return self.get_attribute_value("focused")

    def get_scrollable(self):
        return self.get_attribute_value("scrollable")

    def get_long_clickable(self):
        return self.get_attribute_value("long-clickable")

    def get_password(self):
        return self.get_attribute_value("password")

    def get_selected(self):
        return self.get_attribute_value("selected")

    def get_bounds(self):
        pattern = r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
        matches = re.findall(pattern, self.get_attribute_value("bounds"))

        left = int(matches[0][0])
        top = int(matches[0][1])
        right = int(matches[0][2])
        bottom = int(matches[0][3])

        # 计算宽度和高度
        width = right - left
        height = bottom - top

        # 计算左上角坐标（x, y）
        x = left
        y = top
        return x, y, width, height

    def center_coordinate(self):
        x, y, w, h = self.get_bounds()
        center_x = x + w // 2
        center_y = y + h // 2
        return center_x, center_y

    def scroll(self, duration=200, direction='vertical_up'):
        if direction not in ('vertical_up', "vertical_down", 'horizontal_left', "horizontal_right"):
            raise ValueError(
                'Argument `direction` should be one of "vertical_up" or "vertical_down" or "horizontal_left"'
                'or "horizontal_right". Got {}'.format(repr(direction)))
        to_x = 0
        to_y = 0
        from_x = self.center_coordinate()[0]
        from_y = self.center_coordinate()[1]
        if direction == "vertical_up":
            to_x = from_x
            to_y = from_y - from_y / 2
        elif direction == "vertical_down":
            to_x = from_x
            to_y = from_y + from_y / 2
        elif direction == "horizontal_left":
            to_x = from_x - from_x / 2
            to_y = from_y
        elif direction == "horizontal_right":
            to_x = from_x + from_x / 2
            to_y = from_y
        command = f'adb -s {self.udid} shell input swipe {from_x} {from_y} {to_x} {to_y} {duration}'
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        os.system(command)

    def click(self, x=None, y=None):
        if x is None and y is None:
            x = self.center_coordinate()[0]
            y = self.center_coordinate()[1]
        command = f'adb -s {self.udid} shell input tap {x} {y}'
        os.system(command)
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        logger.debug(f"click {x} {y}")

    def long_click(self, duration):
        x = self.center_coordinate()[0]
        y = self.center_coordinate()[1]
        command = f'adb -s {self.udid} shell swipe {x} {y} {x} {y} {duration}'
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        os.system(command)

    def set_text(self, text, append=False):
        len_of_text = len(self.get_text())
        self.click()
        os.system(f'adb -s {self.udid} shell input keyevent KEYCODE_MOVE_END')
        del_cmd = f'adb -s {self.udid} shell input keyevent'
        if not append:
            if len_of_text != 0:
                for _ in range(len_of_text):
                    del_cmd = del_cmd + " KEYCODE_DEL"
                os.system(del_cmd)
        text = text.replace("&", "\&")
        os.environ[f"{self.udid}_action_was_taken"] = "True"
        os.system(f'adb -s {self.udid} shell input text "{text}"')
        os.system(f'adb -s {self.udid} shell settings put global policy_control immersive.full=*')

    def last_sibling(self,index=1):
        if self.found_node is None:
            self.found_node = self.find_function(query=self.query)
        previous_node = self.found_node.getprevious()
        if index > 0:
            for i in range(index):
                previous_node = self.found_node.getprevious()
                self.found_node = previous_node
        return NicoElement(udid=self.udid, found_node=previous_node)

    def next_sibling(self, index=1):
        if self.found_node is None:
            self.found_node = self.find_function(query=self.query)
        next_node = self.found_node.getnext()
        if index > 0:
            for i in range(index):
                next_node = self.found_node.getnext()
                self.found_node = next_node
        return NicoElement(udid=self.udid, found_node=next_node)

    def parent(self):
        if self.found_node is None:
            self.found_node = self.find_function(query=self.query)
        parent_node = self.found_node.getparent()
        return NicoElement(udid=self.udid, found_node=parent_node)
