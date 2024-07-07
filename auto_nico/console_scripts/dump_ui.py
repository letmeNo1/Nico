from auto_nico.android.nico_android import NicoAndroid


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='device_udid')
    parser.add_argument('-c', type=str, help='compressed', default="true")

    args = parser.parse_args()
    nico = NicoAndroid(args.s)
    nico().get_root_xml(True)