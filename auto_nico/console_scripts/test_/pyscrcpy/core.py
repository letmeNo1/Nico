import os
import abc
from pathlib import Path
import socket
import struct
import threading
import time
from time import sleep
from typing import Any, Callable, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
from adbutils import AdbConnection, AdbDevice, AdbError, Network, adb
from av.codec import CodecContext  # type: ignore
from av.error import InvalidDataError  # type: ignore
import cv2 as cv
import cv2
from loguru import logger

from .const import EVENT_DISCONNECT, EVENT_FRAME, EVENT_INIT, LOCK_SCREEN_ORIENTATION_UNLOCKED, EVENT_ONCHANGE
from .control import ControlSender

Frame = npt.NDArray[np.int8]

VERSION = "1.20"
HERE = Path(__file__).resolve().parent
JAR = HERE / f"scrcpy-server.jar"


class Client:
    def __init__(
            self,
            device: Optional[Union[AdbDevice, str]] = None,
            max_size: int = 0,
            bitrate: int = 8000000,
            max_fps: int = 0,
            block_frame: bool = True,
            stay_awake: bool = True,
            lock_screen_orientation: int = LOCK_SCREEN_ORIENTATION_UNLOCKED,
            skip_same_frame=False
    ):
        """
        [ok]Create a scrcpy client. The client won't be started until you call .start()

        Args:
            device: Android device to coennect to. Colud be also specify by
                serial string. If device is None the client try to connect
                to the first available device in adb deamon.
            max_size: Specify the maximum dimension of the video stream. This
                dimensioin refer both to width and hight.0: no limit[已校验, max size of width or height]
            bitrate: bitrate
            max_fps: Maximum FPS (Frame Per Second) of the video stream. If it
                is set to 0 it means that there is not limit to FPS.
                This feature is supported by android 10 or newer.
            [flip]: 没有这个参数, 会自动处理
            block_frame: If set to true, the on_frame callbacks will be only
                apply on not empty frames. Otherwise try to apply on_frame
                callbacks on every frame, but this could raise exceptions in
                callbacks if they are not able to handle None value for frame.
                True:跳过空白帧
            stay_awake: keep Android device awake while the client-server
                connection is alive.
            lock_screen_orientation: lock screen in a particular orientation.
                The available screen orientation are specify in const.py
                in variables LOCK_SCREEN_ORIENTATION*
        """
        # Params挪到后面去
        self.max_size = max_size
        self.bitrate = bitrate
        self.max_fps = max_fps
        self.block_frame = block_frame
        self.stay_awake = stay_awake
        self.lock_screen_orientation = lock_screen_orientation
        self.skip_same_frame = skip_same_frame
        self.min_frame_interval = 1 / max_fps

        if device is None:
            try:
                device = adb.device_list()[0]
            except IndexError:
                raise Exception("Cannot connect to phone")
        elif isinstance(device, str):
            device = adb.device(serial=device)

        self.device = device
        self.listeners = dict(frame=[], init=[], disconnect=[], onchange=[])

        # User accessible
        self.last_frame: Optional[np.ndarray] = None
        self.resolution: Optional[Tuple[int, int]] = None
        self.device_name: Optional[str] = None
        self.control = ControlSender(self)

        # Need to destroy
        self.alive = False
        self.__server_stream: Optional[AdbConnection] = None
        self.__video_socket: Optional[socket.socket] = None
        self.control_socket: Optional[socket.socket] = None
        self.control_socket_lock = threading.Lock()

    def __init_server_connection(self) -> None:
        """
        Connect to android server, there will be two sockets: video and control socket.
         This method will also set resolution property.
        """
        for _ in range(30):  # 超时 写死
            try:
                self.__video_socket = self.device.create_connection(
                    Network.LOCAL_ABSTRACT, "scrcpy"
                )
                break
            except AdbError:
                sleep(0.1)
                pass
        else:
            raise ConnectionError("Failed to connect scrcpy-server after 3 seconds")

        dummy_byte = self.__video_socket.recv(1)
        if not len(dummy_byte):
            raise ConnectionError("Did not receive Dummy Byte!")

        self.control_socket = self.device.create_connection(
            Network.LOCAL_ABSTRACT, "scrcpy"
        )
        self.device_name = self.__video_socket.recv(64).decode("utf-8").rstrip("\x00")
        if not len(self.device_name):
            raise ConnectionError("Did not receive Device Name!")

        res = self.__video_socket.recv(4)
        self.resolution = struct.unpack(">HH", res)
        self.__video_socket.setblocking(False)

    def __deploy_server(self) -> None:
        """
        Deploy server to android device.
        Push the scrcpy-server.jar into the Android device using
        the adb.push(...). Then a basic connection between client and server
        is established.
        """
        cmd = [
            "CLASSPATH=/data/local/tmp/scrcpy-server.jar",
            "app_process",
            "/",
            "com.genymobile.scrcpy.Server",
            VERSION,  # Scrcpy server version
            "info",  # Log level: info, verbose...
            f"{self.max_size}",  # Max screen width (long side)
            f"{self.bitrate}",  # Bitrate of video
            f"{self.max_fps}",  # Max frame per second
            f"{self.lock_screen_orientation}",  # Lock screen orientation
            "true",  # Tunnel forward
            "-",  # Crop screen
            "false",  # Send frame rate to client
            "true",  # Control enabled
            "0",  # Display id
            "false",  # Show touches
            "true" if self.stay_awake else "false",  # Stay awake
            "-",  # Codec (video encoding) options
            "-",  # Encoder name
            "false",  # Power off screen after server closed
        ]
        self.device.push(JAR, "/data/local/tmp/")
        self.__server_stream: AdbConnection = self.device.shell(cmd, stream=True)

    def start(self, threaded: bool = False) -> None:
        """
        Start the client-server connection.
        In order to avoid unpredictable behaviors, this method must be called
        after the on_init and on_frame callback are specify.

        Args:
            threaded : If set to True the stream loop willl run in a separated
                thread. This mean that the code after client.strart() will be
                run. Otherwise the client.start() method starts a endless loop
                and the code after this method will never run. todo new_thread
        """
        assert self.alive is False

        self.__deploy_server()
        self.__init_server_connection()
        self.alive = True
        for func in self.listeners[EVENT_INIT]:
            func(self)

        if threaded:  # 不阻塞当前thread
            threading.Thread(target=self.__stream_loop).start()
        else:
            self.__stream_loop()

    def stop(self) -> None:
        """
        [ok]Close the various socket connection.
        Stop listening (both threaded and blocked)
        """
        self.alive = False
        try:
            self.__server_stream.close()
        except Exception:
            pass
        try:
            self.control_socket.close()
        except Exception:
            pass
        try:
            self.__video_socket.close()
        except Exception:
            pass

    def __del__(self):
        self.stop()

    def __calculate_diff(self, img1, img2):
        if img1 is None:
            return 1
        gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
        gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

        # 计算两张灰度图像的差异
        diff = cv2.absdiff(gray1, gray2)

        # 设置阈值，忽略差异值较小的像素
        threshold = 30
        _, thresholded_diff = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        # 计算差异像素的总数
        total_diff_pixels = np.sum(thresholded_diff / 255)  # 除以255得到二值图像中白色像素的数量

        # 计算图像的总像素数
        total_pixels = gray1.size

        # 计算变化率
        change_rate = total_diff_pixels / total_pixels
        return change_rate

    def __stream_loop(self) -> None:
        """
        Core loop for video parsing.
        While the connection is open (self.alive == True) recive raw h264 video
        stream and decode it into frames. These frame are those passed to
        on_frame callbacks.
        """
        codec = CodecContext.create("h264", "r")
        while self.alive:
            try:
                raw = self.__video_socket.recv(0x10000)
                if raw == b"":
                    raise ConnectionError("Video stream is disconnected")
                for packet in codec.parse(raw):
                    for frame in codec.decode(packet):  # codec.decode(packet)包含多帧
                        frame = frame.to_ndarray(format="bgr24")

                        if len(self.listeners[EVENT_ONCHANGE]) == 0 and not self.skip_same_frame:
                            self.last_frame = frame
                        elif self.__calculate_diff(self.last_frame, frame) > 0.1:
                            logger.debug("different frame detected")
                            self.last_frame = frame
                            for func in self.listeners[EVENT_ONCHANGE]:
                                func(self, frame)
                        else:  # no_change and should skip this frame
                            continue

                        self.resolution = (frame.shape[1], frame.shape[0])
                        for func in self.listeners[EVENT_FRAME]:  # 发送给用户自定义的函数
                            func(self, frame)
            except (BlockingIOError, InvalidDataError):  # empty frame
                time.sleep(0.01)
                if not self.block_frame:  # init时允许空白帧
                    for func in self.listeners[EVENT_FRAME]:
                        func(self, None)
            except (ConnectionError, OSError) as e:  # Socket Closed
                if self.alive:
                    # todo on_disconnect event
                    self.stop()
                    raise e

    def on_init(self, func: Callable[[Any], None]) -> None:
        """
        Add funtion to on_init listeners.
        Your function is run after client.start() is called.

        Args:
            func: callback to be called after the server starts. 参数:这个class的obj
        """
        self.listeners[EVENT_INIT].append(func)

    def on_frame(self, func: Callable[[Any, Frame], None]):
        """
        Add functoin to on-frame listeners.
        Your function will be run on every valid frame recived.

        Args:
            func: callback to be called on every frame.

        Returns:
            The list of on-frame callbacks.
        """
        self.listeners[EVENT_FRAME].append(func)

    def on_change(self, func: Callable[[Any, Frame], None]):
        self.listeners[EVENT_ONCHANGE].append(func)
