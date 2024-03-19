from auto_nico.adb_utils import AdbUtils

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='device_udid')
    if parser.parse_args().u is None:
        print("Please provide a device_udid")
        return
    args = parser.parse_args()
    adb_utils = AdbUtils(args.s)
    adb_utils.qucik_shell("pm uninstall hank.dump_hierarchy")
    adb_utils.qucik_shell("pm uninstall hank.dump_hierarchy.test")