import socket
import time

def send_tcp_request(host, port, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.sendall(message.encode())
        client_socket.sendall('\n'.encode())


        # 接收服务器响应
        response = client_socket.recv(1024)  # 一次最多接收 1024 字节数据
        print("Received response:", response.decode())
        client_socket.close()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    host = "localhost"  # 服务器主机名或 IP 地址
    port = 9755
  # 服务器端口
    send_tcp_request(host, port, "dump")


