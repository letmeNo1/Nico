from nico.nico import AdbAutoNico

poco = AdbAutoNico("34ddb49334dd")
poco2 = AdbAutoNico("22367209daba64b1")
poco2(text="Sign in on this device").wait_for_appearance(5)
poco(text="Sign in on this device").wait_for_appearance(5)
poco = AdbAutoNico("34ddb49334dd")
poco2 = AdbAutoNico("22367209daba64b1")
poco2(text="Sign in on this device").wait_for_appearance(5)
poco(text="Sign in on this device").wait_for_appearance(5)