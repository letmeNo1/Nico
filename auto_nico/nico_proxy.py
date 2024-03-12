import tempfile

import os
import time
from auto_nico.logger_config import logger
from auto_nico.send_request import send_tcp_request


import lxml.etree as ET


class UIStructureError(Exception):
    pass


def find_element_by_query(root, query):
    xpath_expression = ".//*"
    conditions = []
    for attribute, value in query.items():
        if attribute == "compressed":
            pass
        else:
            attribute = "class" if attribute == "class_name" else attribute
            attribute = "resource-id" if attribute == "id" else attribute
            attribute = "content-desc" if attribute == "content_desc" else attribute

            if attribute.find("_matches") > 0:
                attribute = attribute.replace("_matches", "")
                condition = f"matches(@{attribute},'{value}')"
            elif attribute.find("_contains") > 0:
                attribute = attribute.replace("_contains", "")
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


def get_root_node(udid, port, compressed, force_reload=False):
    temp_folder = tempfile.gettempdir()
    def dump_ui_xml(udid, port, compressed):
        temp_folder = tempfile.gettempdir()
        for _ in range(5):
            response = send_tcp_request(port, f"dump_{str(compressed).lower()}")
            # print(response)
            if '''hierarchy rotation''' in response:
                with open(os.path.join(temp_folder, f"{udid}_ui.xml"), "w", encoding='utf-8') as file:
                    file.write(response)
                root = ET.fromstring(response.encode('utf-8'))
                return root
            else:
                logger.debug("uiautomator dump fail, retrying...")
        raise UIStructureError("uiautomator dump fail")

    if force_reload:
        return dump_ui_xml(udid, port, compressed)
    else:
        PATH = os.path.join(temp_folder, f"{udid}_ui.xml")
        if os.path.exists(PATH):
            with open(PATH, "r", encoding='utf-8') as file:
                response = file.read()
                root = ET.fromstring(response.encode('utf-8'))
                return root
        else:
            return dump_ui_xml(udid, port, compressed)


class NicoProxy:
    def __init__(self, udid, port, found_node=None, index=0, **query):
        self.udid = udid
        self.port = port
        self.query = query
        self.index = index
        self.found_node = found_node

    def _find_function(self, query, muti=False, index=0):
        if query.get("compressed") is not None:
            compressed = query.get("compressed")
        else:
            compressed = True
        action_was_taken = eval(os.getenv(f"{self.udid}_action_was_taken"))
        root = get_root_node(self.udid, self.port, compressed, force_reload=action_was_taken)
        found_rst = find_element_by_query(root, query)
        if found_rst is not None:
            if muti == "all":
                return found_rst
            elif muti is True:
                return found_rst[index]
            else:
                return found_rst[0]
        return None

    def __wait_function(self, timeout, wait_disappear, query):
        time_started_sec = time.time()
        query_string = list(query.values())[0]
        query_method = list(query.keys())[0]
        while time.time() < time_started_sec + timeout:
            found_node = self._find_function(query)
            if wait_disappear:
                if found_node is None:
                    os.environ[f"{self.udid}_action_was_taken"] = "False"
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {query_method} = {query_string}")
                    return 1
                else:
                    os.environ[f"{self.udid}_action_was_taken"] = "True"
            else:
                if found_node is not None:
                    os.environ[f"{self.udid}_action_was_taken"] = "False"
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {query_method} = {query_string}")
                    return 1
                else:
                    os.environ[f"{self.udid}_action_was_taken"] = "True"
        if wait_disappear:
            error = "Can't wait element/elements disappear in %s s by %s = %s" % (timeout, query_method, query_string)
        else:
            error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        raise TimeoutError(error)

    def wait_for_appearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element appearance by {query_method} = {query_string}")
        self.__wait_function(timeout, False, self.query)

    def wait_for_disappearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element disappear by {query_method} = {query_string}")

        self.__wait_function(timeout, True, self.query)

    def wait_for_any(self, *any, timeout=10):
        find_times = 0
        query_list = []
        for item in any[0]:
            query_list.append(item.query)
        time_started_sec = time.time()
        while time.time() < time_started_sec + timeout:
            for index, query in enumerate(query_list):
                query_string = list(query.values())[0]
                query_method = list(query.keys())[0]
                found_node = self._find_function(query)
                if found_node is not None:
                    time.time() - time_started_sec
                    logger.debug(f"Found element by {index}. {query_method} = {query_string}")
                    return index
            find_times += 1
            if find_times == 1:
                logger.debug(f"no found any, try again")
            os.environ[f"{self.udid}_action_was_taken"] = "True"
        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        os.environ[f"{self.udid}_action_was_taken"] = "False"
        raise TimeoutError(error)

    def exists(self):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"checking element is exists by {query_method}={query_string}...")
        rst = self._find_function(self.query) is not None
        return rst

    def get_root_xml(self, compressed):
        get_root_node(self.udid, self.port, compressed, True)
        temp_folder = os.path.join(tempfile.gettempdir(),f"{self.udid}_ui.xml")
        os.startfile(temp_folder)
