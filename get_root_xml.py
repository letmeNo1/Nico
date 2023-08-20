import sys

import psutil
from nico.nico import AdbAutoNico


class GetRootXml:
    def __init__(self,udid):
        self.udid = udid

    def run(self):
        poco = AdbAutoNico(self.udid)
        poco().get_root_xml()


if __name__ == "__main__":
    ins = GetRootXml(sys.argv[1])
    ins.run()

# 获取所有进程列表

