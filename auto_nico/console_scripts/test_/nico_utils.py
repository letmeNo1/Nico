import os

from auto_nico.android.tools.format_converter import add_xpath_att
from auto_nico.common.send_request import send_http_request
from auto_nico.ios.idb_utils import IdbUtils
from auto_nico.ios.tools.format_converter import converter
import lxml.etree as ET


def dump_ui_tree():
    platform = os.environ.get('nico_ui_platform')
    udid = os.environ.get("nico_ui_udid")
    idb_utils = IdbUtils(udid)

    port = int(os.environ.get('RemoteServerPort'))
    if platform == "android":
        xml = send_http_request(port, "dump",{"compressed":"true"}).replace("class", "class_name").replace("resource-id=",
                                                                                              "id=").replace(
            "content-desc=", "content_desc=")
        root = add_xpath_att(ET.fromstring(xml.encode('utf-8')))

    else:
        package_name = idb_utils.get_current_bundleIdentifier(port)
        os.environ['current_package_name'] = package_name
        xml = send_http_request(port, f"dump_tree", {"bundle_id": package_name})
        xml = converter(xml)
        root = ET.fromstring(xml.encode('utf-8'))
    return root