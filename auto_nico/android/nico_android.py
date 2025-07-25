import random
import time
import subprocess

from auto_nico.android.nico_android_element import NicoAndroidElement
from loguru import logger
from auto_nico.common.runtime_cache import RunningCache
from auto_nico.common.send_request import send_http_request
from auto_nico.common.nico_basic import NicoBasic
from auto_nico.android.adb_utils import AdbUtils


class NicoAndroid(NicoBasic):
    """
        Explanation of instantiation and invocation process:
        1. nico = NicoAndroid("3167a8bd3167")  -> Triggers the __init__ method
        - Initializes device-related configurations (UDID binding, ADB connection check, test service installation)
        - Automatically allocates a running port (prioritizes reusing existing ports, generates one by rule if none exists)
        - Starts the test server, verifies its availability, and completes initialization caching

        2. nico(text="Jabra")  -> Triggers the __call__ method
        - Automatically forwards to AndroidDriver if the query contains "ocr"-related parameters
        - Checks device status (e.g., screen wake-up) to ensure the test server is running normally
        - Returns a NicoAndroidElement instance for subsequent UI operations (e.g., click, input, etc.)
    """

    def __init__(self, udid, port="random", **query):
        super().__init__(udid, **query)
        self.udid = udid
        self.adb_utils = AdbUtils(udid)
        self.version = 1.4
        self.adb_utils.install_test_server_package(self.version)
        self.adb_utils.check_adb_server()
        self.__allocate_running_port(port)
        self.runtime_cache = RunningCache(udid)
        self.runtime_cache.set_initialized(True)
        self.__start_test_server()

    def __allocate_running_port(self, port):
        """
        Allocate a running port for the NicoAndroid instance.
        This method checks if a TCP forward port already exists for the device.
        If it does, it uses that port; otherwise, it generates a new random port.
        """
        exists_port = self.adb_utils.get_tcp_forward_port()
        if exists_port is None:
            logger.debug(f"{self.udid} no exists port")
            if port != "random":
                current_port = port
            else:
                random_number = random.randint(9000, 9999)
                current_port = random_number
        else:
            current_port = int(exists_port)
        RunningCache(self.udid).set_current_running_port(current_port)

    def __check_server_ready(self, current_port, max_retries=1):
        """ Check if the Nico Android test server is ready.
        This method attempts to connect to the server and verify its status.

        Args:
            current_port (int): The port on which the server is expected to run.
            max_retries (int): The maximum number of retries to check server readiness.
            Default is 1.
        Returns:
            bool: True if the server is ready, False otherwise.
        """
        for _ in range(max_retries):
            # Check server is running
            response = send_http_request(RunningCache(self.udid).get_current_running_port(), "status")
            rst1 = response is not None and "server is running" in response
            # Check UI tree response is running
            response = send_http_request(RunningCache(self.udid).get_current_running_port(), "get_root")
            rst2 = response is not None and "[android.view.accessibility.AccessibilityNodeInfo" in response
            if rst1 and rst2:
                logger.debug(f"{self.udid}'s test server is ready on {current_port}")
                return True
            else:
                logger.debug(f"server is no ready on {current_port}")
                time.sleep(1)
                continue
        return False

    def __start_test_server(self):
        """
        Start Server for Nico Android.
        1. Cache Management:
        - Use RunningCache to persist and retrieve the current running port associated with the device's udid.
        - Store initialization status to avoid redundant setup operations.

        2. Current Port Handling:
        - Check for existing TCP forward ports via ADB to reuse if available (reduces port conflicts).
        - If an existing port is found, use it directly as the current running port.

        3. New Port Allocation:
        - When no existing port exists, use the user-specified port if provided (non-"random" value).
        - If "random" is specified, generate a random port in the range 9000-9999.
        - In case of server startup failure on the current port, clean up the failed port and retry with a new random port.
        """

        # Helper function to generate ADB command with specified port
        def get_adb_command(udid, port):
            return (
                f"adb -s {udid} shell am instrument -r -w "
                f"-e port {port} "
                f"-e class nico.dump_hierarchy.HierarchyTest "
                "nico.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"
            )

        # Helper function to handle server startup attempts with retries
        def attempt_start_server(target_port):
            """
            Attempts to start the server on specified port with retries.
            Returns True if server starts successfully, False otherwise.
            """
            # Maximum number of retries
            max_retries = 3
            for attempt in range(max_retries):
                # Check packages exist and if not reinstall, skip
                self.adb_utils.install_test_server_package(self.version)

                # Start the process and wait briefly for initialization
                command = get_adb_command(self.udid, target_port)
                logger.debug(f"Executing start command: {command}")
                subprocess.Popen(command, shell=True)
                time.sleep(3)  # Allow time for process to start

                # Set the TCP forward port between PC and Android device
                self.adb_utils.set_tcp_forward_port(target_port)

                # Check if server is ready
                if self.__check_server_ready(target_port, max_retries=3):
                    # Initialize ADB and close keyboard
                    self.close_keyboard()
                    logger.info(f"{self.udid}'s uiautomator initialized successfully")
                    return True

                logger.debug(f"Attempt {attempt + 1}/{max_retries} failed, waiting 3s before retry")
                time.sleep(3)

            return False

        # Check if the server is already running
        if self.__check_server_ready(RunningCache(self.udid).get_current_running_port()):
            logger.debug(f"{self.udid}'s test server is already running")
            return

        # First phase: Try starting with current port
        current_port = RunningCache(self.udid).get_current_running_port()
        if attempt_start_server(current_port):
            return

        # If first phase fails, clean up and try random port
        logger.warning(f"Failed to start on current port {current_port}, attempting random port")
        self.adb_utils.clear_tcp_forward_port(current_port)

        # Get new random port and try again
        random_port = random.randint(9000, 9999)
        if attempt_start_server(random_port):
            return

        # All attempts exhausted
        logger.error(f"{self.udid}'s uiautomator initialization failed - all retries exhausted")
        raise RuntimeError(f"Failed to initialize {self.udid}'s uiautomator after multiple attempts")

    def close_keyboard(self):
        adb_utils = AdbUtils(self.udid)
        ime_list = adb_utils.qucik_shell("ime list -s").split("\n")[0:-1]
        for ime in ime_list:
            adb_utils.qucik_shell(f"ime disable {ime}")

    def __call__(self, **query):
        # Initialize ADB and start the test server
        self.adb_utils.check_adb_server()
        if self.adb_utils.is_screen_off():
            self.adb_utils.wake_up()

        self.__start_test_server()

        # Create and return a NicoAndroidElement instance with the current udid and port
        NAE = NicoAndroidElement(**query)
        NAE.set_udid(self.udid)
        NAE.set_port(RunningCache(self.udid).get_current_running_port())
        return NAE

# nico1 = NicoAndroid("121471aac2a29a1e")
# nico1(text="Sign In").click()
# # nico = NicoAndroid("3167a8bd3167")
# # nico(text="Sign In").click()
