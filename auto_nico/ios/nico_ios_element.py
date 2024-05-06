import os
import re

from auto_nico.common.logger_config import logger
from auto_nico.common.nico_element import NicoElement
from auto_nico.common.running_info import RunningInfo
from auto_nico.common.send_request import send_tcp_request
from auto_nico.ios.XCUIElementType import get_element_type_by_value


class UIStructureError(Exception):
    pass


class NicoIOSElement(NicoElement):
    def __init__(self, **query):
        self.query = query
        super().__init__(**query)

    @property
    def index(self):
        return self._get_attribute_value("index")

    def get_index(self):
        return self.index

    @property
    def text(self):
        if self._get_attribute_value("label") is not None:
            return self._get_attribute_value("label")
        elif self._get_attribute_value("title") is not None:
            return self._get_attribute_value("title")
        return None

    def get_text(self):
        return self.text

    @property
    def identifier(self):
        return self._get_attribute_value("identifier")

    def get_identifier(self):
        return self.identifier

    @property
    def value(self):
        return self._get_attribute_value("value")

    def get_value(self):
        return self.value

    @property
    def xpath(self):
        return self._get_attribute_value("xpath")

    def get_xpath(self):
        return self.xpath

    @property
    def class_nam(self):
        return get_element_type_by_value(self._get_attribute_value("elementType"))

    def get_class_nam(self):
        return self.class_nam

    @property
    def bounds(self):
        pattern = r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
        bounds = self._get_attribute_value("bounds")
        if bounds is None:
            frame = self._get_attribute_value("frame")
            bounds = f'[{int(frame.get("X"))},{int(frame.get("Y"))}][{int(frame.get("Width"))},{int(frame.get("Height"))}]'
        matches = re.findall(pattern, bounds)
        x = int(matches[0][0])
        y = int(matches[0][1])
        w = int(matches[0][2])
        h = int(matches[0][3])
        l = int(matches[0][2]) + x
        t = int(matches[0][3]) + y

        return x, y, w, h, l, t

    def center_coordinate(self):
        x, y, w, h, l, t = self.bounds
        center_x = x + (w) // 2
        center_y = y + (h) // 2
        return center_x, center_y

    def click(self, x=None, y=None, x_offset=None, y_offset=None):
        if x is None and y is None:
            x = self.center_coordinate()[0]
            y = self.center_coordinate()[1]
        if x_offset is not None:
            x = x + x_offset
        if y_offset is not None:
            y = y + y_offset
        send_tcp_request(self.port, f"coordinate_action:{self.package_name}:click:{x}:{y}:none")
        RunningInfo(self.udid).set_action_was_taken(True)
        logger.debug(f"click {x} {y}")

    def long_click(self, duration, x_offset=None, y_offset=None):
        x = self.center_coordinate()[0]
        y = self.center_coordinate()[1]
        if x_offset is not None:
            x = x + x_offset
        if y_offset is not None:
            y = y + y_offset
        send_tcp_request(self.port, f"coordinate_action:{self.package_name}:press:{x}:{y}:{float(duration)}")
        RunningInfo(self.udid).set_action_was_taken(True)
        logger.debug(f"click {x} {y}")

    def set_text(self, text, append=False, x_offset=None, y_offset=None):
        len_of_text = len(self.get_text())
        self.click(x_offset=x_offset, y_offset=y_offset)
        os.system(f'adb -s {self.udid} shell input keyevent KEYCODE_MOVE_END')
        del_cmd = f'adb -s {self.udid} shell input keyevent'
        if not append:
            if len_of_text != 0:
                for _ in range(len_of_text):
                    del_cmd = del_cmd + " KEYCODE_DEL"
                os.system(del_cmd)
        text = text.replace("&", "\&").replace("\"", "")
        RunningInfo(self.udid).set_action_was_taken(True)
        os.system(f'''adb -s {self.udid} shell input text "{text}"''')
        os.system(f'adb -s {self.udid} shell settings put global policy_control immersive.full=*')

    def get(self, index):
        node = self._get(index)
        NAE = NicoIOSElement()
        NAE.set_current_node(node)
        NAE.set_udid(self.udid)
        NAE.set_package_name(self.package_name)
        NAE.set_port(self.port)
        return NAE

    def all(self):
        eles = self._find_all_function(self.query)
        RunningInfo(self.udid).set_action_was_taken(False)
        if eles == []:
            return eles
        ALL_NAE_LIST = []
        for ele in eles:
            NAE = NicoIOSElement()
            NAE.set_query(self.query)
            NAE.set_port(self.port)
            NAE.set_udid(self.udid)
            NAE.set_package_name(self.package_name)
            NAE.set_current_node(ele)

            ALL_NAE_LIST.append(NAE)
        return ALL_NAE_LIST

    def last_sibling(self, index=0):
        previous_node = self._last_sibling(index)
        NAE = NicoIOSElement()
        NAE.set_query(self.query)
        NAE.set_port(self.port)
        NAE.set_udid(self.udid)
        NAE.set_package_name(self.package_name)
        NAE.set_current_node(previous_node)
        return NAE

    def next_sibling(self, index=0):
        next_node = self._next_sibling(index)
        NAE = NicoIOSElement()
        NAE.set_query(self.query)
        NAE.set_port(self.port)
        NAE.set_udid(self.udid)
        NAE.set_package_name(self.package_name)
        NAE.set_current_node(next_node)
        return NAE

    def parent(self):
        parent_node = self._parent()
        NAE = NicoIOSElement()
        NAE.set_query(self.query)
        NAE.set_port(self.port)
        NAE.set_udid(self.udid)
        NAE.set_package_name(self.package_name)
        NAE.set_current_node(parent_node)
        return NAE

    def child(self, index=0):
        child_node = self._child(index)
        NAE = NicoIOSElement()
        NAE.set_query(self.query)
        NAE.set_port(self.port)
        NAE.set_udid(self.udid)
        NAE.set_package_name(self.package_name)
        NAE.set_current_node(child_node)
        return NAE
