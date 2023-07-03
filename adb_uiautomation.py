import os
import subprocess
import tempfile

from adb_uiautomator.common import Common
from find_ui_element import wait_function, find_element_by_query, find_elements_by_query, \
    scroll_to_find_element


class UIStructureError(Exception):
    pass


class AdbUiautomator(Common):
    def __init__(self, udid):
        self.udid = udid
        remove_xml(self.udid)

    def find_element_by_wait(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return wait_function(root, self.udid, timeout, find_element_by_query, **query)

    def check_element_exists(self, timeout=10, **query):
        root = get_root_element(self.udid)
        return find_element_exits(root, self.udid, timeout, find_element_by_query, **query)

    def scroll_to_find_element(self, scroll_time=10, target_area=None, **query):
        root = get_root_element(self.udid)
        return scroll_to_find_element(root, self.udid, scroll_time, target_area, **query)

    #
    # def find_last_element_by_wait(self, timeout=5000, use_re=False, **query):
    #     return wait_function(timeout, use_re, find_element_by_query, self, "last", **query)
    #
    # def find_elements_by_wait(self, timeout=5000, use_re=False, **query):
    #     return wait_function(timeout, use_re, find_elements_by_query, self, **query)
    # def check_element_exist(self,timeout=5000, use_re=False, **query):
    #     return wait_exist(timeout, use_re, find_elements_by_query, self, **query)

# start_time = time.time()
#
# # print(get_ui_xml("290aa9aac2a29a1e"))

# aa.find_element_by_wait(textMatch = "et")
# root = aa.get_ui_xml()
# # 定义要查找的属性名和属性值
# target_attribute_name = 'class'  # 替换为实际的属性名
# target_attribute_value = 'android.widget.EditText'  # 替换为实际的属性值
#
# # matching_element = (aa.find_element_by_wait(timeout=60000,text="Time Server (NTP)"))
# # bb = matching_element.previous_element()
# # print(bb.text)
# print("done")
# # print(matching_element.next_sibling().text)
# # print(matching_element.center_coordinate)
# # 构建XPath表达式
# end_time = time.time()
# execution_time = end_time - start_time
#
# print("代码运行时间：", execution_time, "秒")
# xpath_expression = f".//*[@{target_attribute_name}='{target_attribute_value}']"
# #
# # # # 使用XPath进行查询
# # matching_elements = root.findall(xpath_expression)
#
# matching_element = root.find(xpath_expression)
# print(matching_element)
#
#
# # 打印匹配的元素
# # for element in matching_elements:
# #     print("匹配的元素:")
# #     print("标签:", element.tag)
# #     print("属性:")
# #     for attr_name, attr_value in element.attrib.items():
# #         print(f"{attr_name}: {attr_value}")
#
# for attr_name, attr_value in matching_element.attrib.items():
#     print(f"{attr_name}: {attr_value}")
# AUTO = AdbUiautomation("5a3317f35a33")
# AUTO.find_element_by_wait(text="Accept").click()