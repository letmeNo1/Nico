import re

from nico.utils import Utils

from nico.get_uiautomator_xml import get_root_node,get_exisit_root_node

import os
import time

from nico.logger_config import logger


class UIStructureError(Exception):
    pass


def find_element_by_query(root, query):
    xpath_expression = ".//*"
    conditions = []
    for attribute, value in query.items():
        attribute = "class" if attribute == "class_name" else attribute
        attribute = "resource-id" if attribute == "id" else attribute

        if attribute.find("Matches") > 0:
            attribute = attribute.replace("Matches", "")
            condition = f"matches(@{attribute},'{value}')"
        elif attribute.find("Contains") > 0:
            attribute = attribute.replace("Match", "")
            condition = f"contains(@{attribute},'{value}')"
        else:
            condition = f"@{attribute}='{value}'"
        conditions.append(condition)
    if conditions:
        xpath_expression += "[" + " and ".join(conditions) + "]"
    matching_elements = root.xpath(xpath_expression)
    if len(matching_elements) == 1:
        return matching_elements[0]
    elif len(matching_elements) == 0:
        return None
    else:
        return matching_elements


class NicoProxy:
    def __init__(self, udid, found_node=None, **query):
        self.udid = udid
        self.query = query
        self.found_node = found_node
        self.close_keyboard()

    def __find_function(self, root, query):
        if root is None or find_element_by_query(root, query) is None:
            root = get_root_node(self.udid)
        return find_element_by_query(root, query)

    def __wait_function(self, udid, timeout, query):
        root = get_root_node(self.udid)
        time_started_sec = time.time()
        query_string = list(query.values())[0]
        query_method = list(query.keys())[0]
        while time.time() < time_started_sec + timeout:
            found_node = self.__find_function(root, query)
            if found_node is not None:
                time.time() - time_started_sec
                logger.debug(f"Found element by {query_method} = {query_string}")
                return found_node
            else:
                logger.debug("no found, try again")
                root = get_root_node(udid)
        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        raise TimeoutError(error)

    def wait_for_appearance(self, timeout=10):
        self.__wait_function(self.udid, timeout, self.query)

    def get(self, index):
        root = get_exisit_root_node(self.udid)
        node = self.__find_function(root, self.query)
        print(node[index])
        print("_____________hank")
        return NicoProxy(self.udid, found_node=node[index])

    def exists(self):
        root = get_root_node(self.udid)
        return self.__find_function(root, self.query) is not None

    def get_attribute_value(self, attribute_name):
        if self.found_node is None:
            root = get_exisit_root_node(self.udid)
            self.found_node = self.__find_function(root, self.query)
            if self.found_node is None:
                raise UIStructureError(
                    f"Can't found element by {list(self.query.keys())[0]} = {list(self.query.values())[0]}")
            elif self.found_node is list:
                raise UIStructureError(
                    "More than one element has been retrieved, use the 'get' method to specify the number you want")

    def close_keyboard(self):
        utils = Utils(self.udid)
        ime_list = utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            utils.qucik_shell(f"ime disable {ime}")

    @property
    def index(self):
        return self.get_attribute_value("index")

    @property
    def text(self):
        return self.get_attribute_value("text")

    @property
    def resource_id(self):
        return self.get_attribute_value("resource-id")

    @property
    def class_name(self):
        return self.get_attribute_value("class")

    @property
    def package(self):
        return self.get_attribute_value("package")

    @property
    def content_desc(self):
        return self.get_attribute_value("content-desc")

    @property
    def checkable(self):
        return self.get_attribute_value("checkable")

    @property
    def checked(self):
        return self.get_attribute_value("checked")

    @property
    def clickable(self):
        return self.get_attribute_value("clickable")

    @property
    def enabled(self):
        return self.get_attribute_value("enabled")

    @property
    def focusable(self):
        return self.get_attribute_value("focusable")

    @property
    def focused(self):
        return self.get_attribute_value("focused")

    @property
    def scrollable(self):
        return self.get_attribute_value("scrollable")

    @property
    def long_clickable(self):
        return self.get_attribute_value("long-clickable")

    @property
    def password(self):
        return self.get_attribute_value("password")

    @property
    def selected(self):
        return self.get_attribute_value("selected")

    @property
    def bounds(self):
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

    @property
    def center_coordinate(self):
        x, y, w, h = self.bounds
        center_x = x + w // 2
        center_y = y + h // 2
        return center_x, center_y

    def click(self):
        x = self.center_coordinate[0]
        y = self.center_coordinate[1]
        command = f'adb -s {self.udid} shell input tap {x} {y}'
        os.system(command)
        logger.debug(f"click {x} {y}")

    def long_click(self, duration):
        x = self.center_coordinate[0]
        y = self.center_coordinate[1]
        command = f'adb -s {self.udid} shell swipe {x} {y} {x} {y} {duration}'
        os.system(command)

    def set_text(self, text):
        len_of_text = len(self.text)
        self.click()
        os.system(f'adb -s {self.udid} shell input keyevent KEYCODE_MOVE_END')
        del_cmd = f'adb -s {self.udid} shell input keyevent'
        for _ in range(len_of_text):
            del_cmd = del_cmd + " KEYCODE_DEL"
        os.system(del_cmd)
        os.system(f'adb -s {self.udid} shell input text "{text}"')

    def last_sibling(self):
        root = get_root_node(self.udid)
        found_node = self.__find_function(root,self.query)
        last_sibling = None
        for child in root.iter():
            if child == found_node:
                break
            last_sibling = child
        return NicoProxy(udid=self.udid, found_node=last_sibling)

    def next_sibling(self):
        root = get_root_node(self.udid)
        found_node = self.__find_function(root,self.query)
        next_sibling = None
        found_current = False
        for child in root.iter():
            if found_current:
                next_sibling = child
                break
            if child == found_node:
                found_current = True
        return NicoProxy(udid=self.udid, found_node=next_sibling)
