import json
import time

import os

from lxml.etree import _Element

from auto_nico.common.running_info import RunningInfo
from auto_nico.ios.XCUIElementType import get_value_by_element_type
from typing import Union
from lxml import etree

import tempfile

from auto_nico.common.logger_config import logger
from auto_nico.common.send_request import send_tcp_request

import lxml.etree as ET

from auto_nico.ios.tools.format_converter import converter


class UIStructureError(Exception):
    pass


class NicoProxy:
    def __init__(self, udid, port, found_node=None, package_name=None, **query):
        self.package_name = package_name
        self.udid = udid
        self.port = port
        self.query = query
        self.found_node = found_node

    def _dump_ui_xml(self, configuration):
        platform = configuration.get("platform")
        response = None
        for _ in range(5):
            if platform == "NicoAndroidElement":
                compressed = configuration.get("compressed")
                response = send_tcp_request(self.port, f"dump_{str(compressed).lower()}").replace("class=",
                                                                                                  "class_name=").replace(
                    "resource-id=", "id=").replace("content-desc=", "content_desc=")
            elif platform == "NicoIOSElement":
                package_name = configuration.get("package_name")
                response = send_tcp_request(self.port, f"dump_tree:{package_name}")
                response = converter(response)

            if '''hierarchy''' in str(response):
                # logger.debug(f"{self.udid}'s UI tree is dump success!!!")
                running_info = RunningInfo(self.udid)
                running_info.set_current_ui_tree(response)
                root = ET.fromstring(response.encode('utf-8'))
                return root
            else:
                pass
                # logger.debug(f"{self.udid}'s UI tree dump fail, retrying...")
        raise UIStructureError(f"{self.udid}'s UI tree dump fail")

    def _get_root_node(self, configuration: dict):
        """
        get the root node of the element tree
        @param configuration: The configuration of the platform
        @param udid: The device ID
        @param port: The port number of automation server
        @param force_reload: Whether to force reload the element tree, default is False
        @return: The root node of the element tree
        """
        ui_tree = RunningInfo(self.udid).get_current_ui_tree()
        if ui_tree is not None:
            # logger.debug(f"{self.udid}'s UI Tree already exists. There is no need to dump again!!")
            return ui_tree
        else:
            return self._dump_ui_xml(configuration)

    def __find_function_by_xml(self, query, multi=False, index=0, return_all=False) -> Union[_Element, None]:
        def __find_element_by_query_by_xml(root, query) -> Union[list, None]:
            xpath_expression = ".//*"
            conditions = []
            for attribute, value in query.items():
                if attribute == "compressed":
                    pass
                else:
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

        # logger.debug(f"{self.udid}'s UI tree is dumping!!")
        if query.get("compressed") is not None:
            compressed = query.get("compressed")
        else:
            compressed = True
        configuration = {
            "platform": self.__class__.__name__,
            "compressed": compressed,
            "package_name": self.package_name
        }
        root = self._get_root_node(configuration)
        found_rst = __find_element_by_query_by_xml(root, query)
        if found_rst is not None:
            if return_all is True:
                logger.debug(f"Found element: {found_rst}")
                return found_rst
            if multi is True:
                logger.debug(f"Found element: {found_rst[index]}")
                return found_rst[index]
            else:
                logger.debug(f"Found element: {found_rst[0]}")
                return found_rst[0]
        return None

    def __find_element_by_query_for_ios(self, query, return_all=False) -> Union[dict, None]:
        NSPredicate_list = []
        for attribute, value in query.items():
            if attribute == "xpath":
                xpath_expression = value
                matching_element = send_tcp_request(self.port,
                                                    f"find_element_by_query:{self.package_name}:xpath:{xpath_expression}")
                if matching_element == "":
                    return None
                logger.debug(f"found element: {matching_element}")
                return json.loads(matching_element)
            elif attribute == "custom":
                if return_all:
                    matching_element = send_tcp_request(self.port,
                                                        f"find_elements_by_query:{self.package_name}:predicate:{value}")
                else:
                    matching_element = send_tcp_request(self.port,
                                                        f"find_element_by_query:{self.package_name}:predicate:{value}")
                if matching_element == "":
                    return None
                logger.debug(f"found element: {matching_element}")
                return json.loads(matching_element)
            else:
                if attribute.find("_contains") > 0:
                    if attribute == "text_contains":
                        condition = f'''label CONTAINS "{value}" OR title CONTAINS "{value}"'''
                    else:
                        attribute = attribute.replace("_contains", "")
                        condition = f"{attribute} CONTAINS {value}"
                else:
                    if attribute == "text":
                        condition = f'''label == "{value}" OR title == "{value}"'''
                    elif attribute == "class_name":
                        condition = f'''elementType == {get_value_by_element_type(value)}'''
                    else:
                        condition = f'''{attribute} == "{value}"'''
                NSPredicate_list.append(condition)
        NSPredicate = " AND ".join(NSPredicate_list)
        if return_all:
            matching_elements = send_tcp_request(self.port,
                                                 f"find_elements_by_query:{self.package_name}:predicate:{NSPredicate}")
            return json.loads(f"[{matching_elements}]")

        else:
            matching_element = send_tcp_request(self.port,
                                                f"find_element_by_query:{self.package_name}:predicate:{NSPredicate}")
            if matching_element == "":
                return None
        logger.debug(f"found element: {matching_element}")
        return json.loads(matching_element)

    def _find_function(self, query, use_xml=False) -> Union[dict, _Element]:
        platform = self.__class__.__name__,
        if "NicoAndroid" in str(platform) or use_xml:
            found_element = self.__find_function_by_xml(query)
        elif "NicoIOS" in str(platform):
            found_element = self.__find_element_by_query_for_ios(query)
        else:
            raise Exception("Unsupported platform")
        return found_element

    def _find_all_function(self, query):
        platform = self.__class__.__name__,
        element_list = []
        if "NicoAndroidElement" in platform:
            element_list = self.__find_function_by_xml(query, return_all=True)
        elif "NicoIOSElement" in platform:
            element_list = self.__find_element_by_query_for_ios(query, return_all=True)
        return element_list

    def __wait_function(self, timeout, wait_disappear, query):
        time_started_sec = time.time()
        query_string = list(query.values())[0]
        query_method = list(query.keys())[0]
        while time.time() < time_started_sec + timeout:
            found_node = self._find_function(query)
            if wait_disappear:
                if found_node is None:
                    time.time() - time_started_sec
                    return 1
                else:
                    RunningInfo(self.udid).clear_current_ui_tree()
            else:
                if found_node is not None:
                    time.time() - time_started_sec
                    return 1
                else:
                    RunningInfo(self.udid).clear_current_ui_tree()

        if wait_disappear:
            error = "Can't wait element/elements disappear in %s s by %s = %s" % (timeout, query_method, query_string)
        else:
            error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        raise TimeoutError(error)

    def wait_for_appearance(self, timeout=10, force_reload=False):
        if force_reload:
            RunningInfo(self.udid).clear_current_ui_tree()
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element appearance by {query_method} = {query_string}")
        self.__wait_function(timeout, False, self.query)

    def wait_for_disappearance(self, timeout=10, force_reload=False):
        if force_reload:
            RunningInfo(self.udid).clear_current_ui_tree()
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
            RunningInfo(self.udid).clear_current_ui_tree()
        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        RunningInfo(self.udid).set_action_was_taken(False)
        raise TimeoutError(error)

    def exists(self):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"checking element is exists by {query_method}={query_string}...")
        rst = self._find_function(self.query) is not None
        return rst

    def get_root_xml(self, compressed):
        configuration = {
            "platform": self.__class__.__name__,
            "compressed": compressed,
        }
        self._get_root_node(configuration)
        temp_folder = os.path.join(tempfile.gettempdir(), f"{self.udid}_ui.xml")
        os.startfile(temp_folder)
