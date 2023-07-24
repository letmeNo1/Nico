import os

from adb_uiautomator.nico import AdbAutoNico

nico = AdbAutoNico("514f465834593398")
nico.start_app("com.android.settings/.Settings")
Link = nico(text ="连接").wait_for_appearance()
Link.click()
WLAN = nico(text = "WLAN").wait_for_appearance()
WLAN.click()
nico.back()
bluetooth = nico(text="蓝牙").wait_for_appearance()
bluetooth.click()
nico.back()


os.system("adb shell am instrument -w -r -e class com.example.myapplication.HierarchyTest com.example.myapplication.test/androidx.test.runner.AndroidJUnitRunner")
