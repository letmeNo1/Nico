import os
import tempfile
import time

from common import Common
from get_uiautomator_xml import get_root_element
from ui_object import UiObject

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
    raise TimeoutError(error)


def find_element_exits(root, device_serial, timeout, func, **query):
    try:
        wait_function(root, device_serial, timeout, func, **query)
        return True
    except TimeoutError:
        return False


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


def check_element_exist(root, **query):
    rst = False
    if find_element_by_query(root, **query) != "":
        rst = True
    return rst


def scroll_to_find_element(root, device_serial, scroll_time=10, target_area=None, **query):
    common = Common(device_serial)
    x = int(common.get_screen_size()[0] / 2)
    y1 = int(common.get_screen_size()[1] / 4)
    y2 = int(common.get_screen_size()[1] / 2)
    if target_area is not None:
        x = int(common.get_screen_size()[0] * target_area.get_position()[0])
        y1 = int((common.get_screen_size()[1] * target_area.get_position()[1]) / 4)
        y2 = int((common.get_screen_size()[1] * target_area.get_position()[1]) / 2)
    for i in range(int(scroll_time)):
        print("finding")
        matching_element = find_element_by_query(root, **query)
        if matching_element is not None:
            print("found!")
            return UiObject(root, device_serial, matching_element)

        else:
            print("Couldn't found! try again")
            root = get_root_element(device_serial, True)
            if i == 0:  # first time no find the ele shoule retutrn to top

                os.system("""adb -s %s shell input swipe %s %s %s %s""" % (device_serial, x, y1, x, y2))
            else:
                os.system(
                    """adb -s %s shell input swipe %s %s %s %s""" % (device_serial, x, y2, x, y1))  # swipe up
    return None
