from adb_uiautomator.nico import AdbAutoNico


aa = AdbAutoNico("290aa9aac2a29a1e")
# aa(text ="Next").wait_for_appearance()
print(aa(text ="License Agreement").wait_for_appearance())