import os
import time

from nico.get_uiautomator_xml import get_snapshot_m5d, get_root_node
from nico.nico import AdbAutoNico
from nico.utils import Utils
start_time = time.time()

nico = AdbAutoNico("22367209daba64b1")
nico(text ="Next").wait_for_appearance()
nico(text ="Finnish").wait_for_appearance()
nico(text ="dansk").wait_for_appearance()
nico(text ="Dutch").wait_for_appearance()
nico(text ="suomi").wait_for_appearance()
nico(text ="Czech").wait_for_appearance()

# get_root_node("22367209daba64b1")
# import time
#

end_time = time.time()

#
print("代码执行时间：", end_time - start_time, "秒")