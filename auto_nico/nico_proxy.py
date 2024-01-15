from nico.get_uiautomator_xml import get_root_node, get_root_node_with_output

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


class NicoProxy:
    def __init__(self, udid, port, found_node=None, index=0, **query):
        self.udid = udid
        self.port = port
        self.query = query
        self.index = index
        self.found_node = found_node

    def _find_function(self, query, muti=False, index=0):
        action_was_taken = eval(os.getenv(f"{self.udid}_action_was_taken"))
        root = get_root_node(self.udid, self.port, force_reload=action_was_taken)
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

        error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
        raise TimeoutError(error)

    def wait_for_appearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element by {query_method} = {query_string}")
        self.__wait_function(timeout, False, self.query)

    def wait_for_disappearance(self, timeout=10):
        query_string = list(self.query.values())[0]
        query_method = list(self.query.keys())[0]
        logger.debug(f"Waiting element by {query_method} = {query_string}")

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

    def get_root_xml(self):
        PATH = get_root_node_with_output(self.udid, self.port, True)
        print(PATH)
        os.startfile(PATH)

    def get_root_node(self):
        return get_root_node(self.udid, self.port, force_reload=True)
