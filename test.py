from adb_uiautomator.nico import AdbAutoNico

nico = AdbAutoNico("514f465834593398")

nico(text ="暂停").wait_for_appearance()
nico(text ="暂停").click()