import os
import time

from nico.nico import AdbAutoNico


# nico(text ="Add another email account").wait_for_appearance()
# nico(text ="Set up your personal or work email").wait_for_appearance()
# nico(text ="Network & internet").wait_for_appearance()
# nico(text ="Bluetooth").wait_for_appearance()
# nico(text ="Connected devices").wait_for_appearance()
# nico(text ="Display").wait_for_appearance()
# nico(text ="Sound").wait_for_appearance()
# nico(text ="Sound").click()
# nico(text="Do Not Disturb").click()
#
start_time = time.time()

#
# commands = f"""adb -s 22367209daba64b1 shell am instrument -w -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
# # 替换为你要执行的外部命令
#
# nico = AdbAutoNico("emulator-5554")
# # time.sleep(100)
# nico(text ="Display").wait_for_appearance()
#
# nico(text ="Display").click()
#
#
nico = AdbAutoNico("emulator-5554")
# #
# nico(text ="Display").wait_for_appearance()
# nico(text ="Display").wait_for_appearance()
# nico(text ="Display").wait_for_appearance()

#

nico().wait_for_any([nico(text="122"),nico(text="Display")])

nico2 = AdbAutoNico("514f465834593398")
nico2(text="连接").wait_for_appearance()#

# nico3 = AdbAutoNico("emulator-5554")
# nico3(text="Display").wait_for_appearance()

nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()


nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()

nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()

nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()

nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()

nico4 = AdbAutoNico("emulator-5554")
nico4(text="Display").wait_for_appearance()

# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()
# nico(text ="声音和振动").wait_for_appearance()

#
#
# # dump_ui_xml("emulator-5554")
# # import time
#

