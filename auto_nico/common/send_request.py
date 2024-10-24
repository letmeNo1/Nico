import socket
from loguru import logger


def send_tcp_request(port: int, message: str):
    # logger.debug(f"send_tcp_request: {port} {message}")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())

        # 接收服务器响应
        chunks = []
        while True:
            chunk = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
            if not chunk:
                break
            chunks.append(chunk)
        client_socket.close()
        response = b''.join(chunks)
        if "get_jpg_pic" in message or message == "stop_recording" or "get_png_pic" in message:
            return response
        else:
            response = response.decode()
            return response

    except ConnectionRefusedError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"
    except ConnectionResetError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"
    except ConnectionAbortedError as b:
        logger.error(f"{str(b)} by {port}")
        return f"{str(b)} by {port}"

# send_tcp_request(9580,"print")