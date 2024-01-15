from nico.nico import AdbAutoNico


class NicoBase:
    def __init__(self, udid):
        self.udid = udid
        self.poco = AdbAutoNico(udid)


class bb(NicoBase):
    def __init__(self, udid):
        super().__init__(udid)

    def test(self):
        self.poco(text="More").get_text()


class ccc(bb):
    def __init__(self, udid):
        super().__init__(udid)

    def test(self):
        self.poco(text="More").get_text()

cc =ccc("22367209daba64b1")
cc.test()

cc =ccc("34ddb49334dd")
cc.test()
