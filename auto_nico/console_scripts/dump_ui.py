from auto_nico.nico import AdbAutoNico


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='device_udid')
    parser.add_argument('-c', type=str, help='compressed', default="true")

    args = parser.parse_args()
    nico = AdbAutoNico(args.s)
    nico.get_root_xml(args.c)