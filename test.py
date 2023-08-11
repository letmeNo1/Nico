import os
import time

from nico.get_uiautomator_xml import pull_ui_xml_to_temp_dir, dump_ui_xml
from nico.nico import AdbAutoNico
from nico.utils import Utils

# nico = AdbAutoNico("emulator-5554")
# nico(text ="Search settings").wait_for_appearance()
# # nico(text ="Add another email account").wait_for_appearance()
# # nico(text ="Set up your personal or work email").wait_for_appearance()
# # nico(text ="Network & internet").wait_for_appearance()
# # nico(text ="Bluetooth").wait_for_appearance()
# # nico(text ="Connected devices").wait_for_appearance()
# # nico(text ="Display").wait_for_appearance()
# # nico(text ="Sound").wait_for_appearance()
# nico(text ="Sound").click()
# nico(text="Do Not Disturb").click()


start_time = time.time()  # 记录开始时间

commands = f"""adb -s 22367209daba64b1 shell am instrument -w -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
# 替换为你要执行的外部命令
a = os.popen(commands).read()  # 执行外部命令
print(a)
end_time = time.time()  # 记录结束时间
execution_time = end_time - start_time  # 计算执行时间

print(f"Command execution time: {execution_time:.4f} seconds")

# dump_ui_xml("emulator-5554")
# import time
#

