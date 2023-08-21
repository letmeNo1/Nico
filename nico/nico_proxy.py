import re
from nico.get_uiautomator_xml import get_root_node

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
    if len(matching_elements) == 0:
        return None
    else:
        return matching_elements


class NicoProxy:
    def __init__(self, udid, port, found_node=None, **query):
        self.udid = udid
        self.port = port
        self.query = query
        self.found_node = found_node

    def __find_function(self, query, muti=False, index=0):
        action_was_taken = eval(os.getenv(f"{self.udid}_action_was_taken"))
        root = get_root_node(self.udid, self.port, force_reload=action_was_taken)
        found_rst = find_element_by_query(root, query)
        if found_rst is not None:
            if muti:
                return found_rst[index]
            else:
                return found_rst[0]
        return None

    def __wait_function(self, udid, port, timeout, wait_disapper, query):
        time_started_sec = time.time()
        query_string = list(query.values())[0]
        query_method = list(query.keys())[0]
        while time.time() < time_started_sec + timeout:
            found_node = self.__find_function(query)
            if wait_disapper:
                if found_node is None:
                    os.environ[f"{self.udid}_action_was_taken"] = "False"
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {query_method} = {query_string}")
                else:
                    os.environ[f"{self.udid}_action_was_taken"] = "True"
                    logger.debug(f"no found by {query_method} = {query_string}, try again")
            else:
                if found_node is not None:
                    os.environ[f"{self.udid}_action_was_taken"] = "False"
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {query_method} = {query_string}")

                    return found_node
                else:
                    os.environ[f"{self.udid}_action_was_taken"] = "True"
                    logger.debug(f"no found by {query_method} = {query_string}, try again")

        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        raise TimeoutError(error)

    def wait_for_appearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element by {query_method} = {query_string}")

        self.__wait_function(self.udid, self.port, timeout, False, self.query)

    def wait_for_disappearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element by {query_method} = {query_string}")

        self.__wait_function(self.udid, self.port, timeout, True, self.query)

    def wait_for_any(self, *any, timeout=10):
        query_list = []
        for item in any[0]:
            query_list.append(item.query)
        time_started_sec = time.time()
        while time.time() < time_started_sec + timeout:
            for index, query in enumerate(query_list):
                query_string = list(query.values())[0]
                query_method = list(query.keys())[0]
                found_node = self.__find_function(query)
                if found_node is not None:
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {index}. {query_method} = {query_string}")
                    return index

            logger.debug(f"no found any, try again")
            os.environ[f"{self.udid}_action_was_taken"] = "True"
        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        raise TimeoutError(error)

    def get(self, index):
        node = self.__find_function(self.query, True, index)
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        return NicoProxy(self.udid, self.port, found_node=node[index])

    def set_seek_bar(self, percentage):
        x = self.get_bounds()[0] + self.get_bounds()[2] * percentage
        y = self.center_coordinate()[1]
        logger.debug(f"click {x} {y}")

    def exists(self):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"checking element is exists by {query_method}={query_string}...")
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        return self.__find_function(self.query) is not None

    def get_attribute_value(self, attribute_name):
        if self.found_node is None:
            self.found_node = self.__find_function(self.query)
            if self.found_node is None:
                raise UIStructureError(
                    f"Can't found element by {list(self.query.keys())[0]} = {list(self.query.values())[0]}")
            elif type(self.found_node) is list:
                raise UIStructureError(
                    "More than one element has been retrieved, use the 'get' method to specify the number you want")
            os.environ[f"{self.udid}_action_was_taken"] = "False"
        return self.found_node.attrib[attribute_name]

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
        print(len_of_text)
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

    def last_sibling(self):
        root = get_root_node(self.udid, self.port)
        found_node = self.__find_function(self.query)
        last_sibling = None
        for child in root.iter():
            if child == found_node:
                break
            last_sibling = child
        return NicoProxy(udid=self.udid, port=self.port, found_node=last_sibling)

    def next_sibling(self):
        root = get_root_node(self.udid, self.port, eval(os.getenv(f"{self.udid}_action_was_taken")))
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        found_node = self.__find_function(self.query)
        next_sibling = None
        found_current = False
        for child in root.iter():
            # print(child)
            if found_current:
                next_sibling = child
                break
            if child.attrib == found_node.attrib:
                found_current = True
        return NicoProxy(udid=self.udid, port=self.port, found_node=next_sibling)

    def parent(self):
        found_node = self.__find_function(self.query)
        parent_node = found_node.getparent()
        return NicoProxy(udid=self.udid, port=self.port, found_node=parent_node)
