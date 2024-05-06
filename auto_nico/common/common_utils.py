import json
import socket


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def is_valid_json(s):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None
