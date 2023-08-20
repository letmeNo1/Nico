from nico.nico import AdbAutoNico

poco = AdbAutoNico("22367209daba64b1")
print(poco(text="Refresh").parent().get_clickable())