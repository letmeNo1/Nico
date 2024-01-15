import socket

from nico.logger_config import logger


def send_tcp_request(port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())

        # 接收服务器响应
        response = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
        client_socket.close()
        return response.decode()

    except ConnectionRefusedError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"
    except ConnectionResetError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"
