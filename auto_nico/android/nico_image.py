import os
import time
from loguru import logger
from airtest.core.api import *
from airtest.core.settings import Settings as ST
import logging

airtest_logger = logging.getLogger("airtest")
airtest_logger.setLevel(logging.INFO)

class NicoImage:
    def __init__(self, udid):
        logger.info(f"Connecting to device with UDID: {udid}")
        connect_device("Android://127.0.0.1:5037/" + udid)

    def __call__(self, v):
        self.v = v
        return self

    def exists(self, timeout=3):
        interval=0.5
        logger.info(f"Checking existence of: {self.v} with timeout: {timeout}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if exists(self.v):
                return True
            time.sleep(interval)
        return False  # Return False if the element does not exist within the timeout period

    def click(self, times=1, **kwargs):
        logger.info(f"Clicking on: {self.v} for {times} times")
        return touch(self.v, times, **kwargs)
        
    def double_click(self):
        logger.info(f"Double clicking on: {self.v}")
        return double_click(self.v)

    def find_all(self):
        logger.info(f"Finding all instances of: {self.v}")
        return find_all(self.v)

    def wait_for_appearance(self, timeout=10, interval=0.5):
        logger.info(f"Waiting for appearance of: {self.v} with timeout: {timeout}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if exists(self.v):
                return True
            time.sleep(interval)
        raise TimeoutError(f"Element {self.v} did not appear within {timeout} seconds")

    def wait_for_disappearance(self, timeout=10, interval=0.5):
        logger.info(f"Waiting for disappearance of: {self.v} with timeout: {timeout}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not exists(self.v):
                return True
            time.sleep(interval)
        raise TimeoutError(f"Element {self.v} did not disappear within {timeout} seconds")

    def wait_for_any(self, v_list, timeout=10, interval=0.5):
        logger.info(f"Waiting for any of: {v_list} with timeout: {timeout}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            for v in v_list:
                if exists(v):
                    return v
            time.sleep(interval)
        raise TimeoutError(f"None of the elements {v_list} appeared within {timeout} seconds")
    
    def swipe(self, v2=None, vector=None, **kwargs):
        logger.info(f"Swiping from {self.v} to {v2} with vector: {vector}")
        return swipe(self.v, v2, vector, **kwargs)

    def set_text(self, enter=True, search=False):
        logger.info(f"Setting text: {self.v} with enter: {enter} and search: {search}")
        return text(self.v, enter, search)

    def keyevent(self):
        logger.info(f"Sending keyevent: {self.v}")
        return keyevent(self.v)

    def snapshot(self, filename=None, msg="", quality=None, max_size=None):
        logger.info(f"Taking snapshot with filename: {filename}, msg: {msg}, quality: {quality}, max_size: {max_size}")
        return snapshot(filename, msg, quality, max_size)

    def sleep(self, secs):
        logger.info(f"Sleeping for {secs} seconds")
        return sleep(secs)