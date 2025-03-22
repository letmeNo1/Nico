import os
from pathlib import Path
from datetime import datetime

import cv2

from auto_nico.android.adb_utils import AdbUtils
from auto_nico.android.nico_android import NicoAndroid


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, help='device_udid')

    parser.add_argument('-m', action='store_true',
                        help='Activate special mode.')
    args = parser.parse_args()
    adb_utils = AdbUtils(args.u)
    desktop_path = Path.home() / 'Desktop'
    timestamp = datetime.now().strftime("Screenshot_%Y-%m-%d_%H%M%S")
    pic_path = f"{desktop_path}\{timestamp}.png"

    if args.m:
        nico = NicoAndroid(args.s)
        eles = nico(text_matches=r'^(?=(?:.*?\d){2})').all()
        adb_utils.snapshot(timestamp, desktop_path)
        image = cv2.imread(f"{pic_path}")
        for ele in eles:
            x, y, w, h = ele.get_bounds
            if h < 10:
                h = 50
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
        cv2.imwrite(pic_path, image)
        os.startfile(desktop_path)


    else:
        adb_utils.snapshot(timestamp, desktop_path)
        os.startfile(desktop_path)
