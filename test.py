from adb_uiautomator.nico import AdbAutoNico

nico = AdbAutoNico("514f465834593398",wait_idle=1200)

nico(text ="连接").wait_for_appearance()
nico(text ="连接").click()