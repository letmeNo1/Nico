from auto_nico.adb_utils import AdbUtils

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', type=str, help='device_udid')

    args = parser.parse_args()
    adb_utils = AdbUtils(args.u)
    adb_utils.qucik_shell("pm uninstall hank.dump_hierarchy")
    adb_utils.qucik_shell("pm uninstall hank.dump_hierarchy.test")