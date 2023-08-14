import socket
import subprocess
import time
from nico.logger_config import logger


def __send_request(port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())

        # 接收服务器响应
        response = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
        client_socket.close()
        return response.decode()
    except ConnectionRefusedError:
        return ""
    except ConnectionResetError:
        return ""


def __send_request_until_success(port, message):
    while 100:
        response = __send_request(port, message)
        if response != "":
            break


def send_tcp_request(udid, port, message):
    response = __send_request(port, message)
    if response != "":
        logger.debug(f"Server is ready")
        return response
    else:
        commands = f"""adb -s {udid} shell am instrument -r -w -e port {port} -e class hank.dump_hierarchy.HierarchyTest hank.dump_hierarchy.test/androidx.test.runner.AndroidJUnitRunner"""
        subprocess.Popen(commands, shell=True)
        time.sleep(1)
        __send_request_until_success(port, message)
        logger.debug(f"Server is ready")
