import socket
import base64
import time
import os

def send_and_receive(client_socket, server_address, message, timeout=1):
    client_socket.sendto(message.encode(), server_address)
    client_socket.settimeout(timeout)
    try:
        response, _ = client_socket.recvfrom(4096)
        return response.decode()
    except socket.timeout:
        return None