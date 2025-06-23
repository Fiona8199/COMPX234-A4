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
        return Nonedef download_file(server_address, filename):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request = f"DOWNLOAD {filename}"
    response = send_and_receive(client_socket, server_address, request)

    if not response:
        print(f"Failed to get response for {filename}")
        return

    if response.startswith(f"ERR {filename} NOT_FOUND"):
        print(f"File {filename} not found on server")
        return

    _, _, size, port = response.split("SIZE")[1].split()
    size, port = int(size), int(port)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(("", 0))

    with open(filename, "wb") as file:
        start, end = 0, 999
        while start < size:
            request = f"FILE {filename} GET START {start} END {end}"
            response = send_and_receive(data_socket, server_address, request)
            if not response:
                print(f"Failed to get data chunk for {filename}")
                return

            if response.startswith(f"FILE {filename} OK"):
                _, _, _, _, data = response.split("DATA")
                decoded_data = base64.b64decode(data)
                file.write(decoded_data)
                start += len(decoded_data)
                end = min(start + 999, size - 1)
                print(f"Received {len(decoded_data)} bytes")

        close_request = f"FILE {filename} CLOSE"
        send_and_receive(data_socket, server_address, close_request)

    data_socket.close()
    client_socket.close()
    print(f"File {filename} downloaded successfully")def main(server_hostname, server_port, files_list):
    server_address = (server_hostname, server_port)
    with open(files_list, "r") as f:
        filenames = [line.strip() for line in f.readlines()]

    for filename in filenames:
        download_file(server_address, filename)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <hostname> <port> <files_list>")
        sys.exit(1)
    server_hostname, server_port, files_list = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    main(server_hostname, server_port, files_list)