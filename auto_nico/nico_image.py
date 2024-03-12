import os
import tempfile
import time
from auto_nico.logger_config import logger
from auto_nico.nico import AdbAutoNico
from skimage.metrics import structural_similarity as ssim
import cv2


class NicoImage:
    def __init__(self, udid):
        self.udid = udid
        self.source_image_path = tempfile.gettempdir() + "/test.png"

    def pull_screenshot(self):
        os.popen(f"adb -s {self.udid} shell screencap /sdcard/screenshot.png").read()

        os.popen(f"adb -s {self.udid} pull /sdcard/screenshot.png {self.source_image_path}").read()

    def __calculate_image_similarity(self, image_path, mosaic):
        self.pull_screenshot()
        nico = AdbAutoNico(self.udid)
        img1 = cv2.imread(self.source_image_path)
        img2 = cv2.imread(image_path)
        if mosaic:
            eles = nico(text_matches=r'^(?=(?:.*?\d){2})').all()
            for ele in eles:
                x, y, w, h = ele.get_bounds
                if h < 10:
                    h = 50
                cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 0), -1)
            if not os.path.exists(self.source_image_path) or not os.path.exists(image_path):
                raise FileExistsError(f"can't open/read file {self.source_image_path}, please check")

        # 将图片转换为灰度
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # 计算SSIM
        similarity = ssim(img1_gray, img2_gray)

        print(str(similarity))
        return similarity

    def __wait_page(self, image_path, expected_similarity, timeout, wait_disappear, mosaic):
        time_started_sec = time.time()
        while time.time() < time_started_sec + timeout:
            rst = self.__calculate_image_similarity(image_path, mosaic)
            if wait_disappear:
                if rst < expected_similarity:
                    logger.debug(f"similarity is {rst}")

                    return True
                else:
                    continue
            else:
                if rst >= expected_similarity:
                    logger.debug(f"similarity is {rst}")

                    return True
                else:
                    continue
        error = f"Can't find element by image in {timeout} s, similarity is {rst}"
        raise TimeoutError(error)

    def wait_page_disappear(self, image_path, expected_similarity, timeout, mosaic=False):
        return self.__wait_page(image_path, expected_similarity, timeout, True, mosaic)

    def wait_page_appear(self, image_path, expected_similarity=0.9, timeout=10, mosaic=False):
        return self.__wait_page(image_path, expected_similarity, timeout, False, mosaic)
