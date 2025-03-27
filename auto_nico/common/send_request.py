import socket
import requests
from loguru import logger


def send_tcp_request(port: int, message: str):
    # logger.debug(f"send_tcp_request: {port} {message}")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())

        # Receive server response
        chunks = []
        while True:
            chunk = client_socket.recv(1024)  # Receive up to 1024 bytes at a time
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


import pycurl
from io import BytesIO
from loguru import logger


def send_http_request(port: int, method, params: dict = None, timeout=10):
    url = f"http://localhost:{port}/{method}"
    logger.debug(f"request:{url}")

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.TIMEOUT, timeout)
    if params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        c.setopt(c.URL, f"{url}?{param_str}")

    try:
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        response_code = c.getinfo(pycurl.HTTP_CODE)
        if response_code == 200:
            content_type = c.getinfo(pycurl.CONTENT_TYPE)
            buffer.seek(0)
            response_content = buffer.read()
            if 'image/jpeg' in content_type or 'image/png' in content_type:
                logger.debug(f"Request successful, response content: Image content:{response_content[:100]}")
                return response_content
            else:
                response_text = response_content.decode('utf-8')
                logger.debug(f"response:{response_text[:100]}")
                return response_text
        else:
            logger.error(f"Request failed, status code: {response_code}")
    except pycurl.error as e:
        logger.error(f"An error occurred during the request: {e}")
    finally:
        c.close()
        buffer.close()