import socket
import threading
import random
import os
import base64
import time

def handle_client_request(client_address, filename, client_socket):
    try:
        if not os.path.exists(filename):
            response = f"ERR {filename} NOT_FOUND"
            client_socket.sendto(response.encode(), client_address)
            return

        file_size = os.path.getsize(filename)
        server_port = random.randint(50000, 51000)
        response = f"OK {filename} SIZE {file_size} PORT {server_port}"
        client_socket.sendto(response.encode(), client_address)

        # Create a new socket for data transfer
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.bind(("localhost", server_port))

        with open(filename, "rb") as file:
            while True:
                request, _ = data_socket.recvfrom(1024)
                request = request.decode()
                if request.startswith(f"FILE {filename} CLOSE"):
                    data_socket.sendto(f"FILE {filename} CLOSE_OK".encode(), client_address)
                    break

                if request.startswith(f"FILE {filename} GET"):
                    _, _, start, end = request.split()
                    start, end = int(start), int(end)
                    file.seek(start)
                    data = file.read(end - start + 1)
                    encoded_data = base64.b64encode(data).decode()
                    response = f"FILE {filename} OK START {start} END {end} DATA {encoded_data}"
                    data_socket.sendto(response.encode(), client_address)

        data_socket.close()
    except Exception as e:
        print(f"Error handling client request: {e}")

def main(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("localhost", port))
    print(f"Server running on port {port}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        message = message.decode()
        if message.startswith("DOWNLOAD"):
            _, filename = message.split()
            client_thread = threading.Thread(target=handle_client_request, args=(client_address, filename, server_socket))
            client_thread.start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    main(port)