import os
import re
import subprocess

from loguru import logger
from auto_nico.common.nico_basic_element import NicoBasicElement
from auto_nico.common.runtime_cache import RunningCache


class UIStructureError(Exception):
    pass


class NicoAndroidElement(NicoBasicElement):
    def __init__(self, **query):
        self.query = query
        self.current_node = None
        super().__init__(**query)

    def set_seek_bar(self, percentage):
        x = self.get_bounds()[0] + self.get_bounds()[2] * percentage
        y = self.center_coordinate()[1]
        logger.debug(f"set seek bar to {percentage}")
        self.click(x, y)

    @property
    def index(self):
        return self._get_attribute_value("index")

    def get_index(self):
        return self.index

    @property
    def text(self):
        return self._get_attribute_value("text")

    def get_text(self):
        return self.text

    @property
    def id(self):
        return self._get_attribute_value("id")

    def get_id(self):
        return self.id

    @property
    def class_name(self):
        return self._get_attribute_value("class")

    def get_class_name(self):
        return self.class_name

    @property
    def package(self):
        return self._get_attribute_value("package")

    def get_package(self):
        return self.package

    @property
    def content_desc(self):
        return self._get_attribute_value("content_desc")

    def get_content_desc(self):
        return self.content_desc

    @property
    def checkable(self):
        return self._get_attribute_value("checkable")

    def get_checkable(self):
        return self.checkable

    @property
    def checked(self):
        return self._get_attribute_value("checked")

    def get_checked(self):
        return self.checked

    @property
    def clickable(self):
        return self._get_attribute_value("clickable")

    def get_clickable(self):
        return self.clickable

    @property
    def enabled(self):
        return self._get_attribute_value("enabled")

    def get_enabled(self):
        return self.enabled

    @property
    def focusable(self):
        return self._get_attribute_value("focusable")

    def get_focusable(self):
        return self.focusable

    @property
    def focused(self):
        return self._get_attribute_value("focused")

    def get_focused(self):
        return self.focused

    @property
    def scrollable(self):
        return self._get_attribute_value("scrollable")

    def get_scrollable(self):
        return self.scrollable

    @property
    def long_clickable(self):
        return self._get_attribute_value("long-clickable")

    def get_long_clickable(self):
        return self.long_clickable

    @property
    def password(self):
        return self._get_attribute_value("password")

    def get_password(self):
        return self.password

    @property
    def selected(self):
        return self._get_attribute_value("selected")

    def get_selected(self):
        return self.selected

    @property
    def bounds(self):
        pattern = r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
        matches = re.findall(pattern, self._get_attribute_value("bounds"))

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
    def description(self):
        from cathin.common.utils import _crop_and_encode_image
        from cathin.common.request_api import _call_generate_image_caption_api
        import cv2
        import numpy as np
        logger.debug("Description being generated")
        result = subprocess.run(['adb', '-s', self.udid, 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
        screenshot_data = result.stdout
        nparr = np.frombuffer(screenshot_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cropped_image = _crop_and_encode_image(img, [self.bounds])
        text = _call_generate_image_caption_api(cropped_image[0]).get("descriptions")
        logger.debug("Description generated successfully")
        return text

    def get_bounds(self):
        return self.bounds

    def center_coordinate(self):
        x, y, w, h = self.bounds
        center_x = x + w // 2
        center_y = y + h // 2
        return center_x, center_y

    def scroll(self, duration=200, direction='vertical_up'):
        if direction not in ('vertical_up', "vertical_down", 'horizontal_left', "horizontal_right"):
            raise ValueError(
                'Argument `direction` should be one of "vertical_up" or "vertical_down" or "horizontal_left"'
                'or "horizontal_right". Got {}'.format(repr(direction)))
        to_x = 0
        to_y = 0
        from_x = self.center_coordinate()[0]
        from_y = self.center_coordinate()[1]
        if direction == "vertical_up":
            to_x = from_x
            to_y = from_y - from_y / 2
        elif direction == "vertical_down":
            to_x = from_x
            to_y = from_y + from_y / 2
        elif direction == "horizontal_left":
            to_x = from_x - from_x / 2
            to_y = from_y
        elif direction == "horizontal_right":
            to_x = from_x + from_x / 2
            to_y = from_y
        command = f'adb -s {self.udid} shell input swipe {from_x} {from_y} {to_x} {to_y} {duration}'
        RunningCache(self.udid).clear_current_cache_ui_tree()
        os.system(command)

    def swipe(self, to_x, to_y, duration=0):
        from_x = self.center_coordinate()[0]
        from_y = self.center_coordinate()[1]
        duration = duration*1000 + 200
        command = f'adb -s {self.udid} shell input swipe {from_x} {from_y} {to_x} {to_y} {duration}'
        os.environ[f"{self.udid}_ui_tree"] = ""
        os.system(command)

    def drag(self, to_x, to_y, duration=0):
        from_x = self.center_coordinate()[0]
        from_y = self.center_coordinate()[1]
        duration = duration*1000 + 2000
        command = f'adb -s {self.udid} shell input swipe {from_x} {from_y} {to_x} {to_y} {duration}'
        os.environ[f"{self.udid}_ui_tree"] = ""
        os.system(command)

    def click(self, x=None, y=None, x_offset=None, y_offset=None):
        if x is None and y is None:
            x = self.center_coordinate()[0]
            y = self.center_coordinate()[1]
        if x_offset is not None:
            x = x + x_offset
        if y_offset is not None:
            y = y + y_offset
        command = f'adb -s {self.udid} shell input tap {x} {y}'
        os.system(command)
        RunningCache(self.udid).clear_current_cache_ui_tree()
        logger.debug(f"click {x} {y}")

    def long_click(self, duration, x_offset=None, y_offset=None):
        x = self.center_coordinate()[0]
        y = self.center_coordinate()[1]
        if x_offset is not None:
            x = x + x_offset
        if y_offset is not None:
            y = y + y_offset
        command = f'adb -s {self.udid} shell input swipe {x} {y} {x} {y} {int(duration*1000)}'
        RunningCache(self.udid).clear_current_cache_ui_tree()
        os.system(command)

    def set_text(self, text, append=False, x_offset=None, y_offset=None):
        len_of_text = len(self.get_text())
        self.click(x_offset=x_offset, y_offset=y_offset)
        os.system(f'adb -s {self.udid} shell input keyevent KEYCODE_MOVE_END')
        del_cmd = f'adb -s {self.udid} shell input keyevent'
        if not append:
            for _ in range(len_of_text + 8):
                del_cmd = del_cmd + " KEYCODE_DEL"
            os.system(del_cmd)
        text = text.replace("&", "\&").replace("\"", "")
        RunningCache(self.udid).clear_current_cache_ui_tree()
        os.system(f'''adb -s {self.udid} shell input text "{text}"''')
        os.system(f'adb -s {self.udid} shell settings put global policy_control immersive.full=*')

    def get(self, index):
        node = self._get(index)
        NAE = NicoAndroidElement()
        NAE.set_current_node(node)
        NAE.set_udid(self.udid)
        return NAE

    def all(self):
        eles = self._all()
        if not eles:
            return eles
        ALL_NAE_LIST = []
        for ele in eles:
            NAE = NicoAndroidElement()
            NAE.set_current_node(ele)
            NAE.set_udid(self.udid)
            ALL_NAE_LIST.append(NAE)
        return ALL_NAE_LIST

    def last_sibling(self, index=0):
        previous_node = self._last_sibling(index)
        NAE = NicoAndroidElement()
        NAE.set_udid(self.udid)
        NAE.set_current_node(previous_node)
        return NAE

    def next_sibling(self, index=0):
        next_node = self._next_sibling(index)
        NAE = NicoAndroidElement()
        NAE.set_udid(self.udid)
        NAE.set_current_node(next_node)
        return NAE

    def parent(self):
        parent_node = self._parent()
        NAE = NicoAndroidElement()
        NAE.set_udid(self.udid)
        NAE.set_current_node(parent_node)
        return NAE

    def child(self, index=0):
        child_node = self._child(index)
        NAE = NicoAndroidElement()
        NAE.set_udid(self.udid)
        NAE.set_current_node(child_node)
        return NAE

    def children_amount(self) -> int:
        child_amount = self._child_amount()
        return child_amount