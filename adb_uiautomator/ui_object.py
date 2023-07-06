import os
import re


class UiObject:
    def __init__(self, root, udid, found_node):
        self.root = root
        self.found_node = found_node
        self.udid = udid
        self.close_keyboard()
        
    def node_check(self):
        if type(self.found_node) is str:
            raise TimeoutError(self.found_node)
    
    def get_attribute_value(self, attribute_name):
        self.node_check()
        attribute_value = self.found_node.attrib[attribute_name]
        return attribute_value

    def close_keyboard(self):
        os.popen(f'adb -s {self.udid} shell pm disable-user com.android.inputmethod.latin')

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
    
    
    def exits(self):
        if self.found_node is None:
            return False
        else:
            return True
            

    def click(self):
        x = self.center_coordinate[0]
        y = self.center_coordinate[1]
        command = f'adb -s {self.udid} shell input tap {x} {y}'
        os.system(command)

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
        self.node_check()
        last_sibling = None
        for child in self.root.iter():
            if child == self.found_node:
                break
            last_sibling = child
        return UiObject(self.root, self.udid, last_sibling)

    def next_sibling(self):
        self.node_check()
        next_sibling = None
        found_current = False
        for child in self.root.iter():
            if found_current:
                next_sibling = child
                break
            if child == self.found_node:
                found_current = True
        return UiObject(self.root, self.udid, next_sibling)
