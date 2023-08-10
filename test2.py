import os
import time

from airtest.core.api import connect_device
from airtest.core.helper import G
from base.tools.apollo_poco.drivers.android.uiautomation import AndroidUiautomationPoco

from nico.get_uiautomator_xml import get_snapshot_m5d, get_root_node
from nico.nico import AdbAutoNico
from nico.utils import Utils
start_time = time.time()


connect_device("Android://127.0.0.1:5037/22367209daba64b1")
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
poco(text ="Next").wait_for_appearance()
poco(text ="Finnish").wait_for_appearance()
poco(text ="dansk").wait_for_appearance()
poco(text ="Dutch").wait_for_appearance()
poco(text ="suomi").wait_for_appearance()
poco(text ="Czech").wait_for_appearance()
poco(text ="Finnish").wait_for_appearance()
poco(text ="dansk").wait_for_appearance()
poco(text ="Dutch").wait_for_appearance()
poco(text ="suomi").wait_for_appearance()
poco(text ="Czech").wait_for_appearance()
end_time = time.time()

# # get_root_node("22367209daba64b1")
# import time
#


#
print("代码执行时间：", end_time - start_time, "秒")