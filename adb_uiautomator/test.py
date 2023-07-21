
from adb_uiautomator.nico import AdbAutoNico

nico = AdbAutoNico("290aa9aac2a29a1e")
nico(text ="Next").wait_for_appearance()
nico(text ="Next").click()

