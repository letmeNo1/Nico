from adb_uiautomator.common import Common
from adb_uiautomator.get_uiautomator_xml import get_root_element
from adb_uiautomator.ui_object import UiObject

import os
import time


def wait_function(root, device_serial, timeout, func, **query):
    time_started_sec = time.time()
    query_string = list(query.values())[0]
    query_method = list(query.keys())[0]
    while time.time() < time_started_sec + timeout:
        found_node = func(root, **query)
        if found_node is not None:
            time.time() - time_started_sec
            print(f"Found element by {query_method} = {query_string}")
            if type(found_node) is list:
                return [UiObject(root, device_serial, node) for node in found_node]
            else:
                return UiObject(root, device_serial, found_node)
        else:
            print("no found, try again")
            root = get_root_element(device_serial, True)
    error = "Can't find element/elements in %s s by %s = %s" % (timeout, query_method, query_string)
    return UiObject(root, device_serial, error)


def find_element_by_query(root, **query):
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
