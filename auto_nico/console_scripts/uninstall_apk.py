from auto_nico.android.adb_utils import AdbUtils


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='device_udid')

    args = parser.parse_args()
    adb_utils = AdbUtils(args.s)
    adb_utils.qucik_shell("pm uninstall nico.dump-hierarchy")
    adb_utils.qucik_shell("pm uninstall nico.dump-hierarchy.test")