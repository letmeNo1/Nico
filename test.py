from auto_nico.android.nico_android import NicoAndroid

nico = NicoAndroid("emulator-5554")
nico(text="Use Wi-Fi").wait_for_appearance()
nico(text="AndroidWifi").wait_for_appearance()
nico(text="Add network").wait_for_appearance()
nico(text="Searching for Wi-Fi networks").wait_for_appearance()
nico(text="Wi-Fi preferences").wait_for_appearance()
nico(text="Saved networks").wait_for_appearance()
