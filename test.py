import os

from nico.nico import AdbAutoNico
from nico.utils import Utils

nico = AdbAutoNico("514f465834593398")
utils = Utils("514f465834593398")
utils.start_app("com.android.settings/.Settings")
Link = nico(text ="连接").wait_for_appearance()
Link.click()
WLAN = nico(text = "WLAN").wait_for_appearance()
WLAN.click()
utils.back()
bluetooth = nico(text="蓝牙").wait_for_appearance()
bluetooth.click()
utils.back()


os.system("adb shell am instrument -w -r -e class com.example.myapplication.HierarchyTest com.example.myapplication.test/androidx.test.runner.AndroidJUnitRunner")
