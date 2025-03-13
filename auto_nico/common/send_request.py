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


def send_http_request(port: int, method, params: dict = None):
    try:
        url = f"http://localhost:{port}/{method}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if content_type == 'image/jpeg':
                logger.debug(f"Request successful, response content: Image content:{response.content[:100]}")
                return response.content
            else:
                logger.debug(response.text[:100])
                return response.text
        else:
            print(f"Request failed, status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred during the request: {e}")
