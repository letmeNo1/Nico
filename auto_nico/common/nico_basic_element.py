import json

from auto_nico.common.error import UIStructureError
from auto_nico.common.runtime_cache import RunningCache
from lxml.etree import _Element

from auto_nico.common.nico_basic import NicoBasic
from loguru import logger


class NicoBasicElement(NicoBasic):
    def __init__(self, **query):
        self.udid = None
        self.port = None
        self.package_name = None
        self.current_node = None
        self.query = query
        super().__init__(self.udid, **query)

    def refresh_ui_tree(self):
        RunningCache(self.udid).clear_current_cache_ui_tree()

    def set_udid(self, udid):
        self.udid = udid

    def set_port(self, port):
        self.port = port

    def set_query(self, query):
        self.query = query

    def set_package_name(self, package_name):
        RunningCache(self.udid).set_current_running_package_name(package_name)
        self.package_name = package_name

    def set_current_node(self, current_node):
        self.current_node = current_node

    def _get_attribute_value(self, attribute_name) -> str:
        if self.current_node is None:
            self.current_node = self._find_function(self.query)
        if self.current_node is None:
            raise UIStructureError(
                f"Can't found element with query: {self.query}")
        elif type(self.current_node) is list:
            raise UIStructureError(
                "More than one element has been retrieved, use the 'get' method to specify the number you want")
        RunningCache(self.udid).set_action_was_taken(False)
        if self.current_node.get(attribute_name) is None:
            logger.debug(f"Can't found attribute: {attribute_name}")
        return self.current_node.get(attribute_name)

    def _get(self, index):
        node = self._find_all_function(self.query)[index]
        RunningCache(self.udid).set_action_was_taken(False)
        if node is None:
            raise Exception("No element found")
        return node

    def _all(self):
        eles = self._find_all_function(self.query)
        RunningCache(self.udid).set_action_was_taken(False)
        return eles

    def _last_sibling(self, index=0) -> _Element:
        if self.current_node is None:
            self.current_node = self._find_function(query=self.query, use_xml=True)
        if self.current_node is None:
            raise UIStructureError(f"Can't found element")
        previous_node = self.current_node.getprevious()
        if index >= 1:
            for i in range(index):
                previous_node = previous_node.getprevious()

        return previous_node

    def _next_sibling(self, index=0) -> _Element:
        if self.current_node is None:
            self.current_node = self._find_function(query=self.query, use_xml=True)
        if self.current_node is None:
            raise UIStructureError(f"Can't found element")
        next_node = self.current_node.getnext()
        if index >= 1:
            for i in range(index):
                next_node = next_node.getnext()

        return next_node

    # def _description(self,img, bounds):
    #     from cathin.common.utils import _crop_and_encode_image
    #     from cathin.common.request_api import _call_generate_image_caption_api
    #     cropped_image = _crop_and_encode_image(img, [bounds])
    #     text = _call_generate_image_caption_api(cropped_image[0]).get("descriptions")
    #     logger.debug("Description generated successfully")
    #     return text
    #
    # def _ocr_text(self,img, bounds):
    #     from cathin.common.utils import _crop_and_encode_image
    #     from cathin.common.request_api import _call_ocr_api
    #     cropped_image = _crop_and_encode_image(img, [bounds])
    #     text = _call_ocr_api(cropped_image[0])
    #     logger.debug("Description generated successfully")
    #     return text
    #
    # def _ocr_id(self,img, bounds):
    #     from cathin.common.utils import _crop_and_encode_image
    #     from cathin.common.request_api import _call_classify_image_api
    #     cropped_image = _crop_and_encode_image(img, [bounds])
    #     text = _call_classify_image_api(cropped_image[0]).get("top_predictions")[0][0]
    #     logger.debug("Description generated successfully")
    #     return text

    def _parent(self) -> _Element:
        if self.current_node is None:
            self.current_node = self._find_function(query=self.query, use_xml=True)
        if self.current_node is None:
            raise UIStructureError(f"Can't found element")
        parent_node = self.current_node.getparent()
        return parent_node

    def _child(self, index) -> _Element:
        if self.current_node is None:
            self.current_node = self._find_function(query=self.query, use_xml=True)
        if self.current_node is None:
            raise UIStructureError(f"Can't found element")
        child_node = self.current_node.getchildren()[index]
        return child_node

    def _child_amount(self) -> int:
        if self.current_node is None:
            self.current_node = self._find_function(query=self.query, use_xml=True)
        if self.current_node is None:
            raise UIStructureError(f"Can't found element")

        return self.current_node.getchildren().__len__()