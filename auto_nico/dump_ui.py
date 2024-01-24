from auto_nico.nico import AdbAutoNico


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('udid', type=str, help='device_udid')

    args = parser.parse_args()
    nico = AdbAutoNico(args.udid)
    nico.get_root_xml()